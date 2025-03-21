import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout, QFrame, QInputDialog
from PySide6.QtCore import QRect
from ui.user_management import UserManagementWindow
from ui.company_management import CompanyManagementWindow
from ui.modify_company import ModifyCompanyWindow
from db.database import delete_company_by_rut  # Asegúrate de tener esta función en tu módulo de base de datos

class DeveloperDashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modo Programador - Panel Avanzado")
        self.setGeometry(QRect(0, 0, 1920, 1080))
        self.showMaximized()

        layout = QVBoxLayout()

        # Encabezado
        self.label = QLabel("Panel de Control para Programador", self)
        self.label.setStyleSheet("font-size: 26px; font-weight: bold; color: #FFD700; text-align: center;")
        layout.addWidget(self.label)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Contenedor de botones
        button_layout = QVBoxLayout()

        self.reset_password_button = QPushButton("🔑 Restablecer Contraseña", self)
        self.reset_password_button.setStyleSheet("background-color: #FF5733; color: white; font-size: 16px; font-weight: bold; padding: 12px; border-radius: 6px;")
        self.reset_password_button.clicked.connect(self.reset_user_password)
        button_layout.addWidget(self.reset_password_button)

        self.create_user_button = QPushButton("👤 Gestionar Usuarios", self)
        self.create_user_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; font-weight: bold; padding: 12px; border-radius: 6px;")
        self.create_user_button.clicked.connect(self.open_user_management)
        button_layout.addWidget(self.create_user_button)

        self.manage_companies_button = QPushButton("🏢 Gestionar Empresas", self)
        self.manage_companies_button.setStyleSheet("background-color: #007BFF; color: white; font-size: 16px; font-weight: bold; padding: 12px; border-radius: 6px;")
        self.manage_companies_button.clicked.connect(self.open_company_management)
        button_layout.addWidget(self.manage_companies_button)

        self.modify_company_button = QPushButton("✏️ Modificar Empresa", self)
        self.modify_company_button.setStyleSheet("background-color: #FFA500; color: white; font-size: 16px; font-weight: bold; padding: 12px; border-radius: 6px;")
        self.modify_company_button.clicked.connect(self.open_modify_company)
        button_layout.addWidget(self.modify_company_button)

        self.delete_company_button = QPushButton("🗑️ Borrar Empresa", self)
        self.delete_company_button.setStyleSheet("background-color: #FF0000; color: white; font-size: 16px; font-weight: bold; padding: 12px; border-radius: 6px;")
        self.delete_company_button.clicked.connect(self.delete_company)
        button_layout.addWidget(self.delete_company_button)

        self.exit_button = QPushButton("❌ Cerrar", self)
        self.exit_button.setStyleSheet("background-color: #DC3545; color: white; font-size: 16px; font-weight: bold; padding: 12px; border-radius: 6px;")
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def reset_user_password(self):
        QMessageBox.information(self, "Función", "Aquí puedes restablecer contraseñas.")

    def open_user_management(self):
        self.user_management_window = UserManagementWindow()
        self.user_management_window.show()

    def open_company_management(self):
        self.company_management_window = CompanyManagementWindow()
        self.company_management_window.show()

    def open_modify_company(self):
        self.modify_company_window = ModifyCompanyWindow()
        self.modify_company_window.show()

    def delete_company(self):
        company_rut, ok = QInputDialog.getText(self, "Borrar Empresa", "Ingrese el RUT de la empresa a borrar:")
        if ok and company_rut:
            confirm = QMessageBox.question(self, "Confirmar Borrado", f"¿Está seguro de que desea borrar la empresa con RUT '{company_rut}'?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                if delete_company_by_rut(company_rut):
                    QMessageBox.information(self, "Éxito", f"La empresa con RUT '{company_rut}' ha sido borrada.")
                else:
                    QMessageBox.warning(self, "Error", f"No se pudo borrar la empresa con RUT '{company_rut}'. Verifique que el RUT sea correcto.")

