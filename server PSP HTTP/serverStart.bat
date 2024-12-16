@echo off
rem Запуск HTTP-сервера
set PORT=8080
set DIRECTORY=./www
python server.py %PORT% %DIRECTORY%
pause
