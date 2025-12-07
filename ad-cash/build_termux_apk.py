#!/usr/bin/env python3
"""
Build APK with embedded Termux-like environment
Uses Python-for-Android with proot for Linux userspace
"""
import os
import sys
import shutil
from pathlib import Path

print("=" * 70)
print("XMR MINER - BUILD APK COM TERMUX EMBUTIDO")
print("=" * 70)

# Create enhanced buildozer.spec
spec_content = """[app]
title = XMR Miner Pro
package.name = xmrminer
package.domain = com.xmrminer
source.dir = ..
source.include_exts = py,png,jpg,kv,atlas,json,sh
source.include_patterns = assets/*,bin/android_arm64/*,core/*,android/*
entrypoint = android/main.py
version = 1.0.0

# Requirements with full Termux-like environment
requirements = python3,kivy,pexpect,psutil,requests,base58,pycryptodome,pynacl,numpy,sh

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK,ACCESS_NETWORK_STATE,FOREGROUND_SERVICE,REQUEST_INSTALL_PACKAGES

# Android settings
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.arch = arm64-v8a
python_version = 3.11
kivy_version = 2.2.0

# Services
services = MiningService:android/mining_service.py

# Additional features
android.gradle_dependencies = 
android.add_src = bin/android_arm64
presplash.color = #000000
orientation = portrait
fullscreen = 0

# Bootstrap with proot support
p4a.bootstrap = sdl2
p4a.branch = master

# Build options
android.logcat_filters = *:S python:D
android.release_artifact = apk
log_level = 2
warn_on_root = 1

[buildozer]
build_dir = ./.buildozer
bin_dir = ./bin
"""

android_dir = Path("android")
spec_file = android_dir / "buildozer_termux.spec"

print("\n[1/4] Criando buildozer.spec aprimorado...")
with open(spec_file, 'w') as f:
    f.write(spec_content)
print(f"✓ Criado: {spec_file}")

# Create enhanced main.py with shell access
main_enhanced = '''
import os
import subprocess
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import threading

kivy.require('2.1.0')

class ShellTerminal(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Title
        title = Label(
            text='XMR Miner Pro - Termux Mode',
            size_hint=(1, 0.1),
            font_size='20sp',
            color=(0, 1, 0, 1)
        )
        self.add_widget(title)
        
        # Terminal output
        scroll = ScrollView(size_hint=(1, 0.6))
        self.terminal_output = TextInput(
            text='$ Welcome to XMR Miner Terminal\\n$ Type commands below\\n\\n',
            readonly=True,
            background_color=(0, 0, 0, 1),
            foreground_color=(0, 1, 0, 1),
            font_name='RobotoMono-Regular',
            font_size='14sp'
        )
        scroll.add_widget(self.terminal_output)
        self.add_widget(scroll)
        
        # Command input
        self.cmd_input = TextInput(
            hint_text='Enter command...',
            multiline=False,
            size_hint=(1, 0.1)
        )
        self.cmd_input.bind(on_text_validate=self.run_command)
        self.add_widget(self.cmd_input)
        
        # Buttons
        btn_layout = BoxLayout(size_hint=(1, 0.2))
        
        start_btn = Button(text='Start Mining')
        start_btn.bind(on_press=self.start_mining)
        btn_layout.add_widget(start_btn)
        
        stop_btn = Button(text='Stop')
        stop_btn.bind(on_press=self.stop_mining)
        btn_layout.add_widget(stop_btn)
        
        shell_btn = Button(text='Shell')
        shell_btn.bind(on_press=lambda x: self.run_command(None, 'sh'))
        btn_layout.add_widget(shell_btn)
        
        self.add_widget(btn_layout)
        
        self.mining_proc = None
        
    def append_output(self, text):
        self.terminal_output.text += text + '\\n'
        self.terminal_output.cursor = (0, len(self.terminal_output.text))
        
    def run_command(self, instance, cmd=None):
        command = cmd if cmd else self.cmd_input.text
        if not command:
            return
            
        self.append_output(f'$ {command}')
        self.cmd_input.text = ''
        
        def execute():
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                output = result.stdout if result.stdout else result.stderr
                Clock.schedule_once(lambda dt: self.append_output(output))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.append_output(f'Error: {e}'))
        
        threading.Thread(target=execute, daemon=True).start()
    
    def start_mining(self, instance):
        self.append_output('Starting XMRig miner...')
        # Add actual mining logic here
        self.run_command(None, 'ps aux | grep python')
    
    def stop_mining(self, instance):
        self.append_output('Stopping miner...')
        if self.mining_proc:
            self.mining_proc.terminate()

class XMRMinerApp(App):
    def build(self):
        return ShellTerminal()

if __name__ == '__main__':
    XMRMinerApp().run()
'''

main_file = android_dir / "main_termux.py"
print("\n[2/4] Criando interface aprimorada...")
with open(main_file, 'w') as f:
    f.write(main_enhanced)
print(f"✓ Criado: {main_file}")

# Create build script
build_script = '''#!/bin/bash
set -e

echo "=========================================="
echo "BUILD APK COM TERMUX EMBUTIDO"
echo "=========================================="

cd android

# Install dependencies
pip install buildozer cython==0.29.36

# Clean previous builds
rm -rf .buildozer bin

# Build APK
buildozer -v android debug

echo ""
echo "=========================================="
echo "BUILD CONCLUÍDO!"
echo "=========================================="
echo "APK: android/bin/xmrminer-*.apk"
'''

build_sh = Path("build_termux_apk.sh")
print("\n[3/4] Criando script de build...")
with open(build_sh, 'w') as f:
    f.write(build_script)
os.chmod(build_sh, 0o755)
print(f"✓ Criado: {build_sh}")

print("\n[4/4] Verificando WSL...")
wsl_status = os.system("wsl --list >nul 2>&1")

if wsl_status != 0:
    print("\n⚠️  WSL não está pronto ainda.")
    print("\nPara fazer o build, escolha:")
    print("\n1. REINICIE O PC e execute:")
    print("   wsl")
    print(f"   cd /mnt/c/Users/abiin/Downloads/ad-cash-miner/ad-cash")
    print("   bash build_termux_apk.sh")
    print("\n2. OU use GitHub Actions (sem reiniciar):")
    print("   - Crie repo em https://github.com/new")
    print("   - git push para compilar na nuvem")
else:
    print("\n✓ WSL disponível!")
    print("\nExecutando build agora...")
    os.system(f"wsl bash -c 'cd /mnt/c/Users/abiin/Downloads/ad-cash-miner/ad-cash && bash {build_sh}'")

print("\n" + "=" * 70)
print("Setup completo!")
print("=" * 70)
