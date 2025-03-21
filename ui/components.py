# components.py
from PySide6.QtWidgets import QPushButton, QLineEdit, QComboBox, QTableWidget, QSizePolicy

# Botones Personalizados
def create_button(text, color, callback=None):
    button = QPushButton(text)
    button.setStyleSheet(f"padding: 10px; border-radius: 5px; background-color: {color}; color: #FFFFFF;")
    if callback:
        button.clicked.connect(callback)
    return button

# Campos de Entrada (QLineEdit)
def create_input(placeholder=""):
    input_field = QLineEdit()
    input_field.setPlaceholderText(placeholder)
    input_field.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #555555; background-color: #40444B; color: #FFFFFF;")
    return input_field

# ComboBox Personalizado
def create_combobox(items):
    combobox = QComboBox()
    combobox.addItems(items)
    combobox.setStyleSheet("padding: 10px; border-radius: 5px; background-color: #40444B; color: #FFFFFF;")
    return combobox

# Tablas Personalizadas
def create_table(headers):
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setStyleSheet("background-color: #40444B; color: #FFFFFF; border: 1px solid #555555;")
    table.horizontalHeader().setStyleSheet("background-color: #555555; color: #FFFFFF;")
    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    return table
