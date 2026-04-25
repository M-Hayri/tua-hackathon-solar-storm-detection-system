document.addEventListener('DOMContentLoaded', () => {

    /******************************************
     * 1. MAP (GIS) LAYERS - LEAFLET
     ******************************************/
    const mapTabs = document.querySelectorAll('.map-tab');
    
    // Initialize Map
    const gisMap = L.map('gis-map', {
        zoomControl: false,
        attributionControl: false,
        zoomSnap: 0.1, // Esnek (küsuratlı) yakınlaştırmaya izin ver
        maxBounds: [ // Harita sınırlarını sabitle
            [-90, -180],
            [90, 180]
        ],
        maxBoundsViscosity: 1.0
    });

    // Haritanın arkasındaki yüklenmeyen 'beyaz/gri' Leaflet boşluğunu karanlık (uzay) rengi yap
    document.getElementById('gis-map').style.background = '#090d13';

    // Dark Matter Tiles (CartoDB)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd',
        maxZoom: 20,
        noWrap: true // Tekrarlamayı engelle
    }).addTo(gisMap);

    // Otomatik olarak haritayı container'ın BOYUTUNA tam sıfıra-sıfır oturt
    // Böylece beyazlık kalmaz ve Amerika tamamen içeride olur
    gisMap.fitBounds([
        [-60, -140], // Güney Amerika altı, Pasifik
        [70, 140]    // Kuzey Kutbu, Rusya Doğusu
    ]);

    // Haritanın boyutu tam yüklenmesi için yeniden boyutlandır
    setTimeout(() => {
        gisMap.invalidateSize();
    }, 500);

    // Layer Groups
    const aviationLayer = L.layerGroup();
    const submarineLayer = L.layerGroup();
    const leoLayer = L.layerGroup();

    // Özel İkonlar
    const alertIcon = L.divIcon({ className: 'map-node warning', iconSize: [8,8] });
    const safeIcon = L.divIcon({ className: 'map-node', iconSize: [6,6] });

    // ==========================================
    // 1. HAVACILIK (KUTUP VE KÜRESEL UÇUŞ ROTALARI)
    // ==========================================
    // Gerçeğe yakın yoğun uçuş koridorları (Kuzey Atlantik, Pasifik, Avrupa-Asya)
    const flightRoutes = [
        [[40.6, -73.7], [55.0, -40.0], [51.4, -0.4]], // JFK - LHR
        [[40.6, -73.7], [65.0, -20.0], [48.8, 2.5]],  // JFK - CDG
        [[33.9, -118.4], [55.0, -100.0], [35.6, 139.7]], // LAX - HND
        [[37.6, -122.3], [60.0, -150.0], [31.1, 121.7]], // SFO - PVG
        [[51.4, -0.4], [60.0, 50.0], [25.2, 55.3]], // LHR - DXB
        [[25.2, 55.3], [10.0, 90.0], [1.3, 103.9]], // DXB - SIN
        [[43.6, -79.6], [70.0, -50.0], [55.7, 37.6]], // YYZ - SVO (Kutup Rotası)
        [[47.4, -122.3], [80.0, -120.0], [50.0, 8.5]], // SEA - FRA (Polar Route)
        [[35.6, 139.7], [75.0, 150.0], [40.6, -73.7]], // HND - JFK (Kutup Geçişi)
    ];

    flightRoutes.forEach((route, idx) => {
        let isDangerous = (route[1][0] > 60 || route[1][0] < -60); // 60 enlem üstü riskli
        let color = isDangerous ? '#ff7b72' : '#58a6ff'; // Kutup rotaları kırmızı
        L.polyline(route, {color: color, weight: 2, dashArray: '4, 6', opacity: 0.6}).addTo(aviationLayer);
        
        // Ara noktalara (Waypoints) marker ekle
        L.marker(route[1], {icon: isDangerous ? alertIcon : safeIcon}).addTo(aviationLayer)
         .bindPopup(`Uçuş Koridoru ${idx+1}<br>Durum: ${isDangerous ? 'RADYASYON RİSKİ (HF İPTAL)' : 'NOMİNAL'}`);
    });

    // Rastgele küresel uçuş noktaları (Yoğunluk hissi için) 
    for(let i=0; i<40; i++) {
        let lat = (Math.random() * 120) - 60;
        let lng = (Math.random() * 360) - 180;
        L.marker([lat, lng], {icon: safeIcon}).addTo(aviationLayer);
    }

    // ==========================================
    // 2. DENİZALTI FİBER KABLOLARI (Küresel İnternet Omurgası)
    // ==========================================
    // Marea, TAT-14, Apollo gibi gerçeğe yakın yoğun kablo rotaları
    const cableRoutes = [
        [[40.1, -74.0], [42.0, -40.0], [47.5, -3.0], [50.8, 1.5]], // Trans-Atlantic N
        [[36.8, -76.0], [38.0, -40.0], [38.7, -9.1], [43.3, 5.3]], // Trans-Atlantic S (Marea benzeri)
        [[33.8, -118.4], [25.0, -140.0], [21.3, -157.9], [13.4, 144.7], [35.0, 140.0]], // Pasifik
        [[1.3, 103.9], [5.0, 80.0], [18.9, 72.8], [12.8, 45.0], [25.2, 55.2]], // SEA-ME-WE
        [[-33.8, 151.2], [-20.0, 160.0], [21.3, -157.9], [34.0, -118.0]], // Southern Cross
        [[-22.9, -43.1], [10.0, -30.0], [38.7, -9.1]], // Atlantis-2 (Brezilya - Avrupa)
        [[50.0, -5.0], [60.0, -20.0], [64.1, -21.9], [40.0, -70.0]] // Northern Route
    ];

    cableRoutes.forEach((route, idx) => {
        let hasGIC = idx % 2 === 0; // Kabloların yarısı GIC (Jeomanyetik) riskinde
        L.polyline(route, {color: hasGIC ? '#ff7b72' : '#d29922', weight: 3, opacity: 0.8}).addTo(submarineLayer);
        // Landing noktalarına (karaya çıkış) marker
        L.marker(route[route.length-1], {icon: hasGIC ? alertIcon : safeIcon}).addTo(submarineLayer)
         .bindPopup(`Fiber İniş İstasyonu<br>Durum: ${hasGIC ? 'GIC VOLTAJ DALGALANMASI TESPİT EDİLDİ' : 'NOMİNAL GÜÇ'}`);
    });

    // ==========================================
    // 3. LEO UYDULARI (STARLINK, ONEWEB MEGA İSTASYONLARI)
    // ==========================================
    // Küresel çapta yüzlerce ufak yörünge iz düşümü (Swarm/Küme simülasyonu)
    for(let i=0; i<150; i++) {
        let lat = (Math.random() * 160) - 80; // Kutuplara daha yakın olanlar riskli
        let lng = (Math.random() * 360) - 180;
        
        let isCritical = (Math.abs(lat) > 55); // Kutuplardaki uydular (Radyasyon / Sürüklenme)
        let color = isCritical ? '#ff7b72' : (Math.random() > 0.7 ? '#d29922' : '#3fb950');
        let radius = 200000 + (Math.random() * 400000); // 200-600 km yarıçapında yansıma alanları

        L.circle([lat, lng], {
            color: color,
            fillColor: color,
            fillOpacity: 0.15,
            weight: 1,
            radius: radius
        }).addTo(leoLayer).bindPopup(`Uydu Kümesi #${i+1000}<br>Yörünge Yüksekliği: 550km<br>Durum: ${isCritical ? 'ATMOSFERİK SÜRÜKLENME (DRAG) RİSKİ' : 'GÜVENLİ'}`);
    }

    // Başlangıç Katmanı
    let activeLayerGroup = aviationLayer;
    activeLayerGroup.addTo(gisMap);

    // Sekmeler Arası Geçiş Dinamiği
    mapTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            mapTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            gisMap.removeLayer(activeLayerGroup); // Eski katmanı sil
            
            if(tab.dataset.layer === 'aviation') activeLayerGroup = aviationLayer;
            // Html'deki dataset isimleriyle eşleştir
            if(tab.dataset.layer === 'submarine') activeLayerGroup = submarineLayer;
            if(tab.dataset.layer === 'leo') activeLayerGroup = leoLayer;
            
            activeLayerGroup.addTo(gisMap); // Yeni katmanı yükle
        });
    });


    /******************************************
     * 2. WARGAMING DEĞİŞKENLERİ VE ANİMASYON
     ******************************************/
    const wargameBtn = document.getElementById('wargame-toggle');
    const econLoss = document.getElementById('econ-loss-val');
    const ertVal = document.getElementById('ert-val');
    
    let isWargame = false;
    let econLossInterval, ertInterval, flowchartInterval;
    let currentLoss = 120.5; // billions
    let countdownSec = 14400; // 4 hours

    wargameBtn.addEventListener('click', () => {
        isWargame = !isWargame;
        if(isWargame) {
            document.body.classList.add('wargame-mode');
            wargameBtn.innerText = "Simülasyon Aktif (Çıkış Yap)";
            startWargameSimulation();
        } else {
            document.body.classList.remove('wargame-mode');
            wargameBtn.innerText = "Simülasyon / Tatbikat Modu";
            stopWargameSimulation();
        }
    });

    function startWargameSimulation() {
        econLossInterval = setInterval(() => {
            currentLoss += (Math.random() * 2);
            econLoss.innerText = `$${currentLoss.toFixed(2)} Milyar`;
        }, 1500);

        ertInterval = setInterval(() => {
            countdownSec -= 1;
            const h = Math.floor(countdownSec / 3600);
            const m = Math.floor((countdownSec % 3600) / 60);
            const s = countdownSec % 60;
            ertVal.innerText = `T-Minus ${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
        }, 1000);

        let step = 1;
        flowchartInterval = setInterval(() => {
            document.querySelectorAll('.flow-step').forEach(s => s.classList.remove('active'));
            document.getElementById(`step-${step}`).classList.add('active');
            step = step >= 4 ? 1 : step + 1;
        }, 2000);
    }

    function stopWargameSimulation() {
        clearInterval(econLossInterval);
        clearInterval(ertInterval);
        clearInterval(flowchartInterval);
    }


    /******************************************
     * 3. AI MOTORU POLİNG VE DOM GÜNCELLEME
     ******************************************/
    const API_URL = 'http://127.0.0.1:8000/api/status';
    const IMAGE_BASE_URL = 'http://127.0.0.1:8000/static/current_heatmap.png';
    
    const bannerBox = document.getElementById('banner-box');
    const levelText = document.getElementById('api-threat-level');
    const aiProb = document.getElementById('api-ai-prob');
    const heatmapImg = document.getElementById('heatmap_img');
    const terminalOutput = document.getElementById('terminal_output');
    const healthContainer = document.getElementById('health-container');

    let knownLogs = new Set();

    setInterval(fetchData, 2000);
    fetchData();

    async function fetchData() {
        try {
            const res = await fetch(API_URL);
            if (!res.ok) return;
            const data = await res.json();
            
            // a) Image Update (Cache Bust)
            heatmapImg.src = `${IMAGE_BASE_URL}?t=${Date.now()}`;
            
            // b) TCN & Alert Level
            levelText.innerText = data.alert_level;
            aiProb.innerText = `%${data.probability.toFixed(1)}`;

            if (data.alert_level === 'KIRMIZI ALARM') {
                levelText.style.color = 'var(--accent-red)';
                bannerBox.classList.add('red-alert-bg');
            } else if (data.alert_level === 'SARI ALARM') {
                levelText.style.color = 'var(--accent-yellow)';
                bannerBox.classList.remove('red-alert-bg');
            } else {
                levelText.style.color = 'var(--text-neon)';
                bannerBox.classList.remove('red-alert-bg');
            }

            // c) Terminal Otonom Protokoller
            data.active_protocols.forEach(log => {
                if(!knownLogs.has(log)) {
                    knownLogs.add(log);
                    typeWriterTerminal(log);
                }
            });

            // d) Health Bars (Mevcut 'impact_areas' kullanılıyor, tersine HTML çizimi)
            healthContainer.innerHTML = '';
            data.impact_areas.forEach(item => {
                // Risk 100 ise Health 0'dır
                const health = 100 - item.risk; 
                let colorClass = 'green';
                let statusText = 'SAĞLAM (NOMİNAL)';
                let bgCol = '#3fb950';

                if (health < 40) { colorClass = 'red'; statusText = 'KRİTİK (HASAR BEKLENİYOR)'; bgCol = '#ff7b72'; }
                else if (health < 70) { colorClass = 'yellow'; statusText = 'RİSKLİ (DALGALANMA TESPİTİ)'; bgCol = '#d29922'; }

                const barWidth = Math.max(health, 5); // Güvenli bar genişliği

                const html = `
                <div class="health-item">
                    <div class="health-label">
                        <span>${item.name}</span>
                        <span class="status-badge ${colorClass}">${statusText} - Sağlık %${health}</span>
                    </div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width: ${barWidth}%; background-color: ${bgCol};"></div>
                    </div>
                </div>
                `;
                healthContainer.insertAdjacentHTML('beforeend', html);
            });

        } catch (e) {
            console.error("Localhost API Çalışmıyor:", e);
        }
    }

    // Terminal Typewriter Effect
    function typeWriterTerminal(text) {
        const p = document.createElement('div');
        p.className = 'log-line active'; // Neon yeşil
        p.style.whiteSpace = "pre-wrap"; // Wrap text
        terminalOutput.appendChild(p);
        
        // Remove active class from old logs
        Array.from(terminalOutput.children).forEach(child => {
            if (child !== p) child.classList.remove('active');
        });

        // Scroll
        terminalOutput.scrollTop = terminalOutput.scrollHeight;

        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                p.innerHTML += text.charAt(i);
                i++;
                terminalOutput.scrollTop = terminalOutput.scrollHeight;
            } else {
                clearInterval(interval);
            }
        }, 15);
    }
});
