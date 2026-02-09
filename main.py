import sys
from io import BytesIO
import requests
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QStatusBar
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


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

        # Поля ввода (как в .ui)
        input_layout = QHBoxLayout()
        self.lat_edit = QLineEdit()
        self.lat_edit.setPlaceholderText("Широта")
        self.lon_edit = QLineEdit()
        self.lon_edit.setPlaceholderText("Долгота")
        input_layout.addWidget(self.lat_edit)
        input_layout.addWidget(self.lon_edit)

        # Кнопка "Показать карту"
        self.load_btn = QPushButton("Показать карту")
        self.load_btn.clicked.connect(self.load_map)

        # Метка для отображения карты
        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_label.setMinimumSize(600, 400)
        self.map_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        # Статусная строка
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.load_btn)
        main_layout.addWidget(self.map_label)

        # Подключение Enter к полям
        self.lat_edit.returnPressed.connect(self.load_map)
        self.lon_edit.returnPressed.connect(self.load_map)

        self.apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

    def load_map(self, flag):
        lat_text = self.lat_edit.text().strip()
        lon_text = self.lon_edit.text().strip()

        try:
            if flag:
                if flag == "Up":
                    self.lon = float(lon_text)
                    self.lat = float(lat_text) + (float(lat_text) * 0.00001)
                    self.lat_edit.setText(str(round(self.lat, 6)))
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

        self.status_bar.showMessage("Загрузка карты...", 2000)

        # Формируем запрос к Yandex Static Maps
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

            # Загружаем изображение в QPixmap
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
            self.status_bar.showMessage(f"Карта: {self.lat}, {self.lon}", 3000)

        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки карты: {str(e)}", 5000)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            pass
        if event.key() == Qt.Key.Key_Right:
            pass
        if event.key() == Qt.Key.Key_Up:
            self.load_map("Up")
        if event.key() == Qt.Key.Key_Down:
            pass



def main():
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
