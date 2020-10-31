rd /Q/S build
ROBOCOPY /E data magyka\data
ROBOCOPY /E venv magyka\venv
ROBOCOPY . magyka Magyka.py
ROBOCOPY . magyka run.bat
ROBOCOPY . magyka README.txt
"C:\Program Files\7-Zip\7z" a magyka.zip magyka
rd /Q/S magyka