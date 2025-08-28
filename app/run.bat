@echo off
echo  FastAPI başlatılıyor...
<<<<<<< HEAD
start http://127.0.0.1:8000/docs
uvicorn app.main:app --reload
pause
=======
start "" http://127.0.0.1:8000/docs
uvicorn main:app --reload
pause
>>>>>>> a068dcbac92a302219ae94740e3a23b6b68bd7e9
