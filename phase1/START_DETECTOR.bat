@echo off
title Helmet and Safety Vest Detector
cd /d "%~dp0"
py -3 helmet_vest_detector.py
if errorlevel 1 (
  echo.
  echo Setup or detector failed. Read the error above.
  pause
)
