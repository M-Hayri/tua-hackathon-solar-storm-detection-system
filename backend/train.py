import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import autocast, GradScaler
import time

import os
from dataset import get_dataloaders
from model import SpaceWeatherNet

def train_model():
    # Model Parametreleri ve Veri Yolları
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TRAIN_PATH = os.path.join(BASE_DIR, "data", "processed", "train_data.pt")
    VAL_PATH = os.path.join(BASE_DIR, "data", "processed", "val_data.pt")
    
    BATCH_SIZE = 512
    EPOCHS = 5  # Demoluk 5 döngü belirliyoruz
    LEARNING_RATE = 1e-3
    SAVE_PATH = "best_model.pth"
    
    print("🚀 [TUA] Uzay Havası Derin Öğrenme Eğitimi Başlatılıyor...")
    
    # 1. Donanım (GPU/CUDA Cvd) Kontrolü
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"🖥️ Kullanılan Donanım: {device}")
    
    # 2. Tensor Veri Setlerini Yükleme Boru Hattı
    print("📦 Veri setleri (300 Bin Örnek) RAM/VRAM'e paketleniyor...")
    train_loader, val_loader = get_dataloaders(TRAIN_PATH, VAL_PATH, batch_size=BATCH_SIZE)
    print(f"✅ Bitti. Eğitim: {len(train_loader.dataset)} örnek | Doğrulama: {len(val_loader.dataset)} örnek.")
    
    # 3. Modeli ve Matematiksel Mimariyi Ayağa Kaldırma
    model = SpaceWeatherNet(input_features=5, sequence_length=60).to(device)
    
    # BCE (Binary Cross Entropy) + Logit : İkili sınıflandırma (0-1) için mükemmeldir.
    criterion = nn.BCEWithLogitsLoss() 
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4) # Adam'ın Regularized Süper Sürümü
    scaler = GradScaler() # Mixed Precision (GPU ise %50 Hız Kazandırır)
    
    best_val_loss = float('inf')
    
    # 4. Asıl Eğitim Döngüsü (Training Loop)
    for epoch in range(EPOCHS):
        start_time = time.time()
        
        # ---- TRAIN STEP (ZİHNİ EĞİTME) ----
        model.train()
        train_loss = 0.0
        correct_train = 0
        total_train = 0
        
        for batch_idx, (X_batch, y_batch) in enumerate(train_loader):
            # Batch'leri Hesaplama Ünitesine Taşı (CPU/GPU)
            X_batch, y_batch = X_batch.to(device), y_batch.to(device).unsqueeze(1)
            
            optimizer.zero_grad() # Ağırlıkları temizle
            
            # Autocast float16/float32 dinamik çevirme yapar
            with autocast():
                logits, attention_weights = model(X_batch)
                loss = criterion(logits, y_batch) # Modelin Tahmini ve Gerçek Veriyi Karşılaştır
                
            scaler.scale(loss).backward() # Geri Yayılım (Backpropagation)
            scaler.step(optimizer)        # Adım At (Gradient Descent)
            scaler.update()
            
            train_loss += loss.item() * X_batch.size(0)
            
            # Doğruluk (Accuracy) Hesaplaması
            preds = torch.sigmoid(logits) >= 0.5  # Logit'i 0-1 Sigmoid'e sıkıştırıp %50 sınıra bakıyoruz
            correct_train += (preds == y_batch).sum().item()
            total_train += y_batch.size(0)
            
            if batch_idx % 200 == 0 and batch_idx > 0:
                print(f"   Epoch [{epoch+1}/{EPOCHS}] | Batch {batch_idx}/{len(train_loader)} | Anlık Kayıp: {loss.item():.4f}")
                
        avg_train_loss = train_loss / len(train_loader.dataset)
        train_acc = correct_train / total_train
        
        # ---- VALIDATION STEP (ZİHNİ SINAMA & DOĞRULAMA) ----
        model.eval() # Öğrenmeyi Durdur
        val_loss = 0.0
        correct_val = 0
        total_val = 0
        
        with torch.no_grad(): # Gradient takip etme (Hızlandırır)
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device).unsqueeze(1)
                
                with autocast():
                    logits, _ = model(X_batch)
                    loss = criterion(logits, y_batch)
                    
                val_loss += loss.item() * X_batch.size(0)
                preds = torch.sigmoid(logits) >= 0.5
                correct_val += (preds == y_batch).sum().item()
                total_val += y_batch.size(0)
                
        avg_val_loss = val_loss / len(val_loader.dataset)
        val_acc = correct_val / total_val
        
        elapsed = time.time() - start_time
        
        print("==" * 30)
        print(f"🎯 Epoch {epoch+1}/{EPOCHS} Tamamlandı! (Süre: {elapsed:.1f}s)")
        print(f"   Eğitim (Train) -> Loss: {avg_train_loss:.4f} | Başarım: %{train_acc*100:.2f}")
        print(f"   Deneme (Val)   -> Loss: {avg_val_loss:.4f} | Başarım: %{val_acc*100:.2f}")
        
        # Modeli Diske Kaydetme (Checkpointing)
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), SAVE_PATH)
            print(f"   💾 🔥 Puan Yükseldi: Yeni En İyi Agırlık Dosyası Kaydedildi -> {SAVE_PATH}")
            print("==" * 30)
            
    print("\n✅ TUA YZ Eğitimi Başarıyla Sonlandı! Hazırız!")

if __name__ == "__main__":
    train_model()
