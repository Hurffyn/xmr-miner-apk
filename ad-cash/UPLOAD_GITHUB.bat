@echo off
echo ========================================
echo Upload para GitHub e Build Automatico
echo ========================================
echo.

set /p USERNAME="Digite seu username do GitHub: "

echo.
echo Configurando repositorio...
git remote remove origin 2>nul
git remote add origin https://github.com/%USERNAME%/xmr-miner.git

echo.
echo Fazendo push para GitHub...
git branch -M main
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo UPLOAD CONCLUIDO!
    echo ========================================
    echo.
    echo O GitHub Actions vai compilar o APK automaticamente
    echo.
    echo Acesse: https://github.com/%USERNAME%/xmr-miner/actions
    echo.
    echo Aguarde ~30 minutos e baixe o APK em "Artifacts"
    echo.
) else (
    echo.
    echo ========================================
    echo ERRO NO UPLOAD
    echo ========================================
    echo.
    echo Possiveis causas:
    echo 1. Repositorio nao existe no GitHub
    echo 2. Nao esta logado no Git
    echo.
    echo Solucoes:
    echo 1. Crie o repo em: https://github.com/new
    echo 2. Configure git: 
    echo    git config --global user.name "Seu Nome"
    echo    git config --global user.email "seu@email.com"
    echo.
)

pause
