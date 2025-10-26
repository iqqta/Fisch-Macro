# 🎣 Fisch Macro

**Fisch Macro** adalah script Python otomatisasi untuk mendeteksi dan mengontrol aksi "reeling" pada game *Fisch* di Roblox.  
Program ini menggunakan *computer vision* (OpenCV) untuk mendeteksi bar visual di layar dan melakukan reel otomatis menggunakan PyAutoGUI.

---
## 🖼️ Tampilan Aplikasi

Berikut tampilan GUI dari **Fisch Macro** saat dijalankan di macOS:

![Tampilan Fisch Macro](assets/screenshot.png)

## 🧩 Fitur Utama

- 🔍 Deteksi bar *reeling* secara real-time dari tangkapan layar.
- 🖱️ Reel otomatis berdasarkan posisi bar.
- 🪟 GUI interaktif berbasis **Tkinter** (dapat disesuaikan area tangkapannya).
- 📏 Overlay transparan untuk mengatur area deteksi hit box reel dengan drag & resize.

---

## ⚙️ Persyaratan Sistem

- macOS atau Windows 
- Python **3.9+**
- Game Roblox & Macro dalam mode jendela (*windowed mode bukan full screen/split screen*)

---

## 📦 Instalasi

1. **Download atau clone repository ini:**
    ```bash
    git clone https://github.com/iqqta/FischMacro.git
    cd FischMacro

2. **Install semua dependency:**
    ```bash
    pip3 install opencv-python pyautogui numpy pillow

3. **Aksesibilitas (Mac OS)**
    ```bash
    Nyalakan akses terminal di
    Privacy & Scurity -> Aksesibilitas
    Privacy & Scurity -> Screen & System Audio Recording
    
5. **Jalankan**
    ```bash
    python3 macro.py

