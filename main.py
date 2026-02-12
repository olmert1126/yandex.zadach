import sys
from io import BytesIO
import requests
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QStatusBar, QComboBox
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QEvent

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Карта по координатам")
        self.resize(800, 600)

        self.lat = 0
        self.lon = 0

        # Центральный виджет и макет
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

        self.lat_edit.installEventFilter(self)
        self.lon_edit.installEventFilter(self)

        self.apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

    def load_map(self, flag):
        lat_text = self.lat_edit.text().strip()
        lon_text = self.lon_edit.text().strip()

        try:
            if flag:
                step = 0.005
                if flag == "Up":
                    self.lat += step
                elif flag == "Down":
                    self.lat -= step
                elif flag == "Left":
                    self.lon -= step
                elif flag == "Right":
                    self.lon += step
            else:
                self.lat = float(lat_text)
                self.lon = float(lon_text)
            if not (-90 <= self.lat <= 90):
                raise ValueError("Широта должна быть от -90 до 90")
            if not (-180 <= self.lon <= 180):
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
            "ll": f"{self.lon},{self.lat}",
            "spn": "0.005,0.005",
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.load_map("Left")
        if event.key() == Qt.Key.Key_Right:
            self.load_map("Right")
        if event.key() == Qt.Key.Key_Up:
            self.load_map("Up")
        if event.key() == Qt.Key.Key_Down:
            self.load_map("Down")

    def eventFilter(self, source, event):
        if (event.type() == event.Type.KeyPress and
                source in (self.lat_edit, self.lon_edit) and
                event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right,
                                Qt.Key.Key_Up, Qt.Key.Key_Down)):
            direction_map = {
                Qt.Key.Key_Up: "Up",
                Qt.Key.Key_Down: "Down",
                Qt.Key.Key_Left: "Left",
                Qt.Key.Key_Right: "Right"
            }
            self.load_map(direction_map[event.key()])
            return True
        return super().eventFilter(source, event)
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