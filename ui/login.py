import os
import json
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QCheckBox, QMessageBox, QFrame, QComboBox
)
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtCore import Qt, QRect
from utils.auth import authenticate_user, recover_password_button, get_companies_by_rut
from ui.dashboard import DashboardWindow
from ui.programmer_dashboard import DeveloperDashboardWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar Sesión")
        self.setGeometry(QRect(0, 0, 1920, 1080))
        self.showMaximized()

        self.remember_file = "remember_user.json"

        # Fondo con imagen difuminada
        palette = QPalette()
        background_image = QPixmap("path/image.jpg")
        palette.setBrush(QPalette.Window, QBrush(background_image.scaled(self.size(), Qt.KeepAspectRatioByExpanding)))
        self.setPalette(palette)

        # Contenedor principal
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Caja de inicio de sesión con efecto vidrio esmerilado
        center_container = QFrame(self)
        center_container.setFixedSize(500, 700)
        center_container.setStyleSheet("""
            background-color: rgba(35, 39, 42, 0.85);
            border-radius: 15px;
            padding: 30px;
        """)

        container_layout = QVBoxLayout(center_container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(15)

        # Título
        self.title_label = QLabel("Bienvenido", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #FFFFFF;")
        container_layout.addWidget(self.title_label)

        # Campo de RUT
        self.rut_entry = QLineEdit(self)
        self.rut_entry.setPlaceholderText("Ingrese su RUT (Ej: 12.345.678-9)")
        self.rut_entry.setFixedWidth(400)
        self.rut_entry.setStyleSheet(self.input_style())
        self.rut_entry.textChanged.connect(self.load_companies)
        self.rut_entry.textChanged.connect(self.format_rut)  # Conectar al evento textChanged
        container_layout.addWidget(self.rut_entry)

        # Campo de contraseña
        self.password_entry = QLineEdit(self)
        self.password_entry.setPlaceholderText("Ingrese su contraseña")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setFixedWidth(400)
        self.password_entry.setStyleSheet(self.input_style())
        container_layout.addWidget(self.password_entry)

        # Selección de empresa
        self.company_box = QComboBox(self)
        self.company_box.setFixedWidth(400)
        self.company_box.setStyleSheet(self.input_style())
        container_layout.addWidget(self.company_box)

        # Checkbox "Recordar Usuario"
        self.remember_checkbox = QCheckBox("Recordar Usuario", self)
        self.remember_checkbox.setStyleSheet("color: #FFFFFF;")
        container_layout.addWidget(self.remember_checkbox)

        # Cargar usuario si estaba guardado
        self.load_saved_user()

        # Botón de inicio de sesión con efecto hover
        self.login_button = QPushButton("Iniciar Sesión", self)
        self.login_button.setFixedWidth(400)
        self.login_button.setStyleSheet(self.button_style("#4CAF50", "#45A049"))
        self.login_button.clicked.connect(self.login)
        container_layout.addWidget(self.login_button)

        # Botón de recuperar contraseña
        self.recover_password_button = QPushButton("Recuperar Contraseña", self)
        self.recover_password_button.setFixedWidth(400)
        self.recover_password_button.setStyleSheet(self.button_style("#FFA500", "#E69500"))
        self.recover_password_button.clicked.connect(self.recover_password)
        container_layout.addWidget(self.recover_password_button)

        main_layout.addWidget(center_container, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)

    def input_style(self):
        """Estilo para los campos de entrada."""
        return """
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #555555;
            background-color: #40444B;
            color: #FFFFFF;
            font-size: 14px;
        """

    def button_style(self, color, hover_color):
        """Estilo para los botones con efecto hover."""
        return f"""
            padding: 12px;
            border-radius: 8px;
            background-color: {color};
            color: #FFFFFF;
            font-weight: bold;
            font-size: 16px;
        """
    
    def load_saved_user(self):
        """Carga el usuario guardado si el usuario seleccionó 'Recordar Usuario'."""
        if os.path.exists(self.remember_file):
            with open(self.remember_file, 'r') as file:
                data = json.load(file)
                self.rut_entry.setText(data.get("username", ""))
                self.password_entry.setText(data.get("password", ""))
                self.remember_checkbox.setChecked(True)

    def save_user(self, username, password):
        """Guarda o elimina el usuario en función del checkbox."""
        if self.remember_checkbox.isChecked():
            with open(self.remember_file, 'w') as file:
                json.dump({"username": username, "password": password}, file)
        elif os.path.exists(self.remember_file):
            os.remove(self.remember_file)

    def load_companies(self):
        """Carga las empresas asociadas al RUT ingresado."""
        rut = self.rut_entry.text()
        if rut:
            companies = get_companies_by_rut(rut)
            self.company_box.clear()
            if companies:
                self.company_box.addItems(companies)
            else:
                self.company_box.addItem("No hay empresas asociadas")

    def format_rut(self, text):
        """Formatea el RUT en formato chileno."""
        clean_rut = re.sub(r'[^0-9Kk]', '', text)

        if len(clean_rut) < 2:
            self.rut_entry.setText(text)  # No aplicar formato si es muy corto
            return

        # Separar número y dígito verificador
        num_part = clean_rut[:-1]  # Todo menos el último dígito
        dv = clean_rut[-1]  # Último dígito

        # Insertar puntos cada tres dígitos desde el final
        formatted_num = ".".join(re.findall(r'\d{1,3}', num_part[::-1]))[::-1]

        # Formato final con guion
        formatted_text = f"{formatted_num}-{dv.upper()}"

        # Asignar el texto formateado al campo de entrada
        self.rut_entry.setText(formatted_text)

    def login(self):
        """Verifica credenciales y abre el dashboard correspondiente."""
        rut = self.rut_entry.text().strip()
        password = self.password_entry.text().strip()
        company = self.company_box.currentText().strip()

        if not rut or not password:
            self.show_error("Debe ingresar su RUT y contraseña")
            return

        user = authenticate_user(rut, password)
        
        if user:
            self.save_user(rut, password)

            if user["dashboard"] == "programmer":
                self.developer_dashboard = DeveloperDashboardWindow()
                self.developer_dashboard.show()
            elif company and company != "No hay empresas asociadas":
                self.dashboard = DashboardWindow(company, user["role"])
                self.dashboard.show()
            else:
                self.show_error("Debe seleccionar una empresa válida")
                return
            
            self.close()
        else:
            self.show_error("RUT, empresa o contraseña inválidos")

    def recover_password(self):
        """Inicia el proceso de recuperación de contraseña."""
        rut = self.rut_entry.text()
        if rut:
            result = recover_password_button(rut)
            QMessageBox.information(self, "Recuperación de Contraseña", result)
        else:
            self.show_error("Ingrese su RUT para recuperar la contraseña")

    def show_error(self, message):
        """Muestra un mensaje de error y resalta los campos vacíos."""
        QMessageBox.warning(self, "Error", message)
        if not self.rut_entry.text():
            self.rut_entry.setStyleSheet(self.input_style() + "border: 1px solid red;")
        if not self.password_entry.text():
            self.password_entry.setStyleSheet(self.input_style() + "border: 1px solid red;")
