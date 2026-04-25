import torch
from torch.utils.data import Dataset, DataLoader

class SpaceWeatherDataset(Dataset):
    def __init__(self, data_path: str):
        """
        Loads the pre-processed PyTorch tensor dataset.
        Format expected: dict with keys 'X' (shape: [N, Seq_Len, Features])
        and 'y' (shape: [N]).
        """
        data = torch.load(data_path)
        # Verileri bellekte uygun formata (float32) dönüştürüyoruz
        self.X = data['X'].float()
        self.y = data['y'].float()
        
        assert len(self.X) == len(self.y), "KOBİ Hatası: Girdi (X) ve Hedef (y) örnekleme boyutları eşleşmiyor!"

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def get_dataloaders(train_path, val_path, batch_size=256):
    """
    Eğitim ve Doğrulama tensorlerini, GPU/CPU'ya 'Batch' paketleri halinde
    atacak PyTorch boru hatlarını (DataLoader) döndürür.
    """
    train_dataset = SpaceWeatherDataset(train_path)
    val_dataset = SpaceWeatherDataset(val_path)
    
    # Shuffle=True ile verinin karışmasını (Overfitting'i engelleyecek şekilde) sağlıyoruz.
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader
