@echo off
echo ========================================
echo XMR Miner - Build APK Automatico
echo ========================================
echo.

echo [1/3] Verificando WSL...
wsl --list >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: WSL nao instalado corretamente
    echo Reinicie o PC e execute este script novamente
    pause
    exit /b 1
)

echo WSL OK!
echo.

echo [2/3] Iniciando build do APK...
echo Isso pode levar 30-60 minutos na primeira vez
echo.

wsl bash -c "cd /mnt/c/Users/abiin/Downloads/ad-cash-miner/ad-cash && bash build_android.sh"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo BUILD CONCLUIDO COM SUCESSO!
    echo ========================================
    echo.
    echo APK localizado em:
    echo android\bin\xmrminer-debug.apk
    echo.
    echo Transfira para seu Android e instale!
    echo.
) else (
    echo.
    echo ========================================
    echo ERRO NO BUILD
    echo ========================================
    echo.
    echo Verifique os logs acima
    echo.
)

pause
