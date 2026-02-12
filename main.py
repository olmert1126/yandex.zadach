import sys
from io import BytesIO
import requests
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QStatusBar, QComboBox
)
from PyQt6.QtGui import QPixmap, QImage, QKeyEvent
from PyQt6.QtCore import Qt

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Карта по координатам")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        input_layout = QHBoxLayout()
        self.lat_edit = QLineEdit()
        self.lat_edit.setPlaceholderText("Широта")
        self.lon_edit = QLineEdit()
        self.lon_edit.setPlaceholderText("Долгота")
        input_layout.addWidget(self.lat_edit)
        input_layout.addWidget(self.lon_edit)

        self.load_btn = QPushButton("Показать карту")
        self.load_btn.clicked.connect(self.load_map)

        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_label.setMinimumSize(600, 400)
        self.map_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.load_btn)
        main_layout.addWidget(self.map_label)

        self.lat_edit.returnPressed.connect(self.load_map)
        self.lon_edit.returnPressed.connect(self.load_map)

        self.apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

        self.current_lat = None
        self.current_lon = None
        self.zoom_level = 15
        self.min_zoom = 0
        self.max_zoom = 21

    def _zoom_to_spn(self, zoom):
        return 180.0 / (2 ** zoom)

    def load_map(self):
        lat_text = self.lat_edit.text().strip()
        lon_text = self.lon_edit.text().strip()

        try:
            lat = float(lat_text)
            lon = float(lon_text)
            if not (-90 <= lat <= 90):
                raise ValueError("Широта должна быть от -90 до 90")
            if not (-180 <= lon <= 180):
                raise ValueError("Долгота должна быть от -180 до 180")
        except ValueError as e:
            self.status_bar.showMessage(f"Ошибка: {e}", 5000)
            return

        self.current_lat = lat
        self.current_lon = lon
        self._fetch_and_show_map()

    def _fetch_and_show_map(self):
        self.status_bar.showMessage(f"Загрузка карты (zoom={self.zoom_level})...", 2000)

        spn_val = self._zoom_to_spn(self.zoom_level)
        map_params = {
            "ll": f"{self.current_lon},{self.current_lat}",
            "spn": f"{spn_val},{spn_val}",
            "l": "map",
            "size": "600,400",
            "apikey": self.apikey
        }

        try:
            response = requests.get("https://static-maps.yandex.ru/v1", params=map_params, timeout=10)
            response.raise_for_status()

            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data).convert("RGBA")
            data = pil_image.tobytes("raw", "RGBA")
            qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)

            self.map_label.setPixmap(pixmap.scaled(
                self.map_label.width(),
                self.map_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            self.status_bar.showMessage(
                f"Карта: {self.current_lat}, {self.current_lon} | Zoom: {self.zoom_level}",
                3000
            )

        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки карты: {str(e)}", 5000)

    def keyPressEvent(self, event: QKeyEvent):
        if self.current_lat is None or self.current_lon is None:
            return

        key = event.key()
        if key == Qt.Key.Key_PageUp:
            if self.zoom_level < self.max_zoom:
                self.zoom_level += 1
                self._fetch_and_show_map()
            else:
                self.status_bar.showMessage("Достигнут максимальный зум (21)", 2000)

        elif key == Qt.Key.Key_PageDown:
            if self.zoom_level > self.min_zoom:
                self.zoom_level -= 1
                self._fetch_and_show_map()
            else:
                self.status_bar.showMessage("Достигнут минимальный зум (0)", 2000)

        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()