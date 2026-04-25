# TUA Uzay Havası Otonom Komuta Sistemi (Space Weather Command Center)

Bu proje, güneşte meydana gelen aktiviteleri analiz ederek, uzay havası olaylarının (örneğin; jeomanyetik fırtınalar, radyasyon fırtınaları vb.) Dünya üzerindeki kritik altyapılara (Elektrik şebekeleri, Kutup uçuşları, LEO Uyduları, Denizaltı Siber Fiber Ağları vb.) olası etkilerini derin öğrenme (PyTorch) tabanlı bir Yapay Zeka ile tahmin edip aksiyon almak üzerine kurulmuş tam otonom bir komuta kontrol sistemidir.

## 🚀 Özellikler

- **Yapay Zeka Destekli Tahmin Motoru:** Gelen vektörel verileri kullanarak uzay havasındaki anormallikleri modelleyen derin öğrenme (`PyTorch`) mimarisi.
- **Gerçek Zamanlı Veri Akışı:** Gelişmiş `FastAPI` tabanlı backend mimarisi ile her şey asenkron ve gerçek zamanlı işlenir.
- **Modüler Wargaming Arayüzü:** Özel olarak tasarlanmış, karanlık mod (dark-mode) destekli, Leaflet GIS destekli gerçek zamanlı komuta ekranı.
- **Otonom Protokol Yönetimi:** Olası bir felaket durumunda kritik altyapılara gönderilecek talimatların sistem tarafından otomatik hesaplanması.
- **Kolay Başlangıç:** Windows kullanıcıları için tek tıkla çalışabilme imkanı sunan otomasyon scripti.

## 📁 Proje Yapısı

```
TUA/
│
├── backend/
│   ├── main.py            # FastAPI Sunucusu ve API Katmanı
│   ├── ai_engine.py       # Pytorch AI Inferencing ve Mantık Motoru
│   ├── model.py           # Space Weather PyTorch Model Mimarisi
│   ├── train.py           # Model Eğitim Scripti (Model Training)
│   └── dataset.py         # PyTorch Veri seti (Dataset/DataLoader) Yönetimi
│
├── data/
│   └── processed/         # İşlenmiş Tensor (.pt) veri setleriniz (Git'te yoksayılır)
│
├── static/                # Arayüz İmage / GradCAM Heatmap çıktıları 
│
├── script.js              # Wargaming tarzı Dinamik Web Uygulaması ve Leaflet etkileşimi
├── styles.css             # Sayfa biçimlendirmesi ve modern UI animasyonları
├── index.html             # Komuta Kontrol ekranı Ana Sayfası
├── baslat.bat             # Tek Tıkla Kurulum / Çalıştırma Scripti
├── requirements.txt       # Python Kütüphane Bağımlılıkları
└── README.md              # Proje belgeleri
```

## 🛠️ Kurulum

1. **Repoyu Klonlayın:**
   ```bash
   git clone <REPO_URL>
   cd TUA
   ```

2. **Sanal Ortamı Oluşturun ve Aktifleştirin:**
   ```bash
   python -m venv .venv
   # Windows için:
   .venv\Scripts\activate
   # macOS/Linux için:
   source .venv/bin/activate
   ```

3. **Gerekli Bağımlılıkları Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♂️ Sistemi Çalıştırma

Projenizi çalıştırmanın **iki farklı yolu** vardır:

### Birinci Yöntem (Hızlı)
Windows sistemlerde, projenin kök klasöründeki `baslat.bat` dosyasına **çift tıklayarak** hem AI Backend (8000) hem de Frontend Sunucusunu (8080) aynı anda başlatabilirsiniz. Tarayıcınız komuta merkezini otomatik olarak açacaktır.

### İkinci Yöntem (Manuel - Geliştiriciler İçin)
1. **API Sunucusunu (Backend) Başlatın:**
   ```bash
   python backend/main.py
   ```
   *FastAPI sunucumuz 127.0.0.1:8000 portunda hizmet vermeye başlayacaktır.*

2. **Önyüz (Frontend) Sunucusunu Başlatın:**
   Yeni bir terminal açın ve:
   ```bash
   python -m http.server 8080
   ```
   *Ardından tarayıcınızda `http://localhost:8080` adresine giderek Arayüz'ü görüntüleyebilirsiniz.*

## 🧠 Model Eğitimi (Opsiyonel)

Eğer kendi verisetleriniz ile (.pt torch tensörleri formatında) modeli tekrar baştan eğitmek veya ince ayar (finetuning) yapmak isterseniz:

```bash
python backend/train.py
```
*Model başarılı bir şekilde eğitildiğinde `best_model.pth` isimli ağırlık (weight) dosyası otomatik oluşturulup kaydedilecektir.*

## 👥 Katkıda Bulunma
Projeyi geliştirmek isterseniz pull request'lerinize açığız! Lütfen büyük değişiklikler yapmadan önce bir konu (issue) açarak fikrinizi tartışmaya sunun.

## ⚖️ Lisans
Bu proje [MIT Lisansı](LICENSE) kapsamında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasını inceleyin.
