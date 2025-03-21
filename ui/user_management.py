from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QListWidget, QMessageBox, QHeaderView, QInputDialog, QComboBox
from PySide6.QtCore import Qt
from utils.auth import add_user, reset_password, get_all_users, get_all_companies, assign_user_to_company, delete_user, update_user, update_company

class UserManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Usuarios")
        self.setGeometry(100, 100, 850, 600)
        self.setStyleSheet("background-color: #1E1E1E; color: #FFFFFF; font-size: 14px;")
        
        layout = QVBoxLayout()

        self.title_label = QLabel("👥 Administración de Usuarios", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFD700;")
        layout.addWidget(self.title_label)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(2)
        self.user_table.setHorizontalHeaderLabels(["RUT", "Rol"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.setStyleSheet("background-color: #2C2F33; color: white; border: 1px solid #555;")
        layout.addWidget(self.user_table)
        
        self.load_users()
        
        self.rut_entry = QLineEdit()
        self.rut_entry.setPlaceholderText("Ingrese RUT del usuario")
        self.rut_entry.setStyleSheet("padding: 8px; border-radius: 5px; background-color: #3B3F45; color: white;")
        layout.addWidget(self.rut_entry)
        
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Ingrese contraseña")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet("padding: 8px; border-radius: 5px; background-color: #3B3F45; color: white;")
        layout.addWidget(self.password_entry)
        
        self.role_box = QComboBox()
        self.role_box.addItems(["Admin", "User"])
        self.role_box.setStyleSheet("padding: 8px; border-radius: 5px; background-color: #3B3F45; color: white;")
        layout.addWidget(self.role_box)
        
        self.company_list = QListWidget()
        self.company_list.setSelectionMode(QListWidget.MultiSelection)
        self.company_list.setStyleSheet("padding: 8px; border-radius: 5px; background-color: #3B3F45; color: white;")
        self.load_companies()
        layout.addWidget(self.company_list)
        
        self.add_user_button = QPushButton("➕ Agregar Usuario")
        self.add_user_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px; border-radius: 6px;")
        self.add_user_button.clicked.connect(self.add_user)
        layout.addWidget(self.add_user_button)
        
        self.update_user_button = QPushButton("✏️ Modificar Usuario")
        self.update_user_button.setStyleSheet("background-color: #FFA500; color: white; font-size: 16px; padding: 10px; border-radius: 6px;")
        self.update_user_button.clicked.connect(self.update_user)
        layout.addWidget(self.update_user_button)
        
        self.reset_password_button = QPushButton("🔑 Restablecer Contraseña")
        self.reset_password_button.setStyleSheet("background-color: #FF5733; color: white; font-size: 16px; padding: 10px; border-radius: 6px;")
        self.reset_password_button.clicked.connect(self.reset_password)
        layout.addWidget(self.reset_password_button)
        
        self.delete_user_button = QPushButton("🗑️ Eliminar Usuario")
        self.delete_user_button.setStyleSheet("background-color: #D9534F; color: white; font-size: 16px; padding: 10px; border-radius: 6px;")
        self.delete_user_button.clicked.connect(self.delete_user)
        layout.addWidget(self.delete_user_button)
       
        
        self.setLayout(layout)
    
    def load_users(self):
        users = get_all_users()
        self.user_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(user["rut"]))
            self.user_table.setItem(row, 1, QTableWidgetItem(user["role"]))
    
    def load_companies(self):
        companies = get_all_companies()
        self.company_list.clear()
        for company in companies:
            self.company_list.addItem(f"{company['name']} ({company['rut']})")
    
    def add_user(self):
        rut = self.rut_entry.text()
        password = self.password_entry.text()
        role = self.role_box.currentText()
        selected_companies = self.company_list.selectedItems()
        
        if not rut or not password:
            QMessageBox.warning(self, "Error", "Debe ingresar RUT y contraseña")
            return
        
        if not selected_companies:
            QMessageBox.warning(self, "Error", "Debe seleccionar al menos una empresa")
            return
        
        try:
            add_user(rut, password, role)
            for company_item in selected_companies:
                company_rut = company_item.text().split('(')[-1].strip(')')
                assign_user_to_company(rut, company_rut)
            QMessageBox.information(self, "Éxito", "Usuario agregado correctamente")
            self.load_users()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def update_user(self):
        selected_row = self.user_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para modificar")
            return
        
        rut = self.user_table.item(selected_row, 0).text()
        new_password = self.password_entry.text()
        new_role = self.role_box.currentText()
        selected_companies = self.company_list.selectedItems()
        
        if not selected_companies:
            QMessageBox.warning(self, "Error", "Debe seleccionar al menos una empresa")
            return
        
        try:
            update_user(rut, new_password, new_role)
            for company_item in selected_companies:
                company_rut = company_item.text().split('(')[-1].strip(')')
                assign_user_to_company(rut, company_rut)
            QMessageBox.information(self, "Éxito", "Usuario modificado correctamente")
            self.load_users()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def reset_password(self):
        selected_row = self.user_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para restablecer la contraseña")
            return
        
        rut = self.user_table.item(selected_row, 0).text()
        new_password, ok = QInputDialog.getText(self, "Restablecer Contraseña", "Ingrese nueva contraseña:")
        
        if ok and new_password:
            reset_password(rut, new_password)
            QMessageBox.information(self, "Éxito", "Contraseña restablecida correctamente")
    
    def delete_user(self):
        selected_row = self.user_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para eliminar")
            return
        
        rut = self.user_table.item(selected_row, 0).text()
        confirmation = QMessageBox.question(self, "Confirmación", f"¿Está seguro de eliminar el usuario {rut}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if confirmation == QMessageBox.Yes:
            delete_user(rut)
            QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente")
            self.load_users()
    
    def update_company(self):
        # Aquí puedes definir la lógica para actualizar la empresa
        QMessageBox.information(self, "Función", "Función de modificar empresa no implementada.")
