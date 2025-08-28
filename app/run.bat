@echo off
echo  FastAPI başlatılıyor...
start http://127.0.0.1:8000/docs
uvicorn app.main:app --reload
pause