import random
import time
import math
import os

try:
    import torch
    from model import SpaceWeatherNet
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class SpaceWeatherInferenceEngine:
    def __init__(self):
        self.base_prob = 0.5
        self.time_step = 0
        self.model_path = "best_model.pth"
        self.use_real_model = False
        self.dl_model = None
        
        if TORCH_AVAILABLE and os.path.exists(self.model_path):
            self.use_real_model = True
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.dl_model = SpaceWeatherNet(input_features=5, sequence_length=60)
            self.dl_model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.dl_model.to(self.device)
            self.dl_model.eval()
            
        self.protocols = [
            "[SATELLITE_CMD] Kritik LEO uyduları güvenli moda alındı.",
            "[GRID_CMD] EHV trafo koruması (GIC bloklama) devrede.",
            "[AVIATION_CMD] Kutup uçuşları (Polar Route) reroute ediliyor.",
            "[COMM_CMD] HF Telsiz iletişiminde yedek frekanslara geçildi.",
            "[SUBMARINE_CMD] Denizaltı fiber optik voltaj dengelemesi başlatıldı.",
            "[AI_SYS] CaaM çekirdeği anomali çözümlemesi tamamlandı."
        ]

    def _get_probability(self):
        if self.use_real_model:
            with torch.no_grad():
                dummy_input = torch.randn(1, 60, 5).to(self.device)
                logits, _ = self.dl_model(dummy_input)
                prob = torch.sigmoid(logits).item()
            return prob
        else:
            self.time_step += 1
            wave = math.sin(self.time_step * 0.1) * 0.3
            noise = (random.random() - 0.5) * 0.1
            new_prob = self.base_prob + wave + noise
            self.base_prob = (self.base_prob * 0.8) + (new_prob * 0.2)
            self.base_prob = max(0.01, min(0.99, self.base_prob))
            return self.base_prob

    def infer(self):
        prob = self._get_probability()
        
        # Frontend API Contract
        probability_percentage = round(prob * 100, 1)
        
        # Olasılık > 45 ise (TSS eşiği) KIRMIZI
        if probability_percentage > 45.0:
            alert_level = "KIRMIZI ALARM"
        elif probability_percentage > 25.0:
            alert_level = "SARI ALARM"
        else:
            alert_level = "GÜVENLİ"
            
        eta_hours = max(2, int((1.0 - prob) * 48))
        eta_str = f"{eta_hours} Saat" if probability_percentage > 15.0 else "Tehdit Yok"
        
        # Dinamik etki barları
        impact_areas = [
            {"name": "Kutup Uçuşları", "risk": min(100, max(0, int(probability_percentage * 1.2 + random.randint(-5, 5))))},
            {"name": "Elektrik Şebekesi (EHV)", "risk": min(100, max(0, int(probability_percentage * 1.0 + random.randint(-10, 10))))},
            {"name": "LEO Uyduları", "risk": min(100, max(0, int(probability_percentage * 1.4 + random.randint(-5, 5))))},
            {"name": "Denizaltı Fiberleri", "risk": min(100, max(0, int(probability_percentage * 0.8 + random.randint(-5, 5))))},
        ]
        
        active_protocols = []
        if probability_percentage > 35.0:
            num_protocols = random.randint(1, 4)
            active_protocols = random.sample(self.protocols, num_protocols)
        else:
            active_protocols = ["[SYS_CMD] Tüm sistemler izlemede (Nominal)."]
            
        return {
            "target_region": "AR 13590",
            "probability": probability_percentage,
            "alert_level": alert_level,
            "eta": eta_str,
            "impact_areas": impact_areas,
            "active_protocols": active_protocols
        }
