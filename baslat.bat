@echo off
TITLE TUA Uzay Havasi Komuta Merkezi
:: Proje klasorunu calisma alani olarak belirle
cd /d "%~dp0"

echo ===================================================
echo  TUA UZAY HAVASI OTONOM KOMUTA SISTEMI BASLATILIYOR
echo ===================================================
echo.

:: 1. Gerekli statik dosyalari hazirla (Gunes fotografi sorunu icin)
echo [1/4] Gerekli dosyalar hazirlaniyor...
if not exist "static" mkdir static
copy /Y "solar.png" "static\current_heatmap.png" > nul

:: 2. Yapay Zeka / Backend Sunucusunu Baslat
echo [2/4] Yapay Zeka Motoru (Backend) Baslatiliyor...
:: Yeni bir terminal penceresinde baslatir (Kapatmasi kolay olsun diye)
start "TUA AI Backend (Port 8000)" cmd /k "python backend\main.py"

:: 3. Arayuz / Frontend Sunucusunu Baslat
echo [3/4] Web Sunucusu (Frontend) Baslatiliyor...
start "TUA Web Frontend (Port 8080)" cmd /k "python -m http.server 8080"

:: Sunucularin ayaga kalkmasi icin 3 saniye bekle
echo Sunucularin ayaga kalkmasi bekleniyor...
timeout /t 3 /nobreak > nul

:: 4. Kullanicinin tarayicisi uzerinden sistemi ac
echo [4/4] Komuta Paneli Tarayicida Aciliyor...
start http://localhost:8080/

echo.
echo ===================================================
echo                 SISTEM AKTIF!                      
echo ===================================================
echo Eger sistemi durdurmak isterseniz, arka planda acilan
echo "TUA AI Backend" ve "TUA Web Frontend" isimli siyah 
echo terminal pencerelerini carpilarindan kapatabilirsiniz.
echo ===================================================

