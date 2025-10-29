# app.py
import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QListWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFrame, QStatusBar
)

from proxy import MusicServiceCacheProxy  # ← import actualizado

# =========================
#   Worker en hilo (usa Qt)
# =========================
class FetchSongWorker(QThread):
    finished = pyqtSignal(str, str)  # data, source
    error = pyqtSignal(str)

    def __init__(self, proxy: MusicServiceCacheProxy, song_name: str):
        super().__init__()
        self.proxy = proxy
        self.song_name = song_name

    def run(self):
        try:
            data, source = self.proxy.get_song_with_source(self.song_name)
            self.finished.emit(data, source)
        except Exception as e:
            self.error.emit(str(e))

# =========================
#   Estilos y UI principal
# =========================
BOOTSTRAPISH_QSS = """
/* Paleta inspirada en Bootstrap 5 */
* { font-family: Inter, "Segoe UI", Roboto, Arial; }
/* Lista */
QListWidget {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    outline: none;
    padding: 6px;
    color: #111827;               /* 👈 asegura texto oscuro en items no seleccionados */
}
QListWidget::item {
    padding: 8px 10px;
    border-radius: 8px;
    color: #111827;               /* 👈 redundante pero explícito */
}
QListWidget::item:selected {
    background: #e7f1ff;
    color: #0d6efd;               /* 👈 color de texto al seleccionar */
}

/* Contenedor tipo card */
QFrame#card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
}

/* Lista */
QListWidget {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    outline: none;
    padding: 6px;
}
QListWidget::item {
    padding: 8px 10px;
    border-radius: 8px;
}
QListWidget::item:selected {
    background: #e7f1ff;
    color: #0d6efd;
}

/* Botones */
QPushButton {
    border: 1px solid transparent;
    padding: 8px 14px;
    border-radius: 10px;
    font-weight: 600;
}
QPushButton[class="primary"] { background: #0d6efd; color: white; }
QPushButton[class="primary"]:hover { background: #0b5ed7; }
QPushButton[class="secondary"] { background: #6c757d; color: white; }
QPushButton[class="secondary"]:hover { background: #5c636a; }
QPushButton:disabled { background: #cbd5e1; color: #ffffff; border-color: #cbd5e1; }

/* Badges */
QLabel[badge="true"][variant="success"],
QLabel[badge="true"][variant="info"],
QLabel[badge="true"][variant="warning"] {
    color: white; padding: 2px 8px; border-radius: 999px; font-size: 12px;
}
QLabel[badge="true"][variant="success"] { background: #198754; }
QLabel[badge="true"][variant="info"]    { background: #0dcaf0; color: #052c65; }
QLabel[badge="true"][variant="warning"] { background: #ffc107; color: #1f2937; }

/* Cabeceras */
QLabel#title { font-size: 20px; font-weight: 700; }
QLabel#subtitle { color: #6b7280; }

/* TextEdit como log */
QTextEdit {
    background: #0f172a; color: #e2e8f0;
    border: 1px solid #1f2937; border-radius: 12px;
    padding: 10px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 13px;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proxy de Caché")
        self.resize(860, 560)

        # Proxy (capa funcional)
        self.proxy = MusicServiceCacheProxy()

        # ====== Layout raíz ======
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        header = QHBoxLayout()
        lbl_title = QLabel("Lista de canciones"); lbl_title.setObjectName("title")
        lbl_sub = QLabel("Selecciona una canción y presiona reproducir"); lbl_sub.setObjectName("subtitle")
        header_box = QVBoxLayout(); header_box.addWidget(lbl_title); header_box.addWidget(lbl_sub)
        header.addLayout(header_box); header.addStretch()

        # Card container
        card = QFrame(); card.setObjectName("card")
        card_layout = QHBoxLayout(card); card_layout.setContentsMargins(16, 16, 16, 16); card_layout.setSpacing(16)

        # Lista de canciones
        self.list_songs = QListWidget()
        self.list_songs.addItems([
            "Viva la Vida - Coldplay", "Shape of You - Ed Sheeran", "Someone Like You - Adele",
            "Blinding Lights - The Weeknd", "Bad Guy - Billie Eilish", "Levitating - Dua Lipa",
            "Believer - Imagine Dragons", "Hello - Adele", "In The End - Linkin Park",
            "Thinking Out Loud - Ed Sheeran",
        ])
        self.list_songs.itemDoubleClicked.connect(self.on_play_clicked)

        # Panel derecho (acciones + estado + log)
        right_panel = QVBoxLayout(); right_panel.setSpacing(10)

        self.status_badge = QLabel("Sin reproducción")
        self.status_badge.setProperty("badge", True)
        self.status_badge.setProperty("variant", "warning")

        self.btn_play = QPushButton("Reproducir")
        self.btn_play.setProperty("class", "primary")
        self.btn_play.setEnabled(False)
        self.btn_play.clicked.connect(self.on_play_clicked)

        self.btn_clear_cache = QPushButton("Limpiar caché")
        self.btn_clear_cache.setProperty("class", "secondary")
        self.btn_clear_cache.clicked.connect(self.clear_cache)

        actions = QHBoxLayout()
        actions.addWidget(self.btn_play)
        actions.addWidget(self.btn_clear_cache)
        actions.addStretch()
        actions.addWidget(self.status_badge)

        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.log.append("🧪 Proxy de Caché listo.\n")

        right_panel.addLayout(actions)
        right_panel.addWidget(self.log, 1)

        card_layout.addWidget(self.list_songs, 2)
        card_layout.addLayout(right_panel, 3)

        root.addLayout(header)
        root.addWidget(card, 1)
        self.setCentralWidget(central)

        # Habilitar play al seleccionar
        self.list_songs.currentItemChanged.connect(
            lambda cur, prev: self.btn_play.setEnabled(cur is not None)
        )

        # Estilos
        self.setStyleSheet(BOOTSTRAPISH_QSS)

        # Worker en curso
        self.worker: FetchSongWorker | None = None

    # ================ Acciones UI ================
    def on_play_clicked(self):
        item = self.list_songs.currentItem()
        if not item:
            self.statusBar().showMessage("Selecciona una canción.")
            return
        self.start_fetch(item.text())

    def start_fetch(self, song_name: str):
        if self.worker and self.worker.isRunning():
            self.statusBar().showMessage("Ya hay una reproducción en curso…")
            return

        self.btn_play.setEnabled(False)
        self._set_badge("Buscando…", "info")
        self.log.append(f"➡️  Solicitud: {song_name}")

        self.worker = FetchSongWorker(self.proxy, song_name)
        self.worker.finished.connect(self.on_fetch_finished)
        self.worker.error.connect(self.on_fetch_error)
        self.worker.start()

    def on_fetch_finished(self, data: str, source: str):
        if source == "cache":
            self._set_badge("Desde caché", "success")
            self.log.append("✅ Resultado desde caché.")
        else:
            self._set_badge("Desde servidor", "info")
            self.log.append("🌐 Resultado desde servidor.")

        self.log.append(data + "\n")
        self.btn_play.setEnabled(True)
        self.statusBar().showMessage("Reproducción lista.")

    def on_fetch_error(self, message: str):
        self._set_badge("Error", "warning")
        self.log.append(f"❌ Error: {message}\n")
        self.btn_play.setEnabled(True)
        self.statusBar().showMessage("Ocurrió un error.")

    def clear_cache(self):
        self.proxy.cache.clear()
        self.log.append("🧹 Caché vaciada.\n")
        self.statusBar().showMessage("Caché limpiada.")

    # Helpers
    def _set_badge(self, text: str, variant: str):
        self.status_badge.setText(text)
        self.status_badge.setProperty("variant", variant)
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
