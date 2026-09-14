#!/bin/bash
# Setup script for Smart Workplace Safety Intelligence Platform

echo "Setting up Smart Workplace Safety Intelligence Platform..."

python3 -m venv venv
source venv/bin/activate

echo "Installing backend requirements..."
# pip install -r requirements.txt (assuming requirements exist)
pip install ultralytics fastapi uvicorn python-multipart pydantic psutil albumentations opencv-python

echo "Downloading default model..."
python3 scripts/download_model.py

echo "Creating necessary directories..."
mkdir -p data/uploads data/db ml/models

if [ ! -f .env ]; then
    echo "Copying .env.example to .env..."
    touch .env # mock fallback
fi

echo "Setup Complete! Run the application using docker-compose or uvicorn directly."
