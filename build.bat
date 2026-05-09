@echo off
echo Compilando GeradorSQL_Protheus...
echo.
pyinstaller --onefile --windowed --clean --name "GeradorSQL_Protheus" main.py
echo.
echo Concluido!
echo Executavel gerado em: dist\GeradorSQL_Protheus.exe
echo.
pause
