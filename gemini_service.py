"""
Service for interacting with Google Gemini 2.5 Flash API
"""
import base64
import mimetypes
import os
from google import genai
from google.genai import types
import config


class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash-image"
    
    def save_binary_file(self, file_name, data):
        """Save binary data to file"""
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, "wb") as f:
            f.write(data)
        print(f"File saved to: {file_name}")
        return file_name
    
    def generate_campaign_image(self, campaign_brief, input_images=None, aspect_ratio="1:1", chat_history=None):
        """
        Generate a campaign image using Gemini
        
        Args:
            campaign_brief: CampaignBrief object
            input_images: List of image file paths to send as reference
            aspect_ratio: Aspect ratio for the image (1:1, 9:16, 16:9)
            chat_history: Previous chat history for follow-up requests
        
        Returns:
            Tuple of (image_path, chat_history)
        """
        # Build the prompt
        if chat_history is None:
            prompt = f"""Given this campaign brief:
Product: {campaign_brief.product_name}
Target Region/Market: {campaign_brief.target_region_market}
Target Audience: {campaign_brief.target_audience}
Campaign Message: {campaign_brief.campaign_message}

And possibly relevant input assets, make a marketing campaign image for the target region/market and audience mentioned in the brief.
It should follow the main language spoken in that country or if a language is specified in the campaign brief, use that language.
Only include the input asset images if they are relevant to the product name.
Do not shorten the product name unless done so in the campaign brief.
It should have the exact text of the campaign message in the advert: "{campaign_brief.campaign_message}"  adjusted to the main language of the target region/market.
Please generate the image in {aspect_ratio} aspect ratio."""
        else:
            if aspect_ratio == "9:16":
                prompt = "Extend this image to make a seamless portrait version of this.  Reimagine it a little if you have to to make it look like it was designed for portrait."
            elif aspect_ratio == "16:9":
                prompt = "Extend this image to make a seamless landscape version of this.  Reimagine it a little if you have to to make it look like it was designed for landscape."
            elif aspect_ratio == "1:1":
                prompt = "Extend this image to make a seamless square version of this.  Reimagine it a little if you have to to make it look like it was designed for square."
            else:
                prompt = f"Transform the previous campaign image to {aspect_ratio} aspect ratio maintaining the same content and style and consistency."
        
        # Build contents
        parts = [types.Part.from_text(text=prompt)]
        
        # Add input images if provided and this is the first request
        if input_images and chat_history is None:
            for img_path in input_images:
                try:
                    with open(img_path, 'rb') as f:
                        img_data = f.read()
                    mime_type = mimetypes.guess_type(img_path)[0] or 'image/jpeg'
                    parts.append(types.Part.from_bytes(data=img_data, mime_type=mime_type))
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")
        
        # Build the contents list
        if chat_history:
            contents = chat_history + [types.Content(role="user", parts=parts)]
        else:
            contents = [types.Content(role="user", parts=parts)]
        
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
            ),
        )
        
        # Generate content
        generated_image = None
        response_text = ""
        
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue
            
            if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                generated_image = inline_data.data
            else:
                if hasattr(chunk, 'text'):
                    response_text += chunk.text
        
        # Update chat history
        if chunk.candidates and chunk.candidates[0].content:
            new_history = contents + [chunk.candidates[0].content]
        else:
            new_history = contents
        
        return generated_image, new_history
    
    def check_brand_compliance(self, generated_image_path, input_images, product_name, aspect_ratio=""):
        """
        Check if generated image follows brand guidelines (logo and colors)
        """
        ratio_text = f" ({aspect_ratio})" if aspect_ratio else ""
        prompt = f"""Check if the generated campaign image for {product_name}{ratio_text} follows brand guidelines.
        
Please analyze:
1. If there are input brand asset images, does it use the logo from the input brand assets?
2. If there are input brand asset images, does it use the brand colors from the input brand assets?

Respond in this detailed format:

PRODUCT: {product_name}
ASPECT RATIO: {aspect_ratio if aspect_ratio else "N/A"}

BRAND COMPLIANCE CHECK:
Why this check is needed: Brand compliance ensures the campaign image properly uses the official brand logo and colors to maintain brand consistency and recognition across all marketing materials.

Logo Assessment: [PASS/FAIL]
- What was checked: Presence and correct usage of brand logo
- Findings: [Detailed explanation of what you found regarding the logo - is it present, correctly placed, properly sized, matches brand assets, etc.]

Color Assessment: [PASS/FAIL]
- What was checked: Usage of official brand colors
- Findings: [Detailed explanation of what you found regarding colors - are brand colors used, are they accurate, any issues with color usage, etc.]

Overall Result: [PASS/FAIL]
"""
        
        parts = [types.Part.from_text(text=prompt)]
        
        # Add input images
        for img_path in input_images:
            try:
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                mime_type = mimetypes.guess_type(img_path)[0] or 'image/jpeg'
                parts.append(types.Part.from_bytes(data=img_data, mime_type=mime_type))
            except Exception as e:
                print(f"Error loading input image {img_path}: {e}")
        
        # Add generated image
        try:
            with open(generated_image_path, 'rb') as f:
                img_data = f.read()
            mime_type = mimetypes.guess_type(generated_image_path)[0] or 'image/jpeg'
            parts.append(types.Part.from_bytes(data=img_data, mime_type=mime_type))
        except Exception as e:
            print(f"Error loading generated image {generated_image_path}: {e}")
            return f"{product_name} - Error checking compliance"
        
        contents = [types.Content(role="user", parts=parts)]
        
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["TEXT"],
        )
        
        response_text = ""
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        ):
            if hasattr(chunk, 'text'):
                response_text += chunk.text
        
        return response_text.strip()
    
    def check_prohibited_words(self, generated_image_path, product_name, aspect_ratio=""):
        """
        Check if the generated image contains any prohibited or inappropriate words
        """
        ratio_text = f" ({aspect_ratio})" if aspect_ratio else ""
        prompt = f"""Analyze the text content in this campaign image for {product_name}{ratio_text}.
        
Check if it contains any prohibited, inappropriate, offensive, or unprofessional words.

Respond in this detailed format:

PRODUCT: {product_name}
ASPECT RATIO: {aspect_ratio if aspect_ratio else "N/A"}

PROHIBITED WORDS CHECK:
Why this check is needed: This check ensures the campaign image does not contain any inappropriate, offensive, misspelled, or unprofessional text that could harm the brand reputation or violate content policies.

Text Content Assessment: [PASS/FAIL]
- What was checked: All visible text in the image for prohibited words, inappropriate language, misspellings, or unprofessional content
- Text found in image: [List all text visible in the image]
- Findings: [Detailed explanation of what you found - if any issues exist, specify exactly which words/phrases are problematic and why; if clean, confirm all text is appropriate]

Overall Result: [PASS/FAIL]
"""
        
        parts = [types.Part.from_text(text=prompt)]
        
        # Add generated image
        try:
            with open(generated_image_path, 'rb') as f:
                img_data = f.read()
            mime_type = mimetypes.guess_type(generated_image_path)[0] or 'image/jpeg'
            parts.append(types.Part.from_bytes(data=img_data, mime_type=mime_type))
        except Exception as e:
            print(f"Error loading generated image {generated_image_path}: {e}")
            return f"{product_name} - Error checking prohibited words"
        
        contents = [types.Content(role="user", parts=parts)]
        
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["TEXT"],
        )
        
        response_text = ""
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        ):
            if hasattr(chunk, 'text'):
                response_text += chunk.text
        
        return response_text.strip()

