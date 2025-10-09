#!/bin/bash

# NFL Fatigue Tracker - GitHub Setup Script
echo "🏈 Setting up GitHub repository for NFL Fatigue Tracker..."

# Initialize git repository
echo "Initializing Git repository..."
git init

# Add all files to staging
echo "Adding files to Git..."
git add .

# Create initial commit
echo "Creating initial commit..."
git commit -m "Initial commit: NFL Player Fatigue Tracking Platform

- Complete fatigue tracking system with real-time analysis
- Player management with photo uploads and status tracking
- Advanced metrics analysis (BPM, RR_MS, Speed, Acceleration)
- Intelligent fatigue prediction algorithm
- Personalized recommendations for each player
- Data persistence with JSON storage
- Clean, professional web interface built with Streamlit"

echo ""
echo "✅ Git repository initialized successfully!"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub (https://github.com/new)"
echo "2. Name it: nfl-fatigue-tracker"
echo "3. Don't initialize with README (we already have one)"
echo "4. Copy the repository URL"
echo "5. Run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/nfl-fatigue-tracker.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Replace YOUR_USERNAME with your actual GitHub username!"