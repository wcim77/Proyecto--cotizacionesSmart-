from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QFrame, QHBoxLayout
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QPalette, QBrush
from ui.file_management import FileManagementWindow
from ui.invoice_creation import QuotationCreationWindow
from ui.change_password import ChangePasswordWindow
from ui.support_window import SupportWindow  # Importa la nueva ventana de soporte
from ui.components import create_button
from utils.images import resource_path


class DashboardWindow(QWidget):
    def __init__(self, company, role):
        super().__init__()
        self.setWindowTitle(f"Gestor de cotizaciones - ({company}, {role})")
        
        self.setGeometry(QRect(0, 0, 1920, 1080))
        self.showMaximized()

        # 🔥 CONFIGURAR IMAGEN DE FONDO
        background_image = QPixmap(resource_path("path/background.jpg"))  # Ruta de la imagen
        if not background_image.isNull():
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(background_image.scaled(self.size(), Qt.KeepAspectRatioByExpanding)))
            self.setPalette(palette)
        else:
            print("⚠️ Advertencia: No se encontró la imagen de fondo.")

        self.company = company
        self.role = role

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        container_frame = QFrame(self)
        container_frame.setStyleSheet("background-color: rgba(35, 39, 42, 0.9); border-radius: 15px; padding: 40px;")
        container_frame.setMaximumWidth(600)
        container_frame.setMaximumHeight(600)

        layout = QVBoxLayout(container_frame)
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel(f"{self.company}!", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF; margin: 20px 0;")
        layout.addWidget(self.label)

        # Estilo base para botones
        button_style = (
            "padding: 15px; border-radius: 8px; font-weight: bold; "
            "margin: 10px 0; width: 300px;"
        )

        self.file_button = create_button("Gestionar Archivos", "#4CAF50", self.open_file_management)
        self.file_button.setStyleSheet(button_style + "background-color: #4CAF50; color: #FFFFFF;")
        layout.addWidget(self.file_button)

        self.invoice_button = create_button("Crear Cotización", "#007BFF", self.open_invoice_creation)
        self.invoice_button.setStyleSheet(button_style + "background-color: #007BFF; color: #FFFFFF;")
        layout.addWidget(self.invoice_button)

        self.change_password_button = create_button("Cambiar Contraseña", "#FFA500", self.open_change_password)
        self.change_password_button.setStyleSheet(button_style + "background-color: #FFA500; color: #FFFFFF;")
        layout.addWidget(self.change_password_button)

        self.support_button = create_button("Soporte", "#17A2B8", self.open_support)  # Añadir botón de soporte
        self.support_button.setStyleSheet(button_style + "background-color: #17A2B8; color: #FFFFFF;")
        layout.addWidget(self.support_button)

        self.exit_button = create_button("Salir", "#DC3545", self.close)
        self.exit_button.setStyleSheet(button_style + "background-color: #DC3545; color: #FFFFFF;")
        layout.addWidget(self.exit_button)

        main_layout.addSpacerItem(QSpacerItem(20, 150, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addWidget(container_frame, alignment=Qt.AlignCenter)
        main_layout.addSpacerItem(QSpacerItem(20, 150, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(main_layout)

    def open_file_management(self):
        self.file_window = FileManagementWindow(self.company, self.role)
        self.file_window.show()

    def open_invoice_creation(self):
        self.invoice_window = QuotationCreationWindow(self.company, self.role)
        self.invoice_window.show()

    def open_change_password(self):
        self.change_password_window = ChangePasswordWindow()
        self.change_password_window.show()

    def open_support(self):
        self.support_window = SupportWindow()
        self.support_window.show()

