from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox, QTabWidget, QTextBrowser, QLineEdit
from PySide6.QtCore import Qt
import datetime
from fpdf import FPDF

class SupportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soporte")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        self.label = QLabel("Centro de Soporte", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.label)

        # Crear un QTabWidget para las pestañas
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Pestaña de Guía de Usuario
        self.guide_tab = QWidget()
        self.guide_layout = QVBoxLayout(self.guide_tab)
        
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Buscar en la Guía de Usuario...")
        self.search_bar.textChanged.connect(self.search_in_guide)
        self.guide_layout.addWidget(self.search_bar)

        self.guide_text = QTextBrowser(self)
        self.full_guide_content = self.get_user_guide()
        self.guide_text.setHtml(self.full_guide_content)
        self.guide_layout.addWidget(self.guide_text)

        self.export_button = QPushButton("Exportar Guía a PDF", self)
        self.export_button.clicked.connect(self.export_guide_to_pdf)
        self.guide_layout.addWidget(self.export_button)

        self.tabs.addTab(self.guide_tab, "Guía de Usuario")

        # Pestaña de Enviar Mensaje
        self.message_tab = QWidget()
        self.message_layout = QVBoxLayout(self.message_tab)
        self.description = QLabel("Describe tu problema o pregunta a continuación:", self)
        self.message_layout.addWidget(self.description)
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("Escribe tu mensaje aquí...")
        self.message_layout.addWidget(self.text_edit)
        self.submit_button = QPushButton("Enviar", self)
        self.submit_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.submit_button.clicked.connect(self.submit_support_request)
        self.message_layout.addWidget(self.submit_button)
        self.tabs.addTab(self.message_tab, "Enviar Mensaje")

        self.setLayout(layout)

    def get_user_guide(self):
        return """
        <h1>Guía de Usuario</h1>
        <h2>Introducción</h2>
        <p>Bienvenido al sistema de gestión de cotizaciones. Esta guía le ayudará a entender cómo usar el sistema y resolver problemas comunes.</p>
        
        <h2>Cómo Crear una Cotización</h2>
        <ol>
            <li>Haga clic en "Crear Cotización" en el panel principal.</li>
            <li>Complete los detalles del cliente y los ítems de la cotización.</li>
            <li>Haga clic en "Guardar" para guardar la cotización.</li>
        </ol>
        
        <h2>Sistema de Folios</h2>
        <p>El sistema de cotizaciones permite la administración de folios de la siguiente manera:</p>
        <ul>
            <li>El usuario puede ingresar un número de folio manualmente.</li>
            <li>Debe presionar el botón "Guardar Número de Cotización" para establecerlo como punto de inicio.</li>
            <li>Después de exportar una cotización, el número se incrementa automáticamente.</li>
        </ul>
        
        <h2>Cómo Gestionar Archivos</h2>
        <ol>
            <li>Haga clic en "Gestionar Archivos" en el panel principal.</li>
            <li>Seleccione el archivo que desea gestionar.</li>
            <li>Seleccione la categoría correspondiente para el archivo.</li>
            <li>Realice las acciones necesarias (subir, descargar, eliminar).</li>
        </ol>
        <p>Es importante seleccionar la categoría correcta para asegurar que el archivo se gestione adecuadamente dentro del sistema.</p>
        """
    
    def submit_support_request(self):
        message = self.text_edit.toPlainText()
        if message.strip():
            self.save_support_message(message)
            QMessageBox.information(self, "Soporte", "Tu mensaje ha sido enviado. Nos pondremos en contacto contigo pronto.")
            self.text_edit.clear()
        else:
            QMessageBox.warning(self, "Error", "Por favor, escribe un mensaje antes de enviar.")

    def save_support_message(self, message):
        with open("support_messages.txt", "a", encoding="utf-8") as file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"[{timestamp}] {message}\n")
    
    def search_in_guide(self):
        search_text = self.search_bar.text().lower()
        if search_text:
            highlighted_text = self.full_guide_content.replace(search_text, f'<span style="background-color: yellow">{search_text}</span>')
            self.guide_text.setHtml(highlighted_text)
        else:
            self.guide_text.setHtml(self.full_guide_content)

    def export_guide_to_pdf(self):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, self.guide_text.toPlainText())
        pdf.output("Guia_de_Usuario.pdf")
        QMessageBox.information(self, "Exportación", "La guía ha sido exportada a PDF exitosamente.")
