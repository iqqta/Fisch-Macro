# 🎣 Fisch Macro

**Fisch Macro** adalah script Python otomatisasi untuk mendeteksi dan mengontrol aksi "reeling" pada game *Fisch* di Roblox.  
Program ini menggunakan *computer vision* (OpenCV) untuk mendeteksi bar visual di layar dan melakukan klik/drag otomatis menggunakan PyAutoGUI.

---

## 🧩 Fitur Utama

- 🔍 Deteksi bar *reeling* secara real-time dari tangkapan layar.
- 🖱️ Klik otomatis berdasarkan posisi bar.
- 🪟 GUI interaktif berbasis **Tkinter** (dapat disesuaikan area tangkapannya).
- 📏 Overlay transparan untuk mengatur area deteksi hit box reel dengan drag & drop.

---

## ⚙️ Persyaratan Sistem

- macOS atau Windows 
- Python **3.9+**
- Game Roblox dalam mode jendela (*windowed mode*)

---

## 📦 Instalasi

1. **Clone atau download repository ini:**
    ```bash
    git clone https://github.com/iqqta/FischMacro.git
    cd FischMacro

2. **Install semua dependency:**
    ```bash
    pip install -r requirements.txt

3. **Aksesibilitas**
    ```bash
    Nyalakan akses terminal di
    Privacy & Scurity -> Aksesibilitas
    Privacy & Scurity -> Screen & System Audio Recording
    
5. **Jalankan**
    ```bash
    python3 macro.py

