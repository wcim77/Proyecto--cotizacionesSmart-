from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QFileDialog, QScrollArea, QFormLayout, QTextEdit
from PySide6.QtCore import Qt
from utils.auth import get_all_companies, update_company
from db.database import get_company_by_rut

class ModifyCompanyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modificar Empresa")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.setStyleSheet("background-color: #2C2F33; color: #FFFFFF; font-size: 14px;")
        
        main_layout = QVBoxLayout()
        
        self.title_label = QLabel("✏️ Modificar Empresa", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFD700;")
        main_layout.addWidget(self.title_label)
        
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(scroll_area)
        scroll_layout = QFormLayout(scroll_content)
        
        self.company_selector = QComboBox()
        self.company_selector.setStyleSheet("padding: 12px; border-radius: 6px; background-color: #3B3F45; color: white; font-size: 14px;")
        self.load_companies()
        self.company_selector.currentIndexChanged.connect(self.load_company_details)
        scroll_layout.addRow(QLabel("Seleccione Empresa:"), self.company_selector)

        fields = [
            ("Nombre de la empresa", "name_entry"),
            ("Dirección", "address_entry"),
            ("Ruta del logo", "logo_path_entry"),
            ("Email", "email_entry"),
            ("Teléfono", "phone_entry"),
            ("Ciudad", "city_entry"),
            ("Giro", "giro_entry"),
            ("Nombre del representante", "representative_name_entry"),
            ("ID del representante", "representative_id_entry"),
            ("Email del representante", "representative_email_entry"),
            ("Teléfono del representante", "representative_phone_entry"),
            ("Nombre del banco", "bank_name_entry"),
            ("Número de cuenta", "account_number_entry"),
        ]
        
        for label_text, attr_name in fields:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
            entry = QLineEdit()
            entry.setPlaceholderText(label_text)
            entry.setStyleSheet("padding: 12px; border-radius: 6px; background-color: #3B3F45; color: white; font-size: 14px;")
            setattr(self, attr_name, entry)
            scroll_layout.addRow(label, entry)
        
        # Cambiar el campo account_type_entry a QComboBox
        account_type_label = QLabel("Tipo de cuenta")
        account_type_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        self.account_type_entry = QComboBox()
        self.account_type_entry.addItems(['Ahorro', 'Corriente', 'Vista'])
        self.account_type_entry.setStyleSheet("padding: 12px; border-radius: 6px; background-color: #3B3F45; color: white; font-size: 14px;")
        scroll_layout.addRow(account_type_label, self.account_type_entry)
        
        self.upload_logo_button = QPushButton("📂 Subir Logo")
        self.upload_logo_button.setStyleSheet("background-color: #007BFF; color: white; font-size: 16px; padding: 12px; border-radius: 6px;")
        self.upload_logo_button.clicked.connect(self.upload_logo)
        scroll_layout.addRow(QLabel(""), self.upload_logo_button)

        self.update_button = QPushButton("✏️ Modificar Empresa")
        self.update_button.setStyleSheet("background-color: #FFA500; color: white; font-size: 16px; padding: 12px; border-radius: 6px;")
        self.update_button.clicked.connect(self.update_company)
        scroll_layout.addRow(QLabel(""), self.update_button)

        # Sección de previsualización
        self.preview_label = QLabel("Previsualización de Datos", self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700; margin-top: 20px;")
        scroll_layout.addRow(self.preview_label)

        self.preview_text = QTextEdit(self)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("padding: 12px; border-radius: 6px; background-color: #3B3F45; color: white; font-size: 14px;")
        scroll_layout.addRow(self.preview_text)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def load_companies(self):
        companies = get_all_companies()  # <-- Asegúrate de que esta función devuelve datos

        self.company_selector.clear()
        
        for company in companies:
            print(f"📌 Cargando empresa: {company['name']} - RUT: {company['rut']}")  # <-- Depuración
            self.company_selector.addItem(f"{company['name']} ({company['rut']})", company['rut'])

    def load_company_details(self):
        company_rut = self.company_selector.currentData()
    
        print(f"Empresa seleccionada - RUT: {company_rut}")  # <-- Depuración

        if not company_rut:
            print("⚠️ No se ha seleccionado ninguna empresa.")
            return

        company_data = get_company_by_rut(company_rut)
        
        if not company_data:
            print(f"⚠️ No se encontraron datos para la empresa con RUT: {company_rut}")
            QMessageBox.warning(self, "Error", f"No se encontraron datos para la empresa con RUT: {company_rut}")
            return

        # Si encuentra los datos, los muestra en los campos
        self.name_entry.setText(company_data.get("name", ""))
        self.address_entry.setText(company_data.get("address", ""))
        self.logo_path_entry.setText(company_data.get("logo_path", ""))
        self.email_entry.setText(company_data.get("email", ""))
        self.phone_entry.setText(company_data.get("phone", ""))
        self.city_entry.setText(company_data.get("city", ""))
        self.giro_entry.setText(company_data.get("giro", ""))
        self.representative_name_entry.setText(company_data.get("representative_name", ""))
        self.representative_id_entry.setText(company_data.get("representative_id", ""))
        self.representative_email_entry.setText(company_data.get("representative_email", ""))
        self.representative_phone_entry.setText(company_data.get("representative_phone", ""))
        self.bank_name_entry.setText(company_data.get("bank_name", ""))
        self.account_number_entry.setText(company_data.get("account_number", ""))

        # Selecciona el tipo de cuenta en el QComboBox
        account_type = company_data.get("account_type", "")
        index = self.account_type_entry.findText(account_type)
        if index != -1:
            self.account_type_entry.setCurrentIndex(index)

        # Actualizar la previsualización
        self.update_preview()

    def update_preview(self):
        preview_text = f"""
        <b>Nombre de la empresa:</b> {self.name_entry.text()}<br>
        <b>Dirección:</b> {self.address_entry.text()}<br>
        <b>Ruta del logo:</b> {self.logo_path_entry.text()}<br>
        <b>Email:</b> {self.email_entry.text()}<br>
        <b>Teléfono:</b> {self.phone_entry.text()}<br>
        <b>Ciudad:</b> {self.city_entry.text()}<br>
        <b>Giro:</b> {self.giro_entry.text()}<br>
        <b>Nombre del representante:</b> {self.representative_name_entry.text()}<br>
        <b>ID del representante:</b> {self.representative_id_entry.text()}<br>
        <b>Email del representante:</b> {self.representative_email_entry.text()}<br>
        <b>Teléfono del representante:</b> {self.representative_phone_entry.text()}<br>
        <b>Nombre del banco:</b> {self.bank_name_entry.text()}<br>
        <b>Tipo de cuenta:</b> {self.account_type_entry.currentText()}<br>
        <b>Número de cuenta:</b> {self.account_number_entry.text()}<br>
        """
        self.preview_text.setHtml(preview_text)

    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.logo_path_entry.setText(file_path)
            self.update_preview()

    def update_company(self):
        company_rut = self.company_selector.currentData()
        if not company_rut:
            QMessageBox.warning(self, "Error", "Seleccione una empresa para modificar")
            return

        account_type = self.account_type_entry.currentText()
        if account_type not in ['Ahorro', 'Corriente', 'Vista']:
            QMessageBox.warning(self, "Error", "El tipo de cuenta debe ser 'Ahorro', 'Corriente' o 'Vista'")
            return

        updated_data = {
            "new_name": self.name_entry.text(),
            "new_address": self.address_entry.text(),
            "new_logo_path": self.logo_path_entry.text(),
            "new_email": self.email_entry.text(),
            "new_phone": self.phone_entry.text(),
            "new_city": self.city_entry.text(),
            "new_giro": self.giro_entry.text(),
            "new_representative_name": self.representative_name_entry.text(),
            "new_representative_id": self.representative_id_entry.text(),
            "new_representative_email": self.representative_email_entry.text(),
            "new_representative_phone": self.representative_phone_entry.text(),
            "new_bank_name": self.bank_name_entry.text(),
            "new_account_type": account_type,
            "new_account_number": self.account_number_entry.text()
        }

        try:
            update_company(company_rut, **updated_data)
            QMessageBox.information(self, "Éxito", "Empresa modificada correctamente")
            self.load_companies()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))