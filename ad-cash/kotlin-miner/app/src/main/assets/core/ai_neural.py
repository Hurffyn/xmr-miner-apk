"""
Neural network auto-tuner for mining optimization.
Uses lightweight MLP to predict optimal thread count based on system metrics.
Trains continuously in background.
"""
import numpy as np
import pickle
import os
import threading
import time
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TrainingSample:
    # Input features
    current_threads: int
    cpu_temp: float
    cpu_usage: float
    throttled: int  # 0 or 1
    latency_ms: float
    battery_level: int
    
    # Output (reward)
    hashrate: float
    accepts: int
    rejects: int


class SimpleNeuralOptimizer:
    """
    Lightweight MLP for thread optimization.
    Input: [threads, temp, usage, throttled, latency, battery]
    Output: predicted hashrate
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.path.expanduser('~/.xmrminer/ai_model.pkl')
        self.samples: List[TrainingSample] = []
        self.max_samples = 1000
        
        # Simple weights (input_features + bias -> hidden -> output)
        self.input_size = 6
        self.hidden_size = 12
        self.output_size = 1
        
        # Initialize random weights
        np.random.seed(42)
        self.W1 = np.random.randn(self.input_size, self.hidden_size) * 0.1
        self.b1 = np.zeros(self.hidden_size)
        self.W2 = np.random.randn(self.hidden_size, self.output_size) * 0.1
        self.b2 = np.zeros(self.output_size)
        
        self.learning_rate = 0.001
        self.training_lock = threading.Lock()
        self.load_model()
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        return (x > 0).astype(float)
    
    def forward(self, X):
        """Forward pass."""
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.relu(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        return self.z2
    
    def backward(self, X, y, output):
        """Backward pass (gradient descent)."""
        m = X.shape[0]
        
        # Output layer gradient
        dz2 = output - y
        dW2 = np.dot(self.a1.T, dz2) / m
        db2 = np.sum(dz2, axis=0) / m
        
        # Hidden layer gradient
        da1 = np.dot(dz2, self.W2.T)
        dz1 = da1 * self.relu_derivative(self.z1)
        dW1 = np.dot(X.T, dz1) / m
        db1 = np.sum(dz1, axis=0) / m
        
        # Update weights
        self.W1 -= self.learning_rate * dW1
        self.b1 -= self.learning_rate * db1
        self.W2 -= self.learning_rate * dW2
        self.b2 -= self.learning_rate * db2
    
    def train_step(self):
        """Single training iteration on collected samples."""
        if len(self.samples) < 10:
            return
        
        with self.training_lock:
            # Convert samples to numpy arrays
            X = np.array([[
                s.current_threads,
                s.cpu_temp if s.cpu_temp else 50.0,
                s.cpu_usage,
                float(s.throttled),
                s.latency_ms,
                s.battery_level if s.battery_level else 100.0
            ] for s in self.samples])
            
            # Normalize inputs
            X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
            
            # Target: hashrate (normalized)
            y = np.array([[s.hashrate] for s in self.samples])
            y = (y - y.mean()) / (y.std() + 1e-8)
            
            # Forward + backward pass
            output = self.forward(X)
            self.backward(X, y, output)
    
    def predict_hashrate(self, threads: int, temp: float, usage: float, 
                        throttled: bool, latency: float, battery: int) -> float:
        """Predict hashrate for given configuration."""
        X = np.array([[
            threads,
            temp if temp else 50.0,
            usage,
            1.0 if throttled else 0.0,
            latency,
            battery if battery else 100.0
        ]])
        
        # Normalize (use same scale as training - simplified)
        with self.training_lock:
            if len(self.samples) > 0:
                train_X = np.array([[
                    s.current_threads, s.cpu_temp or 50, s.cpu_usage,
                    float(s.throttled), s.latency_ms, s.battery_level or 100
                ] for s in self.samples])
                mean = train_X.mean(axis=0)
                std = train_X.std(axis=0) + 1e-8
                X = (X - mean) / std
        
        return float(self.forward(X)[0, 0])
    
    def add_sample(self, sample: TrainingSample):
        """Add training sample."""
        with self.training_lock:
            self.samples.append(sample)
            if len(self.samples) > self.max_samples:
                self.samples.pop(0)
    
    def suggest_optimal_threads(self, current_state: dict, max_threads: int) -> int:
        """
        Suggest optimal thread count by trying different values.
        """
        temp = current_state.get('cpu_temp', 50.0)
        throttled = current_state.get('throttled', False)
        battery = current_state.get('battery_level', 100)

        if len(self.samples) < 5:
            # Prefer full load; back off only if clearly thermal/battery constrained
            if throttled or temp > 85 or (battery and battery < 20):
                return max(1, max_threads - 1)
            return max_threads
        
        best_threads = current_state.get('threads', max_threads)
        best_score = -float('inf')
        
        usage = current_state.get('cpu_usage', 0.5)
        latency = current_state.get('latency_ms', 50.0)
        
        # Try different thread counts
        for t in range(1, max_threads + 1):
            score = self.predict_hashrate(t, temp, usage, throttled, latency, battery)
            
            # Penalty for thermal issues
            if temp > 80:
                score -= (temp - 80) * 0.1
            
            # Penalty for battery drain on mobile
            if battery and battery < 30:
                score -= (30 - battery) * 0.05
            
            if score > best_score:
                best_score = score
                best_threads = t
        
        return max(1, best_threads)
    
    def save_model(self):
        """Persist model to disk."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'W1': self.W1,
                    'b1': self.b1,
                    'W2': self.W2,
                    'b2': self.b2,
                    'samples': self.samples[-100:]  # Keep recent samples only
                }, f)
        except Exception as e:
            print(f"Model save failed: {e}")
    
    def load_model(self):
        """Load model from disk."""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.W1 = data['W1']
                    self.b1 = data['b1']
                    self.W2 = data['W2']
                    self.b2 = data['b2']
                    self.samples = data.get('samples', [])
        except Exception as e:
            print(f"Model load failed: {e}")
    
    def train_loop(self, interval: int = 60):
        """Background training loop."""
        while True:
            time.sleep(interval)
            self.train_step()
            if len(self.samples) % 50 == 0:
                self.save_model()


# Global optimizer instance
_optimizer = None


def get_optimizer() -> SimpleNeuralOptimizer:
    global _optimizer
    if _optimizer is None:
        _optimizer = SimpleNeuralOptimizer()
        # Start background training
        t = threading.Thread(target=_optimizer.train_loop, daemon=True)
        t.start()
    return _optimizer
