# How to Get Your OpenAI OAuth Credentials
## Complete Step-by-Step Guide (5 minutes)

---

## Step 1: Go to OpenAI Platform

**Open in your browser:**
```
https://platform.openai.com/apps
```

(Make sure you're logged in to your OpenAI account)

---

## Step 2: Create New App

Click the **"Create new app"** button

---

## Step 3: Fill in App Details

### App Name
```
ArBot-MiniDB Analysis
```

### Description (optional)
```
Batch vision analysis for bathroom water damage assessment
```

### Redirect URI (IMPORTANT - exactly as shown)
```
http://localhost:8000/callback
```

### Scopes (select these checkboxes)
- ✅ `read:models`
- ✅ `write:files`
- ✅ `read:files`

---

## Step 4: Save and Get Credentials

Click **"Create"** or **"Save"**

You'll see two important values:

### Client ID
```
oauth-xxxxxxxxxxxxxxxxxxxxxxxx
```
**Copy this value**

### Client Secret
```
oauth_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
**Copy this value**

⚠️ **WARNING:** Keep the Client Secret private!
Don't share it with anyone or commit it to git.

---

## Step 5: Fill in Your .env.local File

Open the file: `C:\Dev\personal\ArBot-MiniDB\.env.local`

Replace the placeholders:

### BEFORE:
```
OPENAI_CLIENT_ID=YOUR_CLIENT_ID_HERE
OPENAI_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
OPENAI_REDIRECT_URI=http://localhost:8000/callback
```

### AFTER (with your actual credentials):
```
OPENAI_CLIENT_ID=oauth-abc123def456ghi789jkl012mno
OPENAI_CLIENT_SECRET=oauth_xyz789abc456def123ghi456jkl789
OPENAI_REDIRECT_URI=http://localhost:8000/callback
```

---

## Step 6: Save and Run

1. **Save the .env.local file** (Ctrl+S)
2. **Go to your Codex tab**
3. **Run the analysis:**
   ```
   python gpt4o_batch_analysis_oauth.py
   ```

---

## What Happens Next

1. **Codex reads your credentials** from .env.local
2. **Browser opens automatically** asking you to authorize
3. **You see:** "ArBot-MiniDB Analysis is requesting permission"
4. **You click:** "Authorize" or "Allow"
5. **Analysis starts** automatically processing all 94 images
6. **Results saved** to `docs/To validate/ArBot-Vision-GPT4o_v1.0/individual_analysis/`

---

## Troubleshooting

### "Client ID not found"
- Check that .env.local is in the correct location: `C:\Dev\personal\ArBot-MiniDB\.env.local`
- Make sure you didn't have spaces before/after the value
- Restart Codex after creating .env.local

### "Invalid redirect URI"
- Make sure you used exactly: `http://localhost:8000/callback`
- No extra spaces or slashes

### "Browser doesn't open"
- Manually visit the URL printed in the terminal
- Or check your firewall settings on port 8000

### "Authorization failed"
- Make sure your Client ID and Secret are correct
- Try creating a new OAuth app from scratch

---

## Once You Have Your Credentials

**Paste them into .env.local like this:**

```bash
OPENAI_CLIENT_ID=oauth-YOUR_CLIENT_ID_HERE
OPENAI_CLIENT_SECRET=oauth_YOUR_CLIENT_SECRET_HERE
OPENAI_REDIRECT_URI=http://localhost:8000/callback
```

Then you're ready to run the analysis!

---

## ⏱️ Expected Timeline

- **Get OAuth Credentials:** 5 minutes
- **Fill in .env.local:** 1 minute
- **First Authorization:** 2 minutes (browser popup)
- **Analysis of 94 images:** 60-90 minutes
- **Total Time:** ~2 hours

---

**Ready?** Once you have your credentials, you can run the analysis anytime! 🚀
