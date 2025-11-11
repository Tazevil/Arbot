# Quick Start: Run GPT-4o Analysis via Claude Code (Codex)
## Copy & Paste into Codex Tab - Fully Automated Setup

**Use this guide to run everything directly in Claude Code/Codex**

---

## ONE-COMMAND SETUP & RUN

### Paste This Into Claude Code:

```
I need to run a GPT-4o Vision analysis on 94 images in the ArBot-MiniDB project.

The project is in: C:\Dev\personal\ArBot-MiniDB

Here's what I need you to do:

1. Create `oauth_token_manager.py` - OAuth authentication handler
2. Create `gpt4o_batch_analysis_oauth.py` - Analysis script using OAuth
3. Set up `.env.local` with placeholder credentials (I'll fill in)
4. Configure `.gitignore` to protect credentials
5. Run the analysis when ready

The analysis should:
- Process all 94 JPEG images from the images/ directory
- Use GPT-4o Vision model
- Output JSON analysis files to docs/To validate/ArBot-Vision-GPT4o_v1.0/individual_analysis/
- Generate summary statistics
- Use OAuth authentication (no hardcoded API keys)

Please create all necessary files and guide me through the OAuth setup.
```

---

## Alternative: Step-by-Step Commands for Codex

### Command 1: Create OAuth Token Manager

```
Create a Python script at C:\Dev\personal\ArBot-MiniDB\oauth_token_manager.py that:

- Implements OAuth flow for OpenAI API
- Handles authorization code exchange
- Manages token storage in .oauth/ directory
- Supports token refresh
- Has a local callback server on port 8000
- Can revoke tokens
- Logs all operations clearly

Make it production-ready with error handling.
```

### Command 2: Create GPT-4o Analysis Script

```
Create a Python script at C:\Dev\personal\ArBot-MiniDB\gpt4o_batch_analysis_oauth.py that:

- Imports the OAuth token manager
- Processes all 94 images in C:\Dev\personal\ArBot-MiniDB\images\
- Skips preview images automatically
- Uses GPT-4o Vision API with OAuth authentication
- Analyzes each image for construction defects
- Focuses on:
  - Waterproofing (étanchéité)
  - Plumbing (plomberie)
  - Ventilation
  - Tiling/finishes (carrelage)
  - Site conditions
  - Pre-existing damage
- Outputs JSON files to docs/To validate/ArBot-Vision-GPT4o_v1.0/individual_analysis/
- Uses French technical terminology for defect categories
- References DTU standards and specifications
- Shows progress bar (X/94 images analyzed)
- Handles API errors gracefully
- Low temperature (0.2) for consistency

Include proper error handling and retry logic.
```

### Command 3: Create Environment Setup

```
Create a .env.local file at C:\Dev\personal\ArBot-MiniDB\.env.local with:

OPENAI_CLIENT_ID=YOUR_CLIENT_ID_HERE
OPENAI_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
OPENAI_REDIRECT_URI=http://localhost:8000/callback

And update .gitignore to include:
.env
.env.local
.oauth/
oauth_token.json
```

### Command 4: Verify and Run

```
Now:
1. Check that all three files exist
2. Verify Python is available and libraries installed (pip install openai requests)
3. Show me the setup status
4. Ask me for my OpenAI OAuth credentials
5. Once I provide them, update .env.local
6. Run the analysis: python gpt4o_batch_analysis_oauth.py
```

---

## Exact Steps to Run from Codex NOW

### Step 1: Go to Claude Code Tab

The Codex tab you have open should already have project context.

### Step 2: Use This Exact Command

Copy and paste into Claude Code:

```
Context: C:\Dev\personal\ArBot-MiniDB

Please create and execute the complete GPT-4o OAuth analysis setup:

1. **oauth_token_manager.py** - OAuth handler (I'll provide the full script)
2. **gpt4o_batch_analysis_oauth.py** - Analysis runner (I'll provide the full script)
3. **Setup .env.local** - Configuration file
4. **Install dependencies** - pip install openai requests
5. **Prepare output directory** - Create docs/To validate/ArBot-Vision-GPT4o_v1.0/individual_analysis/

Then show me the status and ask for my OpenAI OAuth Client ID and Secret.

When I provide those, update .env.local and run:
python gpt4o_batch_analysis_oauth.py

This will analyze all 94 images from images/ directory using GPT-4o Vision with OAuth authentication.
```

### Step 3: Provide OAuth Credentials When Asked

When Codex asks, paste:
- **Client ID:** `oauth-xxxxxxxxxxxxxxxx`
- **Client Secret:** `oauth_xxxxxxxxxxxxxxxxxxxxxxxx`

(Get these from https://platform.openai.com/apps)

### Step 4: Authorize in Browser

When the script starts, it will:
1. Open browser automatically
2. Ask you to authorize "ArBot-MiniDB Analysis"
3. Return to terminal with token
4. Start analyzing images

---

## If Codex Doesn't Have Full Context

Use this command to load it:

```
I'm working on a project in C:\Dev\personal\ArBot-MiniDB with 94 bathroom renovation images.

The structure is:
- images/ - 94 JPG files (photos of bathroom damage)
- json/ - metadata and knowledge base
- docs/ - documentation, standards, context
- scripts/ - utility scripts

I need to:
1. Analyze all 94 images with GPT-4o Vision
2. Detect construction defects (waterproofing, plumbing, ventilation, etc.)
3. Output JSON analysis files with defect details
4. Use OAuth for API authentication (no hardcoded keys)
5. Save results to docs/To validate/ArBot-Vision-GPT4o_v1.0/

Please help me set this up and run it.
```

---

## What Happens When You Run It

### First Execution:

```
[Claude Code Terminal Output]

Creating oauth_token_manager.py... ✓
Creating gpt4o_batch_analysis_oauth.py... ✓
Creating .env.local... ✓
Installing dependencies... ✓

==========================================
GPT-4o Vision Analysis Setup Complete
==========================================

OpenAI OAuth Credentials Required:
Client ID: [paste your Client ID]
Client Secret: [paste your Client Secret]

[You paste credentials]

Updating .env.local... ✓

Starting analysis...

[Browser opens → You click Authorize → Returns to terminal]

✓ OAuth Authentication Successful

Scanning for images...
✓ Found 94 images

[1/94] 0001_SDB_GEN_20250818.jpg... ✓
[2/94] 0002_SDB_GEN_20250818.jpg... ✓
[3/94] 0003_SALON-PROTECTION_GEN_20250818.jpg... ✓
...
[94/94] 3805_DORMANT_DEG.jpg... ✓

==========================================
Analysis Complete
==========================================
Successful: 94/94
Output: docs/To validate/ArBot-Vision-GPT4o_v1.0/individual_analysis/

Generating summary...
✓ Summary created
```

---

## Full Scripts to Create in Codex

If Codex asks for the actual code, use these:

### Script 1: oauth_token_manager.py

```python
#!/usr/bin/env python3
import os
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlencode
import requests
from datetime import datetime, timedelta

OAUTH_DIR = Path(".oauth")
TOKEN_FILE = OAUTH_DIR / "openai_token.json"
OAUTH_DIR.mkdir(exist_ok=True)

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        query = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
        if 'code' in query:
            OAuthCallbackHandler.auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>✓ Authorization Successful!</h1><p>Close this window.</p></body></html>")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authorization Failed</h1></body></html>")

    def log_message(self, format, *args):
        pass

class OAuthTokenManager:
    def __init__(self):
        self.client_id = os.getenv("OPENAI_CLIENT_ID")
        self.client_secret = os.getenv("OPENAI_CLIENT_SECRET")
        self.redirect_uri = os.getenv("OPENAI_REDIRECT_URI", "http://localhost:8000/callback")
        self.token_url = "https://api.openai.com/oauth/authorize"
        self.exchange_url = "https://api.openai.com/oauth/token"

        if not self.client_id or not self.client_secret:
            raise ValueError("OPENAI_CLIENT_ID and OPENAI_CLIENT_SECRET required")

    def get_authorization_url(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read:models write:files read:files"
        }
        return f"{self.token_url}?{urlencode(params)}"

    def request_authorization(self):
        print("\n" + "="*60)
        print("OpenAI OAuth Authorization Required")
        print("="*60)
        auth_url = self.get_authorization_url()
        print(f"\nOpening browser for authorization...")
        print(f"Visit: {auth_url}\n")

        server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)
        print("Waiting for authorization...")
        webbrowser.open(auth_url)

        while OAuthCallbackHandler.auth_code is None:
            server.handle_request()

        auth_code = OAuthCallbackHandler.auth_code
        server.server_close()
        print("✓ Authorization received!")
        return auth_code

    def exchange_code_for_token(self, auth_code):
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(self.exchange_url, json=data)
        response.raise_for_status()

        token_data = response.json()
        token_data['obtained_at'] = datetime.utcnow().isoformat()
        print("✓ Access token obtained!")
        return token_data

    def save_token(self, token_data):
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f)
        os.chmod(TOKEN_FILE, 0o600)
        print(f"✓ Token saved")

    def load_token(self):
        if not TOKEN_FILE.exists():
            return None
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)

    def is_token_expired(self, token_data):
        if not token_data or 'obtained_at' not in token_data:
            return True
        obtained = datetime.fromisoformat(token_data['obtained_at'])
        expires_in = token_data.get('expires_in', 3600)
        expiry = obtained + timedelta(seconds=expires_in)
        return datetime.utcnow() > expiry

    def refresh_token(self, token_data):
        if 'refresh_token' not in token_data:
            return None
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token_data['refresh_token'],
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(self.exchange_url, json=data)
        response.raise_for_status()
        new_token = response.json()
        new_token['obtained_at'] = datetime.utcnow().isoformat()
        print("✓ Token refreshed!")
        return new_token

    def get_valid_token(self):
        token_data = self.load_token()
        if token_data and not self.is_token_expired(token_data):
            print("✓ Using cached token")
            return token_data['access_token']

        if token_data and self.is_token_expired(token_data):
            new_token = self.refresh_token(token_data)
            if new_token:
                self.save_token(new_token)
                return new_token['access_token']

        auth_code = self.request_authorization()
        token_data = self.exchange_code_for_token(auth_code)
        self.save_token(token_data)
        return token_data['access_token']
```

### Script 2: gpt4o_batch_analysis_oauth.py

```python
#!/usr/bin/env python3
import os
import json
import base64
from pathlib import Path
from datetime import datetime
import openai
from oauth_token_manager import OAuthTokenManager

IMAGES_DIR = Path("images")
OUTPUT_DIR = Path("docs/To validate/ArBot-Vision-GPT4o_v1.0/individual_analysis")
MODEL = "gpt-4o"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

oauth_manager = OAuthTokenManager()

PROMPT = """You are an expert in construction damage assessment for French bathrooms.

ANALYZE this image for defects in:
1. Waterproofing (étanchéité) - DTU 25.41
2. Plumbing (plomberie) - Water protection
3. Ventilation (ventilation) - Air flow
4. Tiling (carrelage) - Surface quality
5. Finishing (finition) - Paint, joints
6. Existing damage (existant) - Pre-existing issues
7. Site conditions (chantier) - Work area cleanliness

Return ONLY valid JSON:
{
  "image_analysis": {
    "file_id": "FILE_ID",
    "file_name": "FILENAME",
    "analysis_timestamp": "ISO_TIMESTAMP",
    "model": "gpt-4o",
    "defects": [
      {
        "id": "D01",
        "category": "étanchéité|plomberie|ventilation|carrelage|finition|existant|chantier",
        "type": "non-conformité|dégradation|absence|insuffisant",
        "severity": 1,
        "priority": 1,
        "confidence": 0.95,
        "title": "SHORT_TITLE",
        "description": "DETAILED_DESCRIPTION",
        "standard_ref": "DTU_25.41_1993|DTU_52.2_2022|FT_NAME",
        "recommended_action": "HOW_TO_FIX",
        "image_area": "WHERE_IN_IMAGE"
      }
    ],
    "summary": {
      "total_defects": 0,
      "critical_defects": 0,
      "overall_assessment": "TEXT"
    }
  }
}"""

def analyze_image(client, image_path, filename):
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}", "detail": "high"}},
                    {"type": "text", "text": PROMPT}
                ]
            }],
            temperature=0.2,
            max_tokens=2000
        )

        analysis_text = response.choices[0].message.content
        try:
            analysis_json = json.loads(analysis_text)
        except:
            analysis_json = {"image_analysis": {"file_name": filename, "raw_response": analysis_text, "parse_error": True}}

        return {"status": "success", "data": analysis_json, "tokens": response.usage.total_tokens}
    except Exception as e:
        return {"status": "error", "error": str(e), "filename": filename}

def main():
    print("="*80)
    print("GPT-4o Vision Analysis with OAuth")
    print("="*80)

    try:
        token = oauth_manager.get_valid_token()
        client = openai.OpenAI(api_key=token)
        print("✓ Authentication successful\n")
    except Exception as e:
        print(f"✗ Auth failed: {e}")
        return 1

    images = sorted([f for f in IMAGES_DIR.glob("*.jpg") if "preview" not in str(f)])
    total = len(images)

    print(f"Found {total} images")
    if input(f"Analyze {total} images? (yes/no): ").strip().lower() != "yes":
        return 0

    successful = 0
    for i, img_path in enumerate(images, 1):
        filename = img_path.name
        file_id = filename.split("_")[0]
        print(f"[{i:2d}/{total}] {filename}...", end=" ", flush=True)

        result = analyze_image(client, img_path, filename)
        if result["status"] == "success":
            output = OUTPUT_DIR / f"{file_id}_analysis.json"
            with open(output, "w", encoding="utf-8") as f:
                json.dump(result["data"], f, indent=2, ensure_ascii=False)
            successful += 1
            print("✓")
        else:
            print(f"✗ {result.get('error', 'Unknown error')}")

    print("\n" + "="*80)
    print(f"Complete: {successful}/{total} successful")
    print(f"Output: {OUTPUT_DIR}")

if __name__ == "__main__":
    exit(main())
```

---

## TL;DR - Copy This To Codex Right Now:

```
I have a project at C:\Dev\personal\ArBot-MiniDB with 94 bathroom images.

Please:
1. Create oauth_token_manager.py in the project root
2. Create gpt4o_batch_analysis_oauth.py in the project root
3. Create .env.local with OAuth placeholders
4. Install pip dependencies (openai, requests)
5. Set up output directory structure
6. Show me setup status and ask for OpenAI OAuth credentials

I'll provide Client ID and Secret when asked, then we'll run:
python gpt4o_batch_analysis_oauth.py

To analyze all 94 images using GPT-4o Vision with OAuth authentication.
```

---

## That's It!

Codex will:
- ✅ Create all necessary files
- ✅ Set up environment
- ✅ Ask for your OAuth credentials
- ✅ Handle authorization
- ✅ Run analysis
- ✅ Output JSON files with defects

**No manual script creation needed!**
