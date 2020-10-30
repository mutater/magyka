pyinstaller magyka.spec --noconfirm --clean --distpath . --icon icon.ico
rd /Q/S build
ROBOCOPY /E data magyka\data
ROBOCOPY . magyka libmpg123-0.dll
"C:\Program Files\7-Zip\7z" a magyka.zip magyka
rd /Q/S magyka