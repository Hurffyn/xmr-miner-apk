import os
import threading
import subprocess
import time
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import config
from core.pool_selector import pick_best_pool_sync
from core.watchdog import build_xmrig_cmd
from core.ai_neural import get_optimizer, TrainingSample
from core.platform_sensors import PlatformMonitor
from core.balance_tracker import BalanceTracker
from core.wallet_storage import wallet_exists, load_wallet, save_wallet
from core.wallet_gen import generate_wallet
import psutil

kivy.require('2.1.0')


class MinerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Wallet input
        self.wallet_input = TextInput(
            hint_text='Wallet Address',
            multiline=False,
            size_hint=(1, 0.15),
        )
        
        # Load or generate wallet
        if wallet_exists():
            saved = load_wallet()
            if saved and 'address' in saved:
                self.wallet_input.text = saved['address']
            else:
                self.wallet_input.text = '87e3o1i9eoZPGSpKMYNVg5644DF6GmifaAHtkPW1MAD5LuryxR9CpErg57Q5gbpn36EqAaJHC2f1Z1a7cjGsPvgLRumZVAc'
        else:
            # Auto-generate wallet
            wallet_data = generate_wallet()
            save_wallet(wallet_data)
            self.wallet_input.text = wallet_data['address']
        
        self.add_widget(self.wallet_input)
        
        # Balance display
        self.balance_label = Label(
            text='Balance: 0.00000000 XMR\nHashrate: 0.00 H/s',
            font_size='18sp',
            size_hint=(1, 0.25),
            color=(0, 1, 0, 1)
        )
        self.add_widget(self.balance_label)
        
        # Status
        self.status = Label(text='Idle', size_hint=(1, 0.15), color=(0.5, 0.5, 0.5, 1))
        self.add_widget(self.status)
        
        # Control button
        self.btn = Button(text='Start Mining', size_hint=(1, 0.2), font_size='16sp')
        self.btn.bind(on_press=self.toggle)
        self.add_widget(self.btn)
        
        # System info
        monitor = PlatformMonitor()
        state = monitor.get_state()
        info = f"CPU: {os.cpu_count()} cores"
        if state['cpu_temp']:
            info += f" | {state['cpu_temp']:.1f}°C"
        if state['battery_level']:
            info += f" | Battery: {state['battery_level']}%"
        self.info_label = Label(text=info, size_hint=(1, 0.15), color=(0, 0, 1, 1))
        self.add_widget(self.info_label)
        
        self.proc = None
        self.mining_thread = None
        self.stop_event = threading.Event()
        self.balance_tracker = None
        self.platform_monitor = PlatformMonitor()
        self.ai_optimizer = get_optimizer()

    def start(self):
        wallet = self.wallet_input.text.strip()
        if not wallet:
            self.status.text = 'Error: Enter wallet address'
            return
        
        host, port, latency = pick_best_pool_sync()
        
        # Get current state
        state = self.platform_monitor.get_state()
        
        # AI suggests optimal threads
        threads = self.ai_optimizer.suggest_optimal_threads({
            'threads': os.cpu_count() or 1,
            'cpu_temp': state['cpu_temp'],
            'cpu_usage': state['cpu_usage'],
            'throttled': state['is_throttling'],
            'latency_ms': latency * 1000.0,
            'battery_level': state['battery_level'],
        }, os.cpu_count() or 1)
        
        bin_path = os.path.abspath(config.XMRIG_BIN_ANDROID)
        cmd = build_xmrig_cmd(bin_path, wallet, host, port, threads)
        
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     universal_newlines=True, bufsize=1)
        
        self.balance_tracker = BalanceTracker(host, wallet)
        self.status.text = f'Mining: {threads}T @ {host}:{port}'
        
        # Monitor loop
        def monitor():
            while not self.stop_event.is_set() and self.proc and self.proc.poll() is None:
                try:
                    line = self.proc.stdout.readline()
                    if line:
                        self.balance_tracker.parse_xmrig_output(line)
                    
                    # Update UI via Clock (thread-safe)
                    def update_ui(dt):
                        pool_balance = self.balance_tracker.get_pool_balance()
                        hashrate = self.balance_tracker.get_hashrate()
                        
                        if pool_balance is not None:
                            self.balance_label.text = f'Balance: {pool_balance:.8f} XMR\nHashrate: {hashrate:.2f} H/s'
                        else:
                            self.balance_label.text = f'Balance: querying...\nHashrate: {hashrate:.2f} H/s'
                    
                    Clock.schedule_once(update_ui, 0)
                    
                    # Feed data to AI
                    state = self.platform_monitor.get_state()
                    sample = TrainingSample(
                        current_threads=threads,
                        cpu_temp=state['cpu_temp'] or 50.0,
                        cpu_usage=state['cpu_usage'],
                        throttled=1 if state['is_throttling'] else 0,
                        latency_ms=latency * 1000.0,
                        battery_level=state['battery_level'] or 100,
                        hashrate=self.balance_tracker.get_hashrate(),
                        accepts=self.balance_tracker.shares_accepted,
                        rejects=self.balance_tracker.shares_rejected,
                    )
                    self.ai_optimizer.add_sample(sample)
                    
                    # Auto-pause on thermal/battery
                    if state['should_reduce']:
                        Clock.schedule_once(lambda dt: self.status.text.__setattr__('text', '⚠️ Paused: thermal/battery'), 0)
                        self.stop()
                        break
                    
                    time.sleep(5)
                except Exception as e:
                    print(f"Monitor error: {e}")
                    break
        
        self.mining_thread = threading.Thread(target=monitor, daemon=True)
        self.mining_thread.start()

    def stop(self):
        self.stop_event.set()
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None
        self.status.text = 'Idle'

    def toggle(self, _):
        if self.proc is None:
            self.stop_event.clear()
            threading.Thread(target=self.start, daemon=True).start()
            self.btn.text = 'Pause Mining'
        else:
            self.stop()
            self.btn.text = 'Start Mining'


class MinerApp(App):
    def build(self):
        return MinerUI()


if __name__ == '__main__':
    MinerApp().run()
