# XMR Miner - Guia Completo de Build APK

## ✅ Status Atual
- [x] Código-fonte pronto
- [x] Dependências Python instaladas
- [x] Git repository inicializado
- [x] GitHub Actions workflow configurado

## 🚀 OPÇÃO RECOMENDADA: GitHub Actions (100% Automático)

### Passo 1: Criar Repositório GitHub
1. Acesse: https://github.com/new
2. Nome do repositório: `xmr-miner`
3. Descrição: `Monero miner with AI optimization`
4. Escolha: **Public** ou **Private** (sua preferência)
5. **NÃO** marque "Initialize with README"
6. Clique em "Create repository"

### Passo 2: Upload do Código
No PowerShell (nesta pasta):

```powershell
cd C:\Users\abiin\Downloads\ad-cash-miner\ad-cash
git remote add origin https://github.com/SEU_USUARIO/xmr-miner.git
git branch -M main
git push -u origin main
```

**Substitua `SEU_USUARIO` pelo seu username do GitHub!**

### Passo 3: Aguardar Build
1. Vá para: `https://github.com/SEU_USUARIO/xmr-miner/actions`
2. Verá um workflow "Build Android APK" rodando
3. Aguarde ~30-40 minutos (primeira vez)
4. Quando terminar (✅ verde), clique no workflow
5. Role até "Artifacts" e baixe `xmr-miner-apk`

### Passo 4: Instalar APK
1. Extraia o ZIP baixado
2. Transfira o arquivo `.apk` para seu Android
3. No Android: Configurações → Segurança → Permitir fontes desconhecidas
4. Abra o APK e instale

---

## 🐧 OPÇÃO 2: WSL (Build Local)

### Instalar WSL
```powershell
wsl --install -d Ubuntu-22.04
```

**Reinicie o PC após instalação!**

### Build no WSL
Após reiniciar, abra PowerShell e execute:

```bash
wsl
cd /mnt/c/Users/abiin/Downloads/ad-cash-miner/ad-cash
bash build_android.sh
```

APK estará em: `android/bin/xmrminer-*.apk`

---

## 🐳 OPÇÃO 3: Docker Desktop

### Instalar Docker
1. Baixe: https://www.docker.com/products/docker-desktop
2. Instale e reinicie
3. Abra Docker Desktop e aguarde iniciar

### Build com Docker
```powershell
cd C:\Users\abiin\Downloads\ad-cash-miner\ad-cash\android
docker run --rm -v ${PWD}:/app kivy/buildozer android debug
```

APK estará em: `bin/xmrminer-*.apk`

---

## 📱 Após Instalar o APK

### Primeira Execução
1. Abra o app "XMR Miner"
2. O app irá gerar uma carteira automaticamente
3. **IMPORTANTE**: Anote o endereço da carteira e as chaves!
4. Clique em "Start Mining"

### Verificar Mineração
- Hashrate aparece em poucos minutos
- Balance demora algumas horas (depende do pool)
- Para ver detalhes: vá ao site do pool com seu endereço

### Pools Configuradas
O app rotaciona automaticamente entre pools:
- MoneroOcean
- SupportXMR
- NanoPool
- 2Miners
- HashVault
- C3Pool

---

## ❓ Problemas Comuns

### "Permission denied" no WSL
```bash
chmod +x build_android.sh
bash build_android.sh
```

### "XMRig binary not found"
O aviso é normal. O APK será gerado sem o binário.
Para adicionar o XMRig:
1. No Android, instale Termux
2. No Termux: `pkg install xmrig`
3. Configure o app para usar o XMRig do Termux

### Build muito lento
- Primeira vez: 30-60 min (baixa SDK/NDK)
- Builds seguintes: 5-10 min
- GitHub Actions: Sempre rápido (servidores potentes)

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do GitHub Actions
2. Para WSL: execute `bash build_android.sh 2>&1 | tee build.log`
3. Envie o arquivo `build.log` para análise

---

## 🎯 Próximos Passos Recomendados

1. ✅ Use GitHub Actions (mais fácil)
2. ✅ Baixe o APK quando terminar
3. ✅ Instale no Android
4. ✅ Anote sua carteira!
5. ✅ Comece a minerar

**Boa mineração! 🚀**
