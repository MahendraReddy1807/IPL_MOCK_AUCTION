# 🔧 Fix Git Setup & Deploy

## Problem

You have nested git repositories that need to be cleaned up before deploying.

## Solution - Run These Commands

### From PowerShell in project root: `IPL MOCK AUCTION`

```powershell
# 1. Clean up nested git repos
Remove-Item -Recurse -Force .kiro\.git -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .kiro\specs\.git -ErrorAction SilentlyContinue

# 2. Remove existing .git if needed (start fresh)
Remove-Item -Recurse -Force .git -ErrorAction SilentlyContinue

# 3. Initialize git
git init

# 4. Add all files
git add .

# 5. Commit
git commit -m "IPL Mock Auction Arena - Streamlit Edition"

# 6. Rename branch to main
git branch -M main

# 7. Add your GitHub remote
git remote add origin https://github.com/MahendraReddy1807/IPL_MOCK_AUCTION.git

# 8. Push to GitHub
git push -u origin main
```

## OR Use the Automated Script

```powershell
# Run the fix script
.\fix_git_and_deploy.ps1
```

## After Successful Push

1. **Go to**: https://share.streamlit.io
2. **Sign in** with GitHub
3. **Click** "New app"
4. **Select**:
   - Repository: `MahendraReddy1807/IPL_MOCK_AUCTION`
   - Branch: `main`
   - Main file path: `streamlit_app/app.py`
5. **Click** "Deploy!"

## Your App Will Be Live At

```
https://your-app-name.streamlit.app
```

## Troubleshooting

### If push fails with authentication error:

```powershell
# Use GitHub CLI or Personal Access Token
gh auth login

# Or set up SSH keys
# Follow: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```

### If repository doesn't exist:

1. Go to: https://github.com/new
2. Create repository: `IPL_MOCK_AUCTION`
3. Don't initialize with README
4. Run the commands above again

### If you get "remote already exists":

```powershell
git remote remove origin
git remote add origin https://github.com/MahendraReddy1807/IPL_MOCK_AUCTION.git
git push -u origin main
```

## Quick Test Locally First

```powershell
cd streamlit_app
pip install streamlit sqlalchemy pandas pillow
streamlit run app.py
```

Open: http://localhost:8501

## Need Help?

Check these files:
- `streamlit_app/DEPLOY_NOW.md` - Full deployment guide
- `streamlit_app/QUICKSTART.md` - Quick start guide
- `DEPLOYMENT_READY.md` - Deployment overview

---

**You're almost there! Just clean up git and push! 🚀**
