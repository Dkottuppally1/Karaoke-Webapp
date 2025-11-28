# 🚀 How to Push to GitHub

## Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in:
   - **Repository name**: `karaoke-webapp` (or your preferred name)
   - **Description**: "AI-powered karaoke generator using Demucs source separation"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## Step 2: Connect Your Local Repo to GitHub

After creating the repo, GitHub will show you commands. Use these:

```bash
cd "/Users/dkottuppally/Karaoke Webapp"

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/karaoke-webapp.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/karaoke-webapp.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify

1. Go to your GitHub repository page
2. You should see all your files there!

## 🔐 Authentication

If you get authentication errors:

**Option A: Personal Access Token (HTTPS)**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when pushing

**Option B: SSH Keys (Recommended)**
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add to GitHub: Settings → SSH and GPG keys → New SSH key
3. Use SSH URL: `git@github.com:USERNAME/REPO.git`

## 📝 Future Updates

After making changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

## 🎯 What's Included

Your repo includes:
- ✅ All source code (backend & frontend)
- ✅ Configuration files
- ✅ Documentation (README, guides)
- ✅ .gitignore (excludes venv, node_modules, outputs, etc.)

What's NOT included (by design):
- ❌ Virtual environment (venv/)
- ❌ Node modules (node_modules/)
- ❌ Generated audio files (outputs/)
- ❌ Model cache files
- ❌ Environment variables (.env)

This is correct! Users will install dependencies themselves.

