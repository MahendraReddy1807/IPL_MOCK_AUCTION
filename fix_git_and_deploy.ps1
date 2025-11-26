# Fix Git Setup and Deploy Script
# Run this from the project root: IPL MOCK AUCTION

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fixing Git Setup for Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean up nested git repos
Write-Host "Step 1: Cleaning up nested git repositories..." -ForegroundColor Yellow
if (Test-Path ".kiro\.git") {
    Remove-Item -Recurse -Force ".kiro\.git"
    Write-Host "✓ Removed .kiro\.git" -ForegroundColor Green
}
if (Test-Path ".kiro\specs\.git") {
    Remove-Item -Recurse -Force ".kiro\specs\.git"
    Write-Host "✓ Removed .kiro\specs\.git" -ForegroundColor Green
}

# Step 2: Initialize git in project root
Write-Host ""
Write-Host "Step 2: Initializing git in project root..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "✓ Git already initialized" -ForegroundColor Green
} else {
    git init
    Write-Host "✓ Git initialized" -ForegroundColor Green
}

# Step 3: Add all files
Write-Host ""
Write-Host "Step 3: Adding all files..." -ForegroundColor Yellow
git add .
Write-Host "✓ Files added" -ForegroundColor Green

# Step 4: Commit
Write-Host ""
Write-Host "Step 4: Committing..." -ForegroundColor Yellow
git commit -m "IPL Mock Auction Arena - Streamlit Edition - Complete Application"
Write-Host "✓ Committed" -ForegroundColor Green

# Step 5: Rename branch to main
Write-Host ""
Write-Host "Step 5: Renaming branch to main..." -ForegroundColor Yellow
git branch -M main
Write-Host "✓ Branch renamed to main" -ForegroundColor Green

# Step 6: Add remote
Write-Host ""
Write-Host "Step 6: Setting up remote..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/MahendraReddy1807/IPL_MOCK_AUCTION.git"

# Remove existing remote if it exists
git remote remove origin 2>$null

# Add new remote
git remote add origin $remoteUrl
Write-Host "✓ Remote added: $remoteUrl" -ForegroundColor Green

# Step 7: Push
Write-Host ""
Write-Host "Step 7: Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "Note: You may need to authenticate with GitHub" -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ SUCCESS! Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Go to: https://share.streamlit.io" -ForegroundColor White
    Write-Host "2. Sign in with GitHub" -ForegroundColor White
    Write-Host "3. Click 'New app'" -ForegroundColor White
    Write-Host "4. Select repository: MahendraReddy1807/IPL_MOCK_AUCTION" -ForegroundColor White
    Write-Host "5. Set main file: streamlit_app/app.py" -ForegroundColor White
    Write-Host "6. Click 'Deploy!'" -ForegroundColor White
    Write-Host ""
    Write-Host "Your app will be live in 2-5 minutes! 🚀" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Push failed. Trying alternative..." -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual steps:" -ForegroundColor Yellow
    Write-Host "1. Make sure you're authenticated with GitHub" -ForegroundColor White
    Write-Host "2. Run: git push -u origin main --force" -ForegroundColor White
    Write-Host ""
}
