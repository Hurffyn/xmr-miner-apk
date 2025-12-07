import threading
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import platform
import time

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

miner_proc = None
miner_thread = None
monitor_thread = None
stop_event = threading.Event()
balance_tracker = None
platform_monitor = PlatformMonitor()
ai_optimizer = get_optimizer()
log_widget = None


def log_message(message: str):
    """Add message to log widget if available."""
    global log_widget
    if log_widget:
        log_widget.config(state='normal')
        log_widget.insert(tk.END, message + '\n')
        log_widget.see(tk.END)
        log_widget.config(state='disabled')


def start_miner(wallet: str, balance_label: tk.Label, status_label: tk.Label):
    global miner_proc, balance_tracker
    try:
        log_message("=== Starting miner ===")
        log_message("Selecting best pool...")
        
        host, port, latency = pick_best_pool_sync()
        log_message(f"Selected pool: {host}:{port} (latency: {latency*1000:.0f}ms)")
        
        log_message("Collecting platform state...")
        state = platform_monitor.get_state()
        log_message(f"State: temp={state['cpu_temp']}, usage={state['cpu_usage']:.2f}, throttling={state['is_throttling']}")
        
        # AI suggests optimal threads
        threads = ai_optimizer.suggest_optimal_threads({
            'threads': os.cpu_count() or 1,
            'cpu_temp': state['cpu_temp'],
            'cpu_usage': state['cpu_usage'],
            'throttled': state['is_throttling'],
            'latency_ms': latency * 1000.0,
            'battery_level': state['battery_level'],
        }, os.cpu_count() or 1)
        
        log_message(f"Using {threads} threads")
        
        # Determine binary path - when frozen, use sys._MEIPASS
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            base_path = sys._MEIPASS
            bin_path = os.path.join(base_path, config.XMRIG_BIN_WINDOWS if platform.system().lower().startswith("win") else config.XMRIG_BIN_ANDROID)
        else:
            # Running as script
            bin_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", config.XMRIG_BIN_WINDOWS if platform.system().lower().startswith("win") else config.XMRIG_BIN_ANDROID))
        
        log_message(f"XMRig binary: {bin_path}")
        
        if not os.path.exists(bin_path):
            log_message(f"ERROR: XMRig binary not found at {bin_path}")
            status_label.config(text="Error: XMRig binary not found")
            return
        
        cmd = build_xmrig_cmd(bin_path, wallet, host, port, threads)
        log_message(f"Command: {' '.join(cmd)}")
        
        miner_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                       universal_newlines=True, bufsize=1)
        log_message(f"Process started with PID: {miner_proc.pid}")
        
        balance_tracker = BalanceTracker(host, wallet)
        status_label.config(text=f"Mining: {threads} threads @ {host}:{port}")
    except Exception as e:
        log_message(f"ERROR during start: {e}")
        status_label.config(text=f"Error: {e}")
        return
    
    # Monitor loop
    def monitor():
        update_counter = 0
        log_message("Monitor thread started")
        while not stop_event.is_set() and miner_proc and miner_proc.poll() is None:
            try:
                line = miner_proc.stdout.readline()
                if line:
                    line_stripped = line.strip()
                    if line_stripped:  # Only log non-empty lines
                        print(line_stripped)  # Debug: print XMRig output
                        log_message(line_stripped)  # Show in GUI
                        balance_tracker.parse_xmrig_output(line)
                
                # Update display every 2 iterations
                update_counter += 1
                if update_counter >= 2:
                    update_counter = 0
                    hashrate = balance_tracker.get_hashrate()
                    pool_balance = balance_tracker.get_pool_balance()
                    
                    if pool_balance is not None:
                        balance_label.config(text=f"Balance: {pool_balance:.8f} XMR\nHashrate: {hashrate:.2f} H/s")
                    else:
                        balance_label.config(text=f"Balance: querying...\nHashrate: {hashrate:.2f} H/s")
                    
                    # Feed data to AI
                    state = platform_monitor.get_state()
                    sample = TrainingSample(
                        current_threads=threads,
                        cpu_temp=state['cpu_temp'] or 50.0,
                        cpu_usage=state['cpu_usage'],
                        throttled=1 if state['is_throttling'] else 0,
                        latency_ms=latency * 1000.0,
                        battery_level=state['battery_level'] or 100,
                        hashrate=hashrate,
                        accepts=balance_tracker.shares_accepted,
                        rejects=balance_tracker.shares_rejected,
                    )
                    ai_optimizer.add_sample(sample)
                    
                    # Auto-adjust if overheating
                    if state['should_reduce']:
                        status_label.config(text="⚠️ Thermal/Battery limit - reducing load")
                        stop_miner()
                        time.sleep(30)
                        if not stop_event.is_set():
                            start_miner(wallet, balance_label, status_label)
                        break
                
                time.sleep(1)
            except Exception as e:
                log_message(f"Monitor error: {e}")
                print(f"Monitor error: {e}")
                break
        
        log_message("Monitor thread ended")
        if miner_proc:
            exit_code = miner_proc.poll()
            if exit_code is not None:
                log_message(f"Process exited with code: {exit_code}")
    
    global monitor_thread
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()


def stop_miner():
    global miner_proc
    stop_event.set()
    if miner_proc and miner_proc.poll() is None:
        log_message("Stopping miner...")
        miner_proc.terminate()
        try:
            miner_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            miner_proc.kill()
    miner_proc = None
    log_message("Miner stopped")


def toggle(btn, wallet_entry, balance_label, status_label):
    global miner_thread
    if miner_proc is None:
        wallet = wallet_entry.get().strip()
        if not wallet:
            messagebox.showerror("Wallet required", "Enter a Monero wallet address")
            return
        stop_event.clear()
        miner_thread = threading.Thread(target=start_miner, args=(wallet, balance_label, status_label), daemon=True)
        miner_thread.start()
        btn.config(text="Pause")
def main():
    global log_widget
    
    # Check/generate wallet
    if not wallet_exists():
        result = messagebox.askyesno("Generate Wallet", 
                                     "No wallet found. Generate new Monero wallet?")
        if result:
            wallet_data = generate_wallet()
            save_wallet(wallet_data)
            messagebox.showinfo("Wallet Created", 
                               f"Address: {wallet_data['address']}\n\n"
                               f"IMPORTANT: Backup your keys!\n"
                               f"Spend key: {wallet_data['spend_key']}\n"
                               f"View key: {wallet_data['view_key']}")
    
    root = tk.Tk()
    root.title("XMR Miner - AI Optimized")
    root.geometry("700x600")
    
    # Main frame (top 70%)
    main_frame = tk.Frame(root)
    main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Wallet input
    tk.Label(main_frame, text="Wallet Address:").pack(pady=5)
    wallet_entry = tk.Entry(main_frame, width=70)
    wallet_entry.pack(padx=10, pady=5)
    
    # Load saved wallet or use default
    saved = load_wallet()
    if saved and 'address' in saved:
        wallet_entry.insert(0, saved['address'])
    else:
        wallet_entry.insert(0, "87e3o1i9eoZPGSpKMYNVg5644DF6GmifaAHtkPW1MAD5LuryxR9CpErg57Q5gbpn36EqAaJHC2f1Z1a7cjGsPvgLRumZVAc")
    
    # Balance display
    balance_label = tk.Label(main_frame, text="Balance: 0.00000000 XMR\nHashrate: 0.00 H/s", 
                            font=("Arial", 14, "bold"), fg="green")
    balance_label.pack(pady=15)
    
    # Status
    status_label = tk.Label(main_frame, text="Idle", fg="gray")
    status_label.pack(pady=5)
    
    # Control button
    btn = tk.Button(main_frame, text="Start", font=("Arial", 12), 
                   command=lambda: toggle(btn, wallet_entry, balance_label, status_label))
    btn.pack(pady=10)
    
    # System info
    state = platform_monitor.get_state()
    info = f"CPU: {os.cpu_count()} cores"
    if state['cpu_temp']:
        info += f" | Temp: {state['cpu_temp']:.1f}°C"
    if state['battery_level']:
        info += f" | Battery: {state['battery_level']}%"
    tk.Label(main_frame, text=info, fg="blue").pack(pady=5)
    
    # Log frame (bottom 30%)
    log_frame = tk.Frame(root, bg="lightgray")
    log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, padx=10, pady=10)
    
    tk.Label(log_frame, text="Logs:", bg="lightgray", font=("Arial", 10, "bold")).pack(anchor=tk.W)
    
    log_widget = scrolledtext.ScrolledText(log_frame, height=10, bg="black", fg="lime", 
                                           font=("Consolas", 9), state='disabled')
    log_widget.pack(fill=tk.BOTH, expand=True)
    
    log_message("XMR Miner initialized")
    log_message(f"System: {os.cpu_count()} CPU cores detected")
    info = f"CPU: {os.cpu_count()} cores"
    if state['cpu_temp']:
        info += f" | Temp: {state['cpu_temp']:.1f}°C"
    if state['battery_level']:
        info += f" | Battery: {state['battery_level']}%"
    tk.Label(root, text=info, fg="blue").pack(pady=5)
    
    root.mainloop()


if __name__ == "__main__":
    main()
