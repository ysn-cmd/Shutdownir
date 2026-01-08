import requests
import json
import os
import time
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QFileDialog, QTextEdit, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
import sys

STEAM_API_KEY = "YOUR_STEAM_API_KEY_HERE"

# --- Steam API: Get game install directory from Steam library ---
def get_steam_game_path(app_id):
    steam_path = r"C:/Program Files (x86)/Steam/steamapps/libraryfolders.vdf"
    try:
        with open(steam_path, 'r', encoding='utf-8') as f:
            data = f.read()
    except FileNotFoundError:
        return None

    library_paths = []
    for line in data.splitlines():
        if "path" in line:
            parts = line.split("\"")
            if len(parts) > 3:
                library_paths.append(parts[3])

    for lib in library_paths:
        game_path = f"{lib}/steamapps/common"
        return game_path

    return None

# -------------------- Folder Watcher Thread --------------------
class FolderWatcher(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, folder_path, shutdown_seconds=10):
        super().__init__()
        self.folder_path = folder_path
        self.shutdown_seconds = shutdown_seconds
        self.running = True

    def get_folder_size(self, path):
        total = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except:
                    pass
        return total

    def run(self):
        last_size = self.get_folder_size(self.folder_path)
        self.log_signal.emit(f"Başlangıç boyutu: {last_size / (1024**2):.2f} MB")

        while self.running:
            time.sleep(15 * 60)  # 15 dakika
            new_size = self.get_folder_size(self.folder_path)
            self.log_signal.emit(f"Güncel boyut: {new_size / (1024**2):.2f} MB")

            if new_size == last_size:
                self.log_signal.emit("İndirme durmuş görünüyor! Bilgisayar kapatılıyor...")
                subprocess.run(["shutdown", "/s", "/t", str(self.shutdown_seconds)])
                break
            else:
                self.log_signal.emit("İndirme devam ediyor...")
                last_size = new_size

# -------------------- PyQt6 GUI --------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Auto Shutdown")
        self.setGeometry(200, 200, 400, 300)

        self.label = QLabel("Steam Game ID:")
        self.game_id_input = QLineEdit()

        self.folder_label = QLabel("Manual Folder Path:")
        self.folder_input = QLineEdit()
        self.folder_btn = QPushButton("Select Folder")
        self.folder_btn.clicked.connect(self.select_folder)

        self.steam_btn = QPushButton("Find Automatically from Steam")
        self.start_btn = QPushButton("Start Monitoring")
        self.start_btn.clicked.connect(self.start_monitoring)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.game_id_input)
        layout.addWidget(self.folder_label)
        layout.addWidget(self.folder_input)
        layout.addWidget(self.folder_btn)
        layout.addWidget(self.steam_btn)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.log_box)
        self.setLayout(layout)

        # Tray
        self.tray = QSystemTrayIcon(QIcon(), parent=self)
        self.tray.setToolTip("Game Auto Shutdown Running")
        self.menu = QMenu()
        show_action = self.menu.addAction("Show")
        exit_action = self.menu.addAction("Exit")
        show_action.triggered.connect(self.show_window)
        exit_action.triggered.connect(self.exit_app)
        self.tray.setContextMenu(self.menu)
        self.tray.show()

        self.watcher = None

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)

    def show_window(self):
        self.show()
        self.setWindowState(Qt.WindowState.WindowActive)

    def exit_app(self):
        if self.watcher:
            self.watcher.running = False
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def start_monitoring(self):
        folder = self.folder_input.text()
        if not folder:
            self.log_box.append("Önce klasör yolu seçmelisin!")
            return

        self.watcher = FolderWatcher(folder)
        self.watcher.log_signal.connect(self.log_box.append)
        self.watcher.start()
        self.log_box.append("Monitoring başlatıldı.")

# -------------------- App Runner --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
