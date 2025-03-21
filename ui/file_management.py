import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QLineEdit, QComboBox, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, QCheckBox, QSizePolicy, QFrame, QFormLayout, QHeaderView
)
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtCore import QUrl, Qt

class FileManagementWindow(QWidget):
    def __init__(self, company, role, parent_window=None, go_back_callback=None):
        super().__init__()
        self.setWindowTitle(f"Gestionar Archivos - {company} ({role})")
        self.setGeometry(0, 0, 1600, 900)
        self.showMaximized()
        self.setStyleSheet("background-color: #2C2F33; color: #FFFFFF; font-size: 14px;")

        self.company = company
        self.role = role
        self.parent_window = parent_window
        self.go_back_callback = go_back_callback
        self.file_dir = f"files/{self.company}"
        os.makedirs(self.file_dir, exist_ok=True)

        self.categories = ['Contrato', 'Licencia Medica', 'Anexo de Contrato', 'Boletas',
                           'Facturas', 'Liquidaciones', 'Finiquitos', 'Cotizaciones']

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.create_nav_bar())
        main_layout.addWidget(self.create_file_table())
        main_layout.addLayout(self.create_upload_form())
        main_layout.addLayout(self.create_buttons())

        self.refresh_file_list()
        self.setLayout(main_layout)

    def create_nav_bar(self):
        nav_layout = QHBoxLayout()

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("🔍 Buscar archivos...")
        self.search_bar.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #555555; background-color: #40444B;")
        self.search_bar.textChanged.connect(self.filter_files)
        nav_layout.addWidget(self.search_bar)

        self.filter_category_box = QComboBox(self)
        self.filter_category_box.addItem("Todos")
        self.filter_category_box.addItems(self.categories)
        self.filter_category_box.setStyleSheet("padding: 8px; border-radius: 5px; background-color: #40444B;")
        self.filter_category_box.currentIndexChanged.connect(self.filter_files)
        nav_layout.addWidget(self.filter_category_box)

        self.order_date_box = QComboBox(self)
        self.order_date_box.addItems(["Ordenar por fecha", "Ascendente", "Descendente"])
        self.order_date_box.setStyleSheet("padding: 8px; border-radius: 5px; background-color: #40444B;")
        self.order_date_box.currentIndexChanged.connect(self.sort_by_date)
        nav_layout.addWidget(self.order_date_box)

        return nav_layout

    def create_file_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["✅", "Nombre del Archivo", "Categoría", "Fecha de Subida"])
        self.table.setStyleSheet("background-color: #40444B; color: #FFFFFF; border: 1px solid #555555;")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return self.table

    def create_upload_form(self):
        upload_layout = QHBoxLayout()

        self.upload_category_box = QComboBox(self)
        self.upload_category_box.addItems(self.categories)
        self.upload_category_box.setStyleSheet("padding: 8px; border-radius: 5px; background-color: #40444B;")
        upload_layout.addWidget(QLabel("Categoría:"))
        upload_layout.addWidget(self.upload_category_box)

        self.upload_button = QPushButton("📤 Subir Archivo", self)
        self.upload_button.setStyleSheet("padding: 8px; border-radius: 5px; background-color: #4CAF50; color: white;")
        self.upload_button.clicked.connect(self.upload_file)
        upload_layout.addWidget(self.upload_button)

        return upload_layout

    def create_buttons(self):
        button_layout = QHBoxLayout()

        self.view_button = self.create_button("👁️ Ver PDF", "#007BFF", self.view_pdf)
        button_layout.addWidget(self.view_button)

        self.download_button = self.create_button("⬇️ Descargar", "#17A2B8", self.download_files)
        button_layout.addWidget(self.download_button)

        self.delete_button = self.create_button("🗑️ Eliminar", "#DC3545", self.delete_files)
        button_layout.addWidget(self.delete_button)

        self.back_button = self.create_button("🔙 Volver", "#6C757D", self.go_back)
        button_layout.addWidget(self.back_button)

        return button_layout

    def create_button(self, text, color, callback):
        button = QPushButton(text, self)
        button.setStyleSheet(f"padding: 8px; border-radius: 5px; background-color: {color}; color: white;")
        button.clicked.connect(callback)
        return button

    def filter_files(self):
        search_text = self.search_bar.text().lower()
        category_filter = self.filter_category_box.currentText()

        for row in range(self.table.rowCount()):
            item_name = self.table.item(row, 1).text().lower()
            item_category = self.table.item(row, 2).text()

            if (category_filter == "Todos" or item_category == category_filter) and search_text in item_name:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def sort_by_date(self):
        order = self.order_date_box.currentText()
        if order == "Ascendente":
            self.table.sortItems(3, Qt.AscendingOrder)
        elif order == "Descendente":
            self.table.sortItems(3, Qt.DescendingOrder)

    def refresh_file_list(self):
        self.table.setRowCount(0)
        files = os.listdir(self.file_dir)
        for file_name in files:
            category = file_name.split('_')[0]
            upload_time = datetime.fromtimestamp(os.path.getctime(os.path.join(self.file_dir, file_name))).strftime('%Y-%m-%d %H:%M:%S')
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            checkbox = QCheckBox()
            self.table.setCellWidget(row_position, 0, checkbox)
            self.table.setItem(row_position, 1, QTableWidgetItem(file_name))
            self.table.setItem(row_position, 2, QTableWidgetItem(category))
            self.table.setItem(row_position, 3, QTableWidgetItem(upload_time))

    def upload_file(self):
        category = self.upload_category_box.currentText()
        file_path, _ = QFileDialog.getOpenFileName(self, "Subir Archivo", "", "Archivos PDF (*.pdf)")
        if file_path:
            file_name = f"{category}_{os.path.basename(file_path)}"
            destination = os.path.join(self.file_dir, file_name)
            try:
                with open(file_path, 'rb') as src_file, open(destination, 'wb') as dest_file:
                    dest_file.write(src_file.read())
                QMessageBox.information(self, "Éxito", "Archivo subido exitosamente")
                self.refresh_file_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Fallo al subir el archivo: {str(e)}")

    def view_pdf(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            file_name = selected_items[0].text()
            file_path = os.path.join(self.file_dir, file_name)
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        else:
            QMessageBox.warning(self, "Error", "Por favor, seleccione un archivo para ver")

    def download_files(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            for item in selected_items:
                file_name = item.text()
                file_path = os.path.join(self.file_dir, file_name)
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        else:
            QMessageBox.warning(self, "Error", "Por favor, seleccione archivos para descargar")

    def delete_files(self):
        selected_files = [self.table.item(row, 1).text() for row in range(self.table.rowCount()) if self.table.cellWidget(row, 0).isChecked()]

        if selected_files:
            for file_name in selected_files:
                file_path = os.path.join(self.file_dir, file_name)
                try:
                    os.remove(file_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Fallo al eliminar el archivo: {str(e)}")
            QMessageBox.information(self, "Éxito", "Archivos eliminados exitosamente")
            self.refresh_file_list()
        else:
            QMessageBox.warning(self, "Error", "Por favor, seleccione archivos para eliminar")

    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()
        self.close()
