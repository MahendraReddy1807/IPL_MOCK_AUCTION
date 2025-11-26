#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Initialize database
python init_db.py

# Seed with player data
python seed_data.py
