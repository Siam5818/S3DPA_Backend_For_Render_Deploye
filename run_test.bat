@echo off
cd /d "C:\laragon\www\S3DPA_Backend"
python -m pytest tests/test_pipeline.py -v
pause
