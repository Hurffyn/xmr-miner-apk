@echo off
echo ========================================
echo UPLOAD PARA GITHUB E BUILD AUTOMATICO
echo ========================================
echo.

echo [1/3] Criando repositorio no GitHub...
echo Abra: https://github.com/new
echo Nome: xmr-miner-termux
echo.
pause

echo.
echo [2/3] Fazendo push do codigo...
git add .
git commit -m "APK com Termux embutido - build automatico"
git push -u origin main

echo.
echo [3/3] Build iniciado!
echo Acesse: https://github.com/SEU_USUARIO/xmr-miner-termux/actions
echo.
echo O APK estara pronto em 10-15 minutos!
pause
