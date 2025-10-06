# Creative Automation Pipeline

A proof-of-concept creative automation pipeline that automates campaign asset generation for social ad campaigns using Google Gemini 2.5 Flash AI.

## Overview

This application enables creative teams to rapidly generate variations of campaign assets for different products, target regions, and audiences. It leverages GenAI to create localized marketing campaign images in multiple aspect ratios, complete with brand compliance checks.

## Features

### Core Features
- **Campaign Brief Management**: Load and edit campaign briefs in JSON format
- **Multi-Product Support**: Generate campaigns for multiple products simultaneously
- **Multi-Aspect Ratio Generation**: Automatically creates images in 1:1, 9:16, and 16:9 aspect ratios
- **Input Asset Reuse**: Optionally provide reference images that are sent to the AI for context
- **Localized Content**: AI generates campaigns with appropriate language and cultural context for target regions
- **Organized Output**: Generated images are automatically organized by product and aspect ratio
- **Real-Time Progress Updates**: Live streaming logs show generation progress with emoji indicators and status updates
- **Background Processing**: Campaigns generate asynchronously, allowing you to monitor progress without blocking the UI
- **Auto-Refresh Gallery**: Generated images appear in the gallery automatically as they complete

### Bonus Features
- **Enhanced Brand Compliance Checks**: Detailed PASS/FAIL verification of brand guidelines (logo and color usage) with specific findings
- **Prohibited Words Detection**: Flags inappropriate, misspelled, or unprofessional content
- **Comprehensive Compliance Reporting**: Generates a detailed `Compliance_Checks.txt` report with structured assessments for each image
- **Real-Time Compliance Monitoring**: Watch compliance checks run live with progress indicators

## Prerequisites

- Python 3.8 or higher
- Google Gemini API Key ([Get one here](https://ai.google.dev/))
- Windows OS (batch files provided for Windows; adapt for other OS)

## Installation & Setup

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd AutomateSocialCampaigns
```

### 2. Configure API Key

Edit `config.py` and replace the placeholder with your actual Gemini API key:

```python
GEMINI_API_KEY = "your-actual-api-key-here"
```

### 3. Install Dependencies

Run the setup batch file to create a virtual environment and install all requirements:

```bash
setup.bat
```

This will:
- Create a Python virtual environment in the `venv` folder
- Install all required packages from `requirements.txt`
- You may have to change the py to python, I needed to do the reverse hence it's defaulted that way.

## Running the Application

Simply run:

```bash
run.bat
```

This will:
- Activate the virtual environment
- Start the Flask web application
- Open the app at `http://localhost:5000`

## Usage Guide

### 1. Prepare Campaign Briefs

The app loads `inputs/campaign_briefs.json` by default. This file contains an array of campaign brief objects:

```json
[
    {
        "product_name": "Adobe Firefly",
        "target_region_market": "Texas, USA",
        "target_audience": "Game Developers",
        "campaign_message": "Create stunning game assets with AI-powered creativity"
    },
    {
        "product_name": "Adobe Photoshop",
        "target_region_market": "Paris, France",
        "target_audience": "Professional Photographers",
        "campaign_message": "Turn your photos into masterpieces"
    }
]
```

**Fields:**
- `product_name`: Name of the product being advertised
- `target_region_market`: Geographic region and market
- `target_audience`: Specific demographic or professional group
- `campaign_message`: The message to display in the campaign (can be in any language - the AI will localize it to match the target region if you specify it in English)

### 2. Add Input Assets (Optional)

Place reference images (logos, brand assets, product images) in the `InputAssets` folder. These will be displayed in the right panel with checkboxes. The selected images will be sent to the AI as reference material.

Supported formats: PNG, JPG, JPEG, GIF, WEBP

### 3. Generate Campaigns

1. Edit the campaign briefs in the text editor if needed
2. Select which input assets to include (all are selected by default)
3. Click **"Generate Campaigns"** button
4. Watch the **real-time progress** in the log console at the bottom:
   - 🚀 Starting generation
   - 🗑️ Clearing old images (auto-cleanup)
   - ⏳ Generating each aspect ratio
   - ✅ Success confirmations
   - Images appear in the gallery automatically as they complete
5. The AI will generate three versions of each campaign:
   - 1:1 (Square) aspect ratio
   - 9:16 (Vertical/Story) aspect ratio
   - 16:9 (Horizontal/Landscape) aspect ratio

Generated images appear in the left panel in real-time and are saved to:
```
output/
  ├── Adobe_Firefly/
  │   ├── 1_1/
  │   ├── 9_16/
  │   └── 16_9/
  └── Adobe_Photoshop/
      ├── 1_1/
      ├── 9_16/
      └── 16_9/
```

### 4. Run Compliance Checks

After generating campaigns, click **"Run Compliance Checks"** to:
- Verify brand guidelines (logo and color usage) with detailed PASS/FAIL assessments
- Check for prohibited/inappropriate words, misspellings, and unprofessional content
- Watch real-time progress of each check in the log console
- Generate a comprehensive report saved to `Compliance_Checks.txt` with structured findings

**Enhanced Compliance Report Format:**
Each check includes:
- Product name and aspect ratio
- Why the check is needed (explanation)
- Logo Assessment with detailed findings
- Color Assessment with detailed findings
- Text Content Assessment with all visible text
- Overall PASS/FAIL result

## Project Structure

```
AutomateSocialCampaigns/
├── app.py                      # Main Flask application
├── models.py                   # Data models (CampaignBrief)
├── gemini_service.py          # Google Gemini API integration
├── config.py                   # Configuration (API keys)
├── requirements.txt            # Python dependencies
├── setup.bat                   # Setup script (Windows)
├── run.bat                     # Run script (Windows)
├── README.md                   # This file
├── inputs/
│   └── campaign_briefs.json   # Default campaign briefs
├── InputAssets/               # Reference images (user-provided)
├── output/                    # Generated campaign images
├── templates/
│   └── index.html             # Web UI template
└── static/
    └── style.css              # Web UI styling
```

## Example Input & Output

### Example Input (campaign_briefs.json)

```json
[
    {
        "product_name": "Adobe Firefly",
        "target_region_market": "Texas, USA",
        "target_audience": "Game Developers",
        "campaign_message": "Create stunning game assets with AI-powered creativity"
    }
]
```

### Example Output

**Generated Files:**
- `output/Adobe_Firefly/1_1/campaign_1_1.png` - Square format
- `output/Adobe_Firefly/9_16/campaign_9_16.png` - Vertical format
- `output/Adobe_Firefly/16_9/campaign_16_9.png` - Horizontal format

**Compliance Report (Compliance_Checks.txt):**
```
PRODUCT: Adobe Firefly
ASPECT RATIO: 1:1

BRAND COMPLIANCE CHECK:
Why this check is needed: Brand compliance ensures the campaign image properly uses the official brand logo and colors...

Logo Assessment: PASS
- What was checked: Presence and correct usage of brand logo
- Findings: [Detailed AI analysis of logo usage]

Color Assessment: PASS
- What was checked: Usage of official brand colors
- Findings: [Detailed AI analysis of color usage]

Overall Result: PASS

PRODUCT: Adobe Firefly
ASPECT RATIO: 1:1

PROHIBITED WORDS CHECK:
Why this check is needed: This check ensures the campaign image does not contain any inappropriate, offensive...

Text Content Assessment: PASS
- What was checked: All visible text in the image for prohibited words...
- Text found in image: [List of all text found]
- Findings: [Detailed AI analysis of text content]

Overall Result: PASS
```

## Key Design Decisions

### 1. Chat History for Aspect Ratios
To maintain visual consistency across aspect ratios, the app uses Gemini's chat history feature. The initial 1:1 image is generated first, then the 9:16 and 16:9 versions are requested as follow-ups in the same conversation. This ensures all three ratios are variations of the same core design.

### 2. Flask Web Application with Real-Time Updates
A web-based UI was chosen over a command-line tool for better user experience:
- Visual JSON editor with syntax highlighting
- Interactive asset selection with checkboxes
- Real-time gallery view of generated images with auto-refresh
- Live progress logging with Server-Sent Events (SSE)
- Background processing for non-blocking operations
- Immediate visual feedback with emoji indicators

### 3. Organized Output Structure
Images are organized by product name and aspect ratio for easy navigation and asset management, following a standard naming convention.

### 4. Enhanced Compliance Checks with Real-Time Monitoring
Brand compliance and prohibited words checks are run separately (on-demand) rather than during generation to:
- Reduce initial generation time
- Allow users to review visual output first
- Batch compliance checks for efficiency
- Provide detailed PASS/FAIL assessments with specific findings
- Stream progress updates live so users can monitor each check
- Generate structured reports with clear explanations

### 5. Google Gemini 2.5 Flash
Chosen for its:
- Native image generation capabilities
- Multi-modal input support (text + images)
- Chat history support for consistent variations
- Fast response times

## Assumptions & Limitations

### Assumptions
1. Users have valid Google Gemini API access
2. Users will provide meaningful campaign briefs
3. Input assets (if provided) are relevant brand materials
4. Users understand JSON format for editing briefs

### Limitations
1. **API Rate Limits**: Google Gemini has rate limits; generating many campaigns simultaneously may hit these limits
2. **Image Quality**: Generated image quality depends on Gemini's capabilities and prompt interpretation
3. **Language Support**: While the AI can generate text in many languages, accuracy depends on Gemini's training
4. **Brand Compliance**: Automated checks are AI-based and may not catch all brand guideline violations; human review recommended
5. **No Image Editing**: Generated images cannot be edited within the app; re-generation required for changes
6. **Windows-Centric**: Batch files are Windows-specific; Unix/Mac users need to adapt scripts
7. **Local Storage Only**: No cloud storage integration in this POC

## Troubleshooting

### "Invalid API Key" Error
- Verify your API key in `config.py` is correct
- Ensure you have access to Gemini 2.5 Flash

### Images Not Generating
- Check console logs for specific error messages
- Verify internet connection
- Check API quota/rate limits

### Compliance Checks Fail
- Ensure images have been generated first
- Verify input assets are in the InputAssets folder
- Check that images are in supported formats

## Future Enhancements

- Cloud storage integration (Azure, AWS, Dropbox)
- Batch processing with progress indicators
- Advanced brand guideline customization
- Multi-language UI support
- Export campaigns in various formats
- Analytics and performance tracking
- Approval workflow integration
- Template library

##  Any assumpLons or limitaLons 
- Didn't feel like setting up an Azure CDN for images, seemed to subtly reference that in the data sources, but wasn't clear it was required and I didn't want to pay for it
- Sometimes the other aspect ratios generate poorly via seems or mushed images.  This can be solved with better prompting / multiple attempts.  
    - This came about from an assumption that we wanted it to be the same or almost the same ad just in a different ratio
    - We can also generate another ad in that ratio, but it would be a different ad
    - We could outpaint, but it wouldn't look great, this is the best solution in my opinion and probably just needs better prompting or trying another model like seedream
    - This will improve with future models as well with little requirement from our end besides changing the model.

## License

This is a proof-of-concept for educational and demonstration purposes.

## Contact

For questions or issues, please refer to the project documentation or contact the development team.

---

**Built with ❤️ using Google Gemini 2.5 Flash, Flask, and Python**

