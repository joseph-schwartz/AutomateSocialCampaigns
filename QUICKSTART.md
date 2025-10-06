# Quick Start Guide

Get up and running in 3 minutes!

## Step 1: Clone the Repository

Clone the repository from GitHub:

```bash
git clone https://github.com/joseph-schwartz/AutomateSocialCampaigns.git
cd AutomateSocialCampaigns
```

**Note**: If you don't have Git installed, download it from [https://git-scm.com/downloads](https://git-scm.com/downloads) or download the repository as a ZIP file from GitHub and extract it.

## Step 2: Setup (First Time Only)

1. **Get Google Gemini API Key**
   - Visit: https://ai.google.dev/
   - Create an API key for Gemini 2.5 Flash

2. **Configure the Application**
   - Open `config.py`
   - Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key

3. **Install Dependencies**
   ```bash
   setup.bat
   ```
   Wait for installation to complete (~1-2 minutes)

   You may have to change the py to python, I needed to do the reverse hence it's defaulted that way.

## Step 3: Run the Application

```bash
run.bat
```

The app will open at: http://localhost:5000

## Step 4: Generate Your First Campaign

1. **Review the Campaign Briefs**
   - The middle panel shows example campaigns for Adobe Firefly and Photoshop
   - Edit if desired (must be valid JSON)

2. **Optional: Add Reference Images**
   - Place brand assets in the `InputAssets` folder
   - They'll appear in the right panel with checkboxes

3. **Generate!**
   - Click **"Generate Campaigns"** (bottom right)
   - **Watch real-time progress** in the log console at the bottom:
     - 🚀 Starting generation
     - 🗑️ Auto-clearing old images
     - ⏳ Progress for each aspect ratio
     - ✅ Success confirmations
   - Images appear in the gallery **automatically** as they complete (~2-3 minutes total)
   - Old images are automatically cleared before new generation starts

4. **Run Compliance Checks** (Optional)
   - Click **"Run Compliance Checks"**
   - Watch live progress in the log console
   - View detailed results in `Compliance_Checks.txt`

## Output Location

Generated images are saved to:
```
output/
  ├── Adobe_Firefly/
  │   ├── 1_1/      (Square)
  │   ├── 9_16/     (Vertical)
  │   └── 16_9/     (Horizontal)
  └── Adobe_Photoshop/
      ├── 1_1/
      ├── 9_16/
      └── 16_9/
```

## Tips

- **Customize Campaigns**: Edit the JSON in the middle panel
- **Load Different Briefs**: Click "Open JSON File" to load another file
- **Include Brand Assets**: Add images to `InputAssets` folder before generating
- **Multiple Products**: Add more objects to the JSON array
- **Monitor Progress**: Watch the log console for real-time updates with emoji indicators
- **Auto-Cleanup**: Don't worry about old images - they're automatically cleared before new generation

## Common Issues

**"Invalid API Key"**: Check `config.py` has the correct key

**"Module not found"**: Run `setup.bat` again

**App won't start**: Make sure Python 3.8+ is installed

**Doesn't know py, try python in batch scripts**:  You may have to change the py to python, I needed to do the reverse hence it's defaulted that way.
---

For detailed documentation, see [README.md](README.md)

