# ui/change_password.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QFrame
from PySide6.QtCore import Qt
from utils.auth import update_user_password, authenticate_user


class ChangePasswordWindow(QWidget):
    def __init__(self, username=None):
        super().__init__()
        self.setWindowTitle("Cambiar Contraseña")
        self.setFixedSize(450, 450)

        self.username = username  # El nombre de usuario que cambiará la contraseña

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        container_frame = QFrame(self)
        container_frame.setStyleSheet("background-color: #23272A; border-radius: 15px; padding: 30px;")
        container_frame.setFixedSize(450, 450)

        container_layout = QVBoxLayout(container_frame)
        container_layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Cambiar Contraseña", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        container_layout.addWidget(self.label)

        self.old_password_entry = QLineEdit(self)
        self.old_password_entry.setPlaceholderText("Ingrese contraseña actual")
        self.old_password_entry.setEchoMode(QLineEdit.Password)
        self.old_password_entry.setFixedWidth(300)
        self.old_password_entry.setStyleSheet("padding: 10px; border-radius: 8px; background-color: #40444B; color: #FFFFFF;")
        container_layout.addWidget(self.old_password_entry)

        self.new_password_entry = QLineEdit(self)
        self.new_password_entry.setPlaceholderText("Ingrese nueva contraseña")
        self.new_password_entry.setEchoMode(QLineEdit.Password)
        self.new_password_entry.setFixedWidth(300)
        self.new_password_entry.setStyleSheet("padding: 10px; border-radius: 8px; background-color: #40444B; color: #FFFFFF;")
        container_layout.addWidget(self.new_password_entry)

        self.confirm_password_entry = QLineEdit(self)
        self.confirm_password_entry.setPlaceholderText("Confirme nueva contraseña")
        self.confirm_password_entry.setEchoMode(QLineEdit.Password)
        self.confirm_password_entry.setFixedWidth(300)
        self.confirm_password_entry.setStyleSheet("padding: 10px; border-radius: 8px; background-color: #40444B; color: #FFFFFF;")
        container_layout.addWidget(self.confirm_password_entry)

        self.change_password_button = QPushButton("Cambiar Contraseña", self)
        self.change_password_button.setFixedWidth(300)
        self.change_password_button.setStyleSheet("padding: 10px; border-radius: 8px; background-color: #4CAF50; color: #FFFFFF; font-weight: bold;")
        self.change_password_button.clicked.connect(self.change_password)
        container_layout.addWidget(self.change_password_button)

        main_layout.addWidget(container_frame, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)

    def change_password(self):
        old_password = self.old_password_entry.text()
        new_password = self.new_password_entry.text()
        confirm_password = self.confirm_password_entry.text()

        if not old_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Las nuevas contraseñas no coinciden")
            return

        if len(new_password) < 6 or not any(char.isupper() for char in new_password):
            QMessageBox.warning(self, "Error", "La nueva contraseña debe tener al menos 6 caracteres y una mayúscula")
            return

        # Verificar la contraseña actual
        if not authenticate_user(self.username, old_password):
            QMessageBox.warning(self, "Error", "La contraseña actual es incorrecta")
            print(f"Error: La contraseña actual para el usuario {self.username} es incorrecta")
            return

        # Actualizar la contraseña
        try:
            update_user_password(self.username, new_password)
            QMessageBox.information(self, "Éxito", "La contraseña se ha cambiado correctamente")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            print(f"Error al actualizar la contraseña para el usuario {self.username}: {str(e)}")
