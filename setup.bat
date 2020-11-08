pyinstaller magyka.spec -y
rd /Q/S build
ROBOCOPY /E data dist/magyka/data
rd /Q/S dist\magyka\lib2to3
rd /Q/S dist\magyka\Include
rm magyka.zip
"C:\Program Files\7-Zip\7z" a magyka.zip dist/magyka
rd /Q/S dist