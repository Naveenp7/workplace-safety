@echo off
REM Setup script for Smart Workplace Safety Intelligence Platform

echo Setting up Smart Workplace Safety Intelligence Platform...

python -m venv venv
call venv\Scripts\activate

echo Installing backend requirements...
pip install ultralytics fastapi uvicorn python-multipart pydantic psutil albumentations opencv-python

echo Downloading default model...
python scripts\download_model.py

echo Creating necessary directories...
if not exist "data\uploads" mkdir data\uploads
if not exist "data\db" mkdir data\db
if not exist "ml\models" mkdir ml\models

if not exist .env (
    echo Copying .env.example to .env...
    type nul > .env
)

echo Setup Complete! Run the application using docker-compose or uvicorn directly.
