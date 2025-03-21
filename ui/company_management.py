import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QFrame, QHBoxLayout, QGridLayout, QComboBox, QScrollArea
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QRect
from db.database import add_company
from db.database import save_logo

class CompanyManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Empresas")
        self.setGeometry(QRect(0, 0, 1920, 1080))
        self.showMaximized()
        self.setStyleSheet("background-color: #F5F5F5; color: #333333; font-size: 16px;")

        main_layout = QVBoxLayout()

        self.title_label = QLabel("Añadir nueva empresa", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333333;")
        main_layout.addWidget(self.title_label)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(scroll_area)
        scroll_layout = QVBoxLayout(scroll_content)

        form_layout = QGridLayout()
        form_layout.setSpacing(15)

        # Datos de la empresa
        self.name_entry = QLineEdit(self)
        self.name_entry.setPlaceholderText("Nombre de la empresa")
        form_layout.addWidget(QLabel("Nombre de la Empresa:"), 0, 0)
        form_layout.addWidget(self.name_entry, 0, 1)

        self.address_entry = QLineEdit(self)
        self.address_entry.setPlaceholderText("Dirección")
        form_layout.addWidget(QLabel("Dirección:"), 1, 0)
        form_layout.addWidget(self.address_entry, 1, 1)

        self.email_entry = QLineEdit(self)
        self.email_entry.setPlaceholderText("Correo electrónico")
        form_layout.addWidget(QLabel("Correo Electrónico:"), 2, 0)
        form_layout.addWidget(self.email_entry, 2, 1)

        self.rut_entry = QLineEdit(self)
        self.rut_entry.setPlaceholderText("RUT")
        form_layout.addWidget(QLabel("RUT:"), 3, 0)
        form_layout.addWidget(self.rut_entry, 3, 1)

        self.phone_entry = QLineEdit(self)
        self.phone_entry.setPlaceholderText("Teléfono")
        form_layout.addWidget(QLabel("Teléfono:"), 4, 0)
        form_layout.addWidget(self.phone_entry, 4, 1)

        self.city_entry = QLineEdit(self)
        self.city_entry.setPlaceholderText("Ciudad")
        form_layout.addWidget(QLabel("Ciudad:"), 5, 0)
        form_layout.addWidget(self.city_entry, 5, 1)

        self.giro_entry = QLineEdit(self)
        self.giro_entry.setPlaceholderText("Giro")
        form_layout.addWidget(QLabel("Giro:"), 6, 0)
        form_layout.addWidget(self.giro_entry, 6, 1)

        # Datos del representante legal
        self.representative_name_entry = QLineEdit(self)
        self.representative_name_entry.setPlaceholderText("Nombre del representante legal")
        form_layout.addWidget(QLabel("Nombre del Representante Legal:"), 7, 0)
        form_layout.addWidget(self.representative_name_entry, 7, 1)

        self.representative_id_entry = QLineEdit(self)
        self.representative_id_entry.setPlaceholderText("Cédula o documento de identidad")
        form_layout.addWidget(QLabel("Cédula o Documento de Identidad:"), 8, 0)
        form_layout.addWidget(self.representative_id_entry, 8, 1)

        self.representative_email_entry = QLineEdit(self)
        self.representative_email_entry.setPlaceholderText("Correo electrónico del representante")
        form_layout.addWidget(QLabel("Correo del Representante:"), 9, 0)
        form_layout.addWidget(self.representative_email_entry, 9, 1)

        self.representative_phone_entry = QLineEdit(self)
        self.representative_phone_entry.setPlaceholderText("Teléfono del representante")
        form_layout.addWidget(QLabel("Teléfono del Representante:"), 10, 0)
        form_layout.addWidget(self.representative_phone_entry, 10, 1)

        # Datos bancarios
        self.bank_name_entry = QLineEdit(self)
        self.bank_name_entry.setPlaceholderText("Banco")
        form_layout.addWidget(QLabel("Banco:"), 11, 0)
        form_layout.addWidget(self.bank_name_entry, 11, 1)

        self.account_type_box = QComboBox(self)
        self.account_type_box.addItems(["Ahorro", "Corriente", "Vista"])
        form_layout.addWidget(QLabel("Tipo de Cuenta:"), 12, 0)
        form_layout.addWidget(self.account_type_box, 12, 1)

        self.account_number_entry = QLineEdit(self)
        self.account_number_entry.setPlaceholderText("Número de cuenta")
        form_layout.addWidget(QLabel("Número de Cuenta:"), 13, 0)
        form_layout.addWidget(self.account_number_entry, 13, 1)

        # Logo de la empresa
        self.logo_label = QLabel(self)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(150, 150)
        self.logo_label.setStyleSheet("border: 1px solid #CCC; background-color: #FFF;")
        self.logo_label.setText("No se ha seleccionado imagen")
        form_layout.addWidget(self.logo_label, 14, 0)

        self.upload_logo_button = QPushButton("Subir Logo", self)
        self.upload_logo_button.setStyleSheet("padding: 10px; background-color: #007BFF; color: #FFFFFF; border-radius: 8px;")
        self.upload_logo_button.clicked.connect(self.upload_logo)
        form_layout.addWidget(self.upload_logo_button, 14, 1)

        scroll_layout.addLayout(form_layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Botones
        button_layout = QHBoxLayout()
        self.add_company_button = QPushButton("Añadir Empresa", self)
        self.add_company_button.setStyleSheet("padding: 12px; background-color: #28A745; color: #FFFFFF; border-radius: 8px;")
        self.add_company_button.clicked.connect(self.add_company)
        button_layout.addWidget(self.add_company_button)

        self.back_button = QPushButton("Atrás", self)
        self.back_button.setStyleSheet("padding: 12px; background-color: #6C757D; color: #FFFFFF; border-radius: 8px;")
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.logo_path = None

    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Imágenes (*.png *.jpg *.jpeg)")
        if file_path:
            try:
                self.logo_path = save_logo(file_path)
                if self.logo_path and os.path.isfile(self.logo_path):
                    pixmap = QPixmap(file_path)
                    self.logo_label.setPixmap(pixmap.scaled(150, 150))
            except Exception:
                QMessageBox.warning(self, "Error", "Error al subir el logo")

    def add_company(self):
        name = self.name_entry.text()
        address = self.address_entry.text()
        email = self.email_entry.text()
        rut = self.rut_entry.text()
        phone = self.phone_entry.text()
        city = self.city_entry.text()
        giro = self.giro_entry.text()
        representative_name = self.representative_name_entry.text()
        representative_id = self.representative_id_entry.text()
        representative_email = self.representative_email_entry.text()
        representative_phone = self.representative_phone_entry.text()
        bank_name = self.bank_name_entry.text()
        account_type = self.account_type_box.currentText()
        account_number = self.account_number_entry.text()
        logo_path = self.logo_path  # Asegurar que se está pasando el logo

        if all([name, address, email, rut, phone, city, giro, representative_name, representative_id,
                representative_email, representative_phone, bank_name, account_type, account_number, logo_path]):
            add_company(name, address, logo_path, email, rut, phone, city, giro,
                        representative_name, representative_id, representative_email,
                        representative_phone, bank_name, account_type, account_number)
            QMessageBox.information(self, "Éxito", "Empresa añadida exitosamente")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Todos los campos, incluido el logo, son obligatorios")


    def go_back(self):
        self.close()
