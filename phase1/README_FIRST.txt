HELMET + SAFETY VEST DETECTOR — EASY WINDOWS SETUP

1. Install Python 3.10, 3.11, or 3.12 from https://www.python.org/downloads/windows/
   During installation, enable "Add Python to PATH".
2. Install Git for Windows from https://git-scm.com/download/win
   (needed to fetch the CLIP dependency from its source).
3. Extract this folder.
4. Double-click START_DETECTOR.bat.
5. First run downloads Python packages and pretrained model weights. It can take
   several minutes and requires internet access and disk space.
6. Press Q or ESC in the video window to quit.

The installer uses a project-local .venv, so it does not attempt to modify
C:\Program Files\Python... or require administrator permission.

To use a video instead of webcam, open Command Prompt in this folder and run:
  .venv\Scripts\python.exe helmet_vest_detector.py --source "C:\path\to\video.mp4"

Note: YOLO-World's prompt-based detection is approximate. This is a demo, not a
validated safety system. A PPE-specific trained model may be needed for reliable
helmet/vest detection.
