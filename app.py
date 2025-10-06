"""
Creative Automation Pipeline - Main Flask Application
"""
import os
import json
import time
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from models import CampaignBrief
from gemini_service import GeminiService
import mimetypes
import queue
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'InputAssets'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Gemini service
gemini_service = GeminiService()

# Global message queue for SSE
log_queues = {}
queue_lock = threading.Lock()


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/load_briefs', methods=['GET'])
def load_briefs():
    """Load the default campaign briefs"""
    try:
        with open('inputs/campaign_briefs.json', 'r') as f:
            briefs = json.load(f)
        return jsonify({"success": True, "briefs": briefs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/load_file', methods=['POST'])
def load_file():
    """Load a custom campaign briefs file"""
    try:
        print("[load_file] Received request")
        if 'file' not in request.files:
            print("[load_file] Error: No file in request")
            return jsonify({"success": False, "error": "No file provided"})
        
        file = request.files['file']
        print(f"[load_file] File received: {file.filename}")
        if file.filename == '':
            print("[load_file] Error: Empty filename")
            return jsonify({"success": False, "error": "No file selected"})
        
        # Read the file content
        file_content = file.read()
        print(f"[load_file] File content length: {len(file_content)} bytes")
        
        # Parse JSON
        briefs = json.loads(file_content)
        print(f"[load_file] Successfully parsed JSON: {len(briefs) if isinstance(briefs, list) else 'object'}")
        return jsonify({"success": True, "briefs": briefs})
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {str(e)}"
        print(f"[load_file] JSON decode error: {error_msg}")
        return jsonify({"success": False, "error": error_msg})
    except Exception as e:
        error_msg = str(e)
        print(f"[load_file] Error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": error_msg})


@app.route('/api/input_assets', methods=['GET'])
def get_input_assets():
    """Get list of input assets"""
    try:
        assets = []
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    assets.append(filename)
        return jsonify({"success": True, "assets": assets})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/output_images', methods=['GET'])
def get_output_images():
    """Get list of generated output images"""
    try:
        output_structure = {}
        if os.path.exists(app.config['OUTPUT_FOLDER']):
            for product in os.listdir(app.config['OUTPUT_FOLDER']):
                product_path = os.path.join(app.config['OUTPUT_FOLDER'], product)
                if os.path.isdir(product_path):
                    output_structure[product] = {}
                    for ratio_folder in os.listdir(product_path):
                        ratio_path = os.path.join(product_path, ratio_folder)
                        if os.path.isdir(ratio_path):
                            images = []
                            for img in os.listdir(ratio_path):
                                if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                                    images.append(f"{product}/{ratio_folder}/{img}")
                            output_structure[product][ratio_folder] = images
        return jsonify({"success": True, "images": output_structure})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/InputAssets/<path:filename>')
def serve_input_asset(filename):
    """Serve input asset files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/output/<path:filename>')
def serve_output_file(filename):
    """Serve output files"""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


def broadcast_log(session_id, message, log_type='info'):
    """Broadcast a log message to all connected clients for this session"""
    with queue_lock:
        if session_id in log_queues:
            log_queues[session_id].put({
                'type': log_type,
                'message': message,
                'timestamp': time.time()
            })
    print(f"[{log_type.upper()}] {message}")


@app.route('/api/stream/<session_id>')
def stream_logs(session_id):
    """SSE endpoint for streaming logs"""
    with queue_lock:
        log_queues[session_id] = queue.Queue()
    
    def event_stream():
        q = log_queues[session_id]
        try:
            while True:
                try:
                    # Wait for messages with timeout
                    msg = q.get(timeout=30)
                    yield f"data: {json.dumps(msg)}\n\n"
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
        except GeneratorExit:
            # Clean up when client disconnects
            with queue_lock:
                if session_id in log_queues:
                    del log_queues[session_id]
    
    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/generate', methods=['POST'])
def generate_campaigns():
    """Generate campaign images for all briefs"""
    try:
        data = request.json
        briefs = data.get('briefs', [])
        selected_assets = data.get('selected_assets', [])
        session_id = data.get('session_id', 'default')
        
        # Run generation in a background thread
        def run_generation():
            try:
                broadcast_log(session_id, "🚀 Starting campaign generation process...", 'info')
                
                # Clear old output images first
                import shutil
                if os.path.exists(app.config['OUTPUT_FOLDER']):
                    broadcast_log(session_id, "🗑️  Clearing old campaign images...", 'info')
                    shutil.rmtree(app.config['OUTPUT_FOLDER'])
                    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
                    broadcast_log(session_id, "✅ Output folder cleared", 'success')
                    # Signal frontend to clear gallery
                    broadcast_log(session_id, "", 'gallery_cleared')
                
                broadcast_log(session_id, f"📝 Processing {len(briefs)} campaign brief(s)", 'info')
                
                # Convert to full paths
                input_images = [os.path.join(app.config['UPLOAD_FOLDER'], asset) for asset in selected_assets]
                broadcast_log(session_id, f"📁 Using {len(input_images)} input asset(s)", 'info')
                
                results = []
                
                for idx, brief_data in enumerate(briefs, 1):
                    brief = CampaignBrief.from_dict(brief_data)
                    product_folder = brief.product_name.replace(' ', '_')
                    
                    broadcast_log(session_id, f"\n{'='*60}", 'info')
                    broadcast_log(session_id, f"🎨 [{idx}/{len(briefs)}] Processing: {brief.product_name}", 'info')
                    broadcast_log(session_id, f"{'='*60}", 'info')
                    
                    # Generate 1:1 ratio first
                    broadcast_log(session_id, f"⏳ Generating 1:1 aspect ratio for {brief.product_name}...", 'info')
                    image_data_1_1, chat_history = gemini_service.generate_campaign_image(
                        brief, input_images, aspect_ratio="1:1"
                    )
                    
                    if image_data_1_1:
                        output_path_1_1 = os.path.join(
                            app.config['OUTPUT_FOLDER'], 
                            product_folder, 
                            "1_1",
                            "campaign_1_1.png"
                        )
                        saved_path_1_1 = gemini_service.save_binary_file(output_path_1_1, image_data_1_1)
                        broadcast_log(session_id, f"✅ Saved 1:1 image to: {output_path_1_1}", 'success')
                        # Broadcast image completion to update gallery
                        broadcast_log(session_id, f"{product_folder}/1_1/campaign_1_1.png", 'image_complete')
                        
                        # Generate 9:16 ratio from chat history
                        broadcast_log(session_id, f"⏳ Generating 9:16 aspect ratio for {brief.product_name}...", 'info')
                        image_data_9_16, chat_history = gemini_service.generate_campaign_image(
                            brief, None, aspect_ratio="9:16", chat_history=chat_history
                        )
                        
                        if image_data_9_16:
                            output_path_9_16 = os.path.join(
                                app.config['OUTPUT_FOLDER'], 
                                product_folder, 
                                "9_16",
                                "campaign_9_16.png"
                            )
                            saved_path_9_16 = gemini_service.save_binary_file(output_path_9_16, image_data_9_16)
                            broadcast_log(session_id, f"✅ Saved 9:16 image to: {output_path_9_16}", 'success')
                            # Broadcast image completion to update gallery
                            broadcast_log(session_id, f"{product_folder}/9_16/campaign_9_16.png", 'image_complete')
                        
                        # Generate 16:9 ratio from chat history
                        broadcast_log(session_id, f"⏳ Generating 16:9 aspect ratio for {brief.product_name}...", 'info')
                        image_data_16_9, chat_history = gemini_service.generate_campaign_image(
                            brief, None, aspect_ratio="16:9", chat_history=chat_history
                        )
                        
                        if image_data_16_9:
                            output_path_16_9 = os.path.join(
                                app.config['OUTPUT_FOLDER'], 
                                product_folder, 
                                "16_9",
                                "campaign_16_9.png"
                            )
                            saved_path_16_9 = gemini_service.save_binary_file(output_path_16_9, image_data_16_9)
                            broadcast_log(session_id, f"✅ Saved 16:9 image to: {output_path_16_9}", 'success')
                            # Broadcast image completion to update gallery
                            broadcast_log(session_id, f"{product_folder}/16_9/campaign_16_9.png", 'image_complete')
                        
                        broadcast_log(session_id, f"✨ Completed all aspect ratios for {brief.product_name}", 'success')
                        
                        results.append({
                            "product": brief.product_name,
                            "success": True,
                            "paths": {
                                "1_1": output_path_1_1,
                                "9_16": output_path_9_16 if image_data_9_16 else None,
                                "16_9": output_path_16_9 if image_data_16_9 else None
                            }
                        })
                    else:
                        broadcast_log(session_id, f"❌ Failed to generate image for {brief.product_name}", 'error')
                        results.append({
                            "product": brief.product_name,
                            "success": False,
                            "error": "Failed to generate image"
                        })
                
                broadcast_log(session_id, f"\n{'='*60}", 'info')
                broadcast_log(session_id, f"🎉 Campaign generation completed!", 'success')
                broadcast_log(session_id, f"📊 Generated {len([r for r in results if r['success']])} out of {len(results)} campaign(s)", 'info')
                broadcast_log(session_id, f"{'='*60}\n", 'info')
                broadcast_log(session_id, "COMPLETE", 'complete')
                
            except Exception as e:
                import traceback
                error_msg = str(e)
                broadcast_log(session_id, f"❌ Error during generation: {error_msg}", 'error')
                broadcast_log(session_id, traceback.format_exc(), 'error')
                broadcast_log(session_id, "COMPLETE", 'complete')
        
        # Start generation in background thread
        thread = threading.Thread(target=run_generation)
        thread.daemon = True
        thread.start()
        
        return jsonify({"success": True, "session_id": session_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/compliance_check', methods=['POST'])
def compliance_check():
    """Run compliance checks on all generated images"""
    try:
        data = request.json
        selected_assets = data.get('selected_assets', [])
        session_id = data.get('session_id', 'default')
        input_images = [os.path.join(app.config['UPLOAD_FOLDER'], asset) for asset in selected_assets]
        
        def run_compliance():
            try:
                broadcast_log(session_id, "🔍 Starting compliance checks...", 'info')
                broadcast_log(session_id, f"📁 Using {len(input_images)} input asset(s) for brand compliance", 'info')
                
                compliance_results = []
                total_checks = 0
                
                # Count total checks first
                if os.path.exists(app.config['OUTPUT_FOLDER']):
                    for product in os.listdir(app.config['OUTPUT_FOLDER']):
                        product_path = os.path.join(app.config['OUTPUT_FOLDER'], product)
                        if os.path.isdir(product_path):
                            for ratio_folder in os.listdir(product_path):
                                ratio_path = os.path.join(product_path, ratio_folder)
                                if os.path.isdir(ratio_path):
                                    for img_file in os.listdir(ratio_path):
                                        if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                                            total_checks += 2  # brand + prohibited words
                
                broadcast_log(session_id, f"📊 Found {total_checks // 2} image(s) to check", 'info')
                
                check_count = 0
                if os.path.exists(app.config['OUTPUT_FOLDER']):
                    for product in os.listdir(app.config['OUTPUT_FOLDER']):
                        product_path = os.path.join(app.config['OUTPUT_FOLDER'], product)
                        if os.path.isdir(product_path):
                            product_name = product.replace('_', ' ')
                            
                            broadcast_log(session_id, f"\n{'='*60}", 'info')
                            broadcast_log(session_id, f"🔎 Checking: {product_name}", 'info')
                            broadcast_log(session_id, f"{'='*60}", 'info')
                            
                            # Check each aspect ratio
                            for ratio_folder in os.listdir(product_path):
                                ratio_path = os.path.join(product_path, ratio_folder)
                                if os.path.isdir(ratio_path):
                                    for img_file in os.listdir(ratio_path):
                                        if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                                            img_path = os.path.join(ratio_path, img_file)
                                            ratio_display = ratio_folder.replace('_', ':')
                                            
                                            # Brand compliance check
                                            if input_images:
                                                check_count += 1
                                                broadcast_log(session_id, f"⏳ [{check_count}/{total_checks}] Brand compliance check for {product_name} ({ratio_display})...", 'info')
                                                brand_result = gemini_service.check_brand_compliance(
                                                    img_path, input_images, product_name, ratio_display
                                                )
                                                compliance_results.append(brand_result)
                                                compliance_results.append("")  # Add blank line for readability
                                                
                                                # Determine if passed or failed
                                                if "PASS" in brand_result or "consistent" in brand_result.lower():
                                                    broadcast_log(session_id, f"✅ Brand compliance: PASS", 'success')
                                                else:
                                                    broadcast_log(session_id, f"⚠️  Brand compliance: Review needed", 'warning')
                                            
                                            # Prohibited words check
                                            check_count += 1
                                            broadcast_log(session_id, f"⏳ [{check_count}/{total_checks}] Prohibited words check for {product_name} ({ratio_display})...", 'info')
                                            words_result = gemini_service.check_prohibited_words(
                                                img_path, product_name, ratio_display
                                            )
                                            compliance_results.append(words_result)
                                            compliance_results.append("=" * 80)  # Add separator for readability
                                            compliance_results.append("")  # Add blank line for readability
                                            
                                            # Determine if passed or failed
                                            if "PASS" in words_result or "No prohibited" in words_result:
                                                broadcast_log(session_id, f"✅ Prohibited words check: PASS", 'success')
                                            else:
                                                broadcast_log(session_id, f"⚠️  Prohibited words check: Review needed", 'warning')
                
                # Save to Compliance_Checks.txt
                broadcast_log(session_id, f"\n💾 Saving results to Compliance_Checks.txt...", 'info')
                with open('Compliance_Checks.txt', 'w') as f:
                    for result in compliance_results:
                        f.write(result + '\n')
                
                broadcast_log(session_id, f"\n{'='*60}", 'info')
                broadcast_log(session_id, f"🎉 Compliance checks completed!", 'success')
                broadcast_log(session_id, f"📋 Total checks performed: {len(compliance_results)}", 'info')
                broadcast_log(session_id, f"💾 Results saved to: Compliance_Checks.txt", 'info')
                broadcast_log(session_id, f"{'='*60}\n", 'info')
                broadcast_log(session_id, "COMPLETE", 'complete')
                
            except Exception as e:
                import traceback
                error_msg = str(e)
                broadcast_log(session_id, f"❌ Error during compliance checks: {error_msg}", 'error')
                broadcast_log(session_id, traceback.format_exc(), 'error')
                broadcast_log(session_id, "COMPLETE", 'complete')
        
        # Start compliance checks in background thread
        thread = threading.Thread(target=run_compliance)
        thread.daemon = True
        thread.start()
        
        return jsonify({"success": True, "session_id": session_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    print("=" * 50)
    print("Creative Automation Pipeline")
    print("=" * 50)
    print("Starting web application...")
    print("Access the app at: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

