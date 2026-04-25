import torch
import torch.nn as nn

class SpaceWeatherNet(nn.Module):
    def __init__(self, input_features=5, sequence_length=60, d_model=64, n_heads=4):
        """
        TCN (Temporal Convolutional Network) + Causal Multi-Head Attention Sınıflandırma Ağı
        """
        super(SpaceWeatherNet, self).__init__()
        
        # 1. TCN (Temporal Convolutional Network) Blokları
        # Giriş boyutu Conv1d'de: (Batch, Channels/Features, Length) olmalıdır.
        self.tcn_block = nn.Sequential(
            nn.Conv1d(in_channels=input_features, out_channels=32, kernel_size=3, padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),
            
            nn.Conv1d(in_channels=32, out_channels=d_model, kernel_size=3, padding=1),
            nn.BatchNorm1d(d_model),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        
        # Boyut Küçülmesi: Orijinal uzunluk 60 -> MaxPool_1 (30) -> MaxPool_2 (15)
        self.reduced_seq_len = sequence_length // 4  
        
        # 2. CaaM Modülü (Causal Attention)
        # Sinyallerin içindeki gizli "nedensel ilişkilere" odaklanmak için Attention kullanıyoruz.
        self.attention = nn.MultiheadAttention(embed_dim=d_model, num_heads=n_heads, batch_first=True, dropout=0.2)
        
        # 3. İkili Sınıflandırma Karar Katmanı (Classifier)
        self.classifier = nn.Sequential(
            nn.Linear(d_model * self.reduced_seq_len, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 1)  # Son çıktı: 1 node (Güneş Fırtınası Olacak mı? Sigmoid veya Logit)
        )
        
    def forward(self, x):
        # x şekli (Veri Setinden Gelen): [Batch, Sequence=60, Features=5]
        # Ancak Conv1d uzaysal boyutu 2. endekste ister: [Batch, Features, Sequence]
        x = x.transpose(1, 2)  
        
        # TCN Çıkarımı ---> Zaman Serilerindeki Fiziksel Zıplamaları yakalar (Örn: X-Ray Patlamaları)
        tcn_out = self.tcn_block(x)  # Çıktı Shape'i: [Batch, d_model=64, Seq=15]
        
        # Attention Algoritması için Formata Geri Çevirme ---> [Batch, Seq=15, d_model=64]
        tcn_out = tcn_out.transpose(1, 2)
        
        # CaaM Mantığı (Multi-Head Attention) ile Hangi Zamana Daha 'Dikkat' Edileceğine Karar Verme
        attn_out, attn_weights = self.attention(query=tcn_out, key=tcn_out, value=tcn_out)
        
        # Lineer sinir katmanına atmak için düzleştirme
        flattened = attn_out.reshape(attn_out.size(0), -1)  # [Batch, 15 * 64]
        
        # Karar Mekanizması
        logits = self.classifier(flattened) # [Batch, 1] Çıktı (Logit olarak çıkar, Sigmoid Eğitimde hesaplanacak)
        
        return logits, attn_weights
