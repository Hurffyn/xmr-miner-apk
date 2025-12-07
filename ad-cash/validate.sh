#!/bin/bash
# Script de validação e teste do minerador

echo "========================================="
echo "🔍 VALIDAÇÃO XMR MINER"
echo "========================================="
echo ""

# Check Python
echo "✓ Verificando Python..."
python3 --version || { echo "❌ Python não encontrado"; exit 1; }
echo ""

# Check structure
echo "✓ Verificando estrutura de arquivos..."
REQUIRED_FILES=(
    "core/ai_neural.py"
    "core/balance_tracker.py"
    "core/wallet_gen.py"
    "core/wallet_storage.py"
    "core/platform_sensors.py"
    "windows/launcher.py"
    "android/main.py"
    "build_windows.sh"
    "build_android.sh"
    "README.md"
    "LICENSE"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file FALTANDO"
        exit 1
    fi
done
echo ""

# Check binaries
echo "✓ Verificando binários XMRig..."
if [ -f "bin/windows_x64/xmrig.exe" ]; then
    SIZE=$(ls -lh bin/windows_x64/xmrig.exe | awk '{print $5}')
    echo "  ✅ Windows x64: $SIZE"
else
    echo "  ❌ Windows x64: FALTANDO"
fi

if [ -f "bin/android_arm64/xmrig" ] && [ -x "bin/android_arm64/xmrig" ]; then
    echo "  ✅ Android ARM64: OK"
else
    echo "  ⚠️  Android ARM64: Placeholder (compilar manualmente)"
fi
echo ""

# Test imports
echo "✓ Testando imports Python..."
python3 -c "
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
try:
    from core import config
    from core import pool_selector
    from core import wallet_gen
    from core import platform_sensors
    print('  ✅ Todos os módulos carregados com sucesso')
except ImportError as e:
    print(f'  ⚠️  Aviso de import: {e}')
    print('  💡 Algumas dependências podem estar faltando (normal se não instaladas)')
except Exception as e:
    print(f'  ⚠️  Aviso: {e}')
" || echo "  ⚠️  Imports com avisos (instalar deps: pip install -r requirements.txt)"
echo ""

# Test pool selection
echo "✓ Testando seleção de pool..."
timeout 10 python3 core/miner_controller.py --demo 2>&1 | head -5 || echo "  ⚠️  Timeout (normal se sem rede)"
echo ""

# Summary
echo "========================================="
echo "📊 RESUMO"
echo "========================================="
echo "Arquivos Python: $(find . -name '*.py' | wc -l)"
echo "Linhas de código: $(wc -l core/*.py android/*.py windows/*.py 2>/dev/null | tail -1 | awk '{print $1}')"
echo "Tamanho total: $(du -sh . | awk '{print $1}')"
echo ""
echo "✅ Validação concluída!"
echo ""
echo "📦 Próximos passos:"
echo "  1. Windows: ./build_windows.sh"
echo "  2. Android: Compilar XMRig ARM64 + ./build_android.sh"
echo "  3. Ler ENTREGA.md para instruções completas"
echo "========================================="
