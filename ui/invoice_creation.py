import os
import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QFileDialog, QDateEdit, QHeaderView, QSizePolicy
from PySide6.QtCore import Qt, QDate, QRect
from fpdf import FPDF
import sqlite3
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus.paragraph import ParagraphStyle
from db.database import get_next_quotation_number, save_quotation_number, save_custom_quotation_number, is_quotation_number_used

class QuotationCreationWindow(QWidget):
    def __init__(self, company, role, db_path="db/invoice_manager.db", go_back_callback=None):
        super().__init__()
        self.setWindowTitle(f"Crear Cotización - {company}")
        self.setGeometry(QRect(100, 100, 1400, 800))  # Ajuste de tamaño de ventana
        self.showMaximized()

        self.company = company
        self.role = role
        self.db_path = db_path
        self.go_back_callback = go_back_callback

        # 📌 **Estilos con Alto Contraste**
        self.setStyleSheet("""
            QWidget {
                background-color: #202020;  /* Fondo oscuro */
                color: #FFFFFF;  /* Letras blancas para contraste */
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #FFA500;  /* Naranja brillante */
            }
            QLineEdit, QDateEdit {
                font-size: 16px;
                padding: 5px;
                border: 2px solid #FFA500;  /* Bordes naranjas */
                border-radius: 5px;
                background-color: #303030; /* Fondo más claro */
                color: #FFFFFF; /* Letras blancas */
            }
            QPushButton {
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton#add_item {
                background-color: #28A745; /* Verde */
            }
            QPushButton#calculate_total {
                background-color: #007BFF; /* Azul */
            }
            QPushButton#export_pdf {
                background-color: #FF4500; /* Rojo fuerte */
            }
            QPushButton#back_dashboard {
                background-color: #6C757D; /* Gris */
            }
            QTableWidget {
                background-color: #303030;
                border-radius: 5px;
                font-size: 16px;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #FFA500;
                color: #202020;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
        """)

        main_layout = QVBoxLayout()

        # **Título**
        self.label = QLabel(f"Crear Cotización - {self.company}", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 26px; font-weight: bold; color: #FFA500; margin-bottom: 10px;")
        main_layout.addWidget(self.label)

        # 📌 **Formulario de Datos**
        form_layout = QHBoxLayout()

        self.quotation_number_input = QLineEdit(self)
        self.quotation_number_input.setPlaceholderText("Número de Cotización")
        self.quotation_number_input.setText(get_next_quotation_number())  # Obtiene el último guardado
        self.quotation_number_input.setReadOnly(False)
        form_layout.addWidget(self.quotation_number_input)

        self.client_name_input = QLineEdit(self)
        self.client_name_input.setPlaceholderText("Nombre del Cliente")
        form_layout.addWidget(self.client_name_input)

        self.client_rut_input = QLineEdit(self)
        self.client_rut_input.setPlaceholderText("RUT del Cliente")
        self.client_rut_input.textChanged.connect(self.format_rut)
        form_layout.addWidget(self.client_rut_input)

        self.client_city_input = QLineEdit(self)
        self.client_city_input.setPlaceholderText("Ciudad del Cliente")
        form_layout.addWidget(self.client_city_input)

        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(self.date_input)

        main_layout.addLayout(form_layout)

        # Botón para guardar manualmente el número de cotización
        self.save_quotation_number_button = QPushButton("Guardar Número de Cotización", self)
        self.save_quotation_number_button.clicked.connect(self.save_custom_quotation_number)
        main_layout.addWidget(self.save_quotation_number_button)

        # 📌 **Tabla Mejorada y Ampliada**
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["CANT", "DESCRIPCIÓN", "NETO", "IVA", "TOTAL"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(self.table)

        # 📌 **Botones de Acción**
        button_layout = QHBoxLayout()
        
        self.add_item_button = QPushButton("Agregar Ítem", self)
        self.add_item_button.setObjectName("add_item")
        self.add_item_button.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_item_button)

        self.calculate_total_button = QPushButton("Calcular Total", self)
        self.calculate_total_button.setObjectName("calculate_total")
        self.calculate_total_button.clicked.connect(self.calculate_total)
        button_layout.addWidget(self.calculate_total_button)

        main_layout.addLayout(button_layout)

        # 📌 **Totales con Estilo Mejorado**
        total_layout = QVBoxLayout()

        self.net_total_label = QLabel("Neto: $0.00 CLP", self)
        self.net_total_label.setAlignment(Qt.AlignRight)
        self.net_total_label.setStyleSheet("color: #FFA500; font-size: 18px; font-weight: bold;")
        total_layout.addWidget(self.net_total_label)

        self.iva_total_label = QLabel("IVA: $0.00 CLP", self)
        self.iva_total_label.setAlignment(Qt.AlignRight)
        self.iva_total_label.setStyleSheet("color: #FFA500; font-size: 18px; font-weight: bold;")
        total_layout.addWidget(self.iva_total_label)

        self.total_label = QLabel("Total: $0.00 CLP", self)
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FF4500;")
        total_layout.addWidget(self.total_label)

        main_layout.addLayout(total_layout)

        # 📌 **Navegación**
        navigation_layout = QHBoxLayout()

        self.export_button = QPushButton("Exporta", self)
        self.export_button.setObjectName("export_pdf")
        self.export_button.clicked.connect(self.export_to_pdf)
        navigation_layout.addWidget(self.export_button)

        self.back_button = QPushButton("Volver al Dashboard", self)
        self.back_button.setObjectName("back_dashboard")
        self.back_button.clicked.connect(self.go_back)
        navigation_layout.addWidget(self.back_button)

        

        main_layout.addLayout(navigation_layout)

        self.setLayout(main_layout)

    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()
        self.close()

    def get_company_details(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, address, logo_path, email, rut, phone, city, giro, representative_name, representative_id, representative_email, representative_phone, bank_name, account_type, account_number 
            FROM companies 
            WHERE name = ?
        """, (self.company,))
        company = cursor.fetchone()
        conn.close()

        if company:
            return {
                "name": company[0],
                "address": company[1],
                "logo_path": company[2],
                "email": company[3],
                "rut": company[4],
                "phone": company[5],
                "city": company[6],
                "giro": company[7],
                "representative_name": company[8],
                "representative_id": company[9],
                "representative_email": company[10],
                "representative_phone": company[11],
                "bank_name": company[12],
                "account_type": company[13],
                "account_number": company[14]
            }
        return {}

    def save_custom_quotation_number(self):
        numero_cotizacion = self.quotation_number_input.text()
        try:
            if is_quotation_number_used(numero_cotizacion):
                QMessageBox.warning(self, "Número de Cotización Duplicado", f"El número de cotización {numero_cotizacion} ya ha sido utilizado.")
                return
            save_custom_quotation_number(numero_cotizacion)
            QMessageBox.information(self, "Número de Cotización Guardado", f"El número de cotización {numero_cotizacion} ha sido guardado.")
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_item(self):
        self.table.insertRow(self.table.rowCount())

    def calculate_total(self):
        net_total = 0
        iva_total = 0
        total = 0
        for row in range(self.table.rowCount()):
            try:
                quantity = float(self.table.item(row, 0).text() or 0)
                net_price = float(self.table.item(row, 2).text() or 0)
                iva = int(net_price * 0.19)  # IVA sin decimales
                total_price = int(quantity * net_price + iva)  # Precio total sin decimales

                self.table.setItem(row, 3, QTableWidgetItem(f"{iva:,}".replace(",", ".")))  # Formato CLP
                self.table.setItem(row, 4, QTableWidgetItem(f"{total_price:,}".replace(",", ".")))  # Formato CLP

                net_total += int(quantity * net_price)  # Sumar sin decimales
                iva_total += iva
                total += total_price
            except (ValueError, AttributeError):
                continue

        # Mostrar los totales con formato CLP (separador de miles con puntos)
        self.net_total_label.setText(f"Neto: ${net_total:,} CLP".replace(",", "."))
        self.iva_total_label.setText(f"IVA: ${iva_total:,} CLP".replace(",", "."))
        self.total_label.setText(f"Total: ${total:,} CLP".replace(",", "."))

    def export_to_pdf(self):
        numero_cotizacion = self.quotation_number_input.text()
        fecha_cotizacion = self.date_input.date().toString("yyyyMMdd")
        nombre_cliente = self.client_name_input.text().replace(" ", "_")  # Reemplaza espacios por guiones bajos

        # Concatenar número de cotización y fecha
        nombre_archivo = f"{numero_cotizacion}-{fecha_cotizacion[:4]}-{fecha_cotizacion[4:6]}-{nombre_cliente}.pdf"

        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Cotización", nombre_archivo, "PDF Files (*.pdf)")
        if file_path:
            if not file_path.endswith(".pdf"):
                file_path += ".pdf"

            company_details = self.get_company_details()  # Retrieve company details

            doc = SimpleDocTemplate(file_path, pagesize=letter)
            doc.title = f"{numero_cotizacion}-{fecha_cotizacion[:4]}-{fecha_cotizacion[4:6]}-{nombre_cliente}"
            doc.author = company_details.get('representative_name', 'N/A')

            elements = []
            styles = getSampleStyleSheet()

            # --- ENCABEZADO: LOGO IZQUIERDA + DATOS REPRESENTANTE MÁS A LA DERECHA ---
            logo_path = company_details.get("logo_path")
            if logo_path and os.path.exists(logo_path):
                logo = Image(logo_path, width=90, height=90)
            else:
                logo = Paragraph("", styles["Normal"])  # Espacio en blanco si no hay logo

            rep_legal_info = Paragraph(f"""
                <div align='right'>
            <b>{company_details.get('name', 'N/A')}</b><br/>
            <b>R.U.T.:</b> {company_details.get('rut', 'N/A')}<br/>
            <b>DIRECCIÓN:</b> {company_details.get('address', 'N/A')}<br/>
            <b>TELÉFONO:</b> {company_details.get('phone', 'N/A')}<br/>
            <b>CIUDAD:</b> {company_details.get('city', 'N/A')}<br/>
            <b>GIRO:</b> {company_details.get('giro', 'N/A')}<br/>
            <b>REP.LEGAL:</b> {company_details.get('representative_name', 'N/A')}<br/>
            <b>MAIL:</b> {company_details.get('representative_email', 'N/A')}
            </div>
            """, styles["Normal"])

            # Ajustar la tabla para mover los datos más a la derecha y alinearlos más arriba
            header_table = Table([[logo, "", rep_legal_info]], colWidths=[80, 200, 300])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alineación vertical superior
                ('LEFTPADDING', (0, 0), (0, 0), 50),  # Mueve el logo más a la derecha
                ('LEFTPADDING', (2, 0), (2, 0), 100),  # Mueve el texto más a la derecha
                ('TOPPADDING', (0, 0), (-1, -1), -20),  # Reduce el padding superior
            ]))
            elements.append(header_table)

            elements.append(Spacer(1, 20))

            # --- NÚMERO DE COTIZACIÓN Y FECHA ---
            folio_fecha = f"{numero_cotizacion}-{fecha_cotizacion[:4]}-{fecha_cotizacion[4:6]}"
            quotation_info = Table([
                [Paragraph(f"<b>Numero de serie :</b> {folio_fecha}", styles["Normal"])]
            ], colWidths=[450, 50])  # Se aumenta la primera columna para evitar desplazamientos

            quotation_info.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Mantener alineación a la izquierda
                ('LEFTPADDING', (0, 0), (-1, -1), -25),  # Llevarlo más a la izquierda
                ('TOPPADDING', (0, 0), (-1, -1), -50),  # Mantener alineado con el logo
            ]))

            elements.append(quotation_info)
            elements.append(Spacer(1, 10))  # Espaciado mínimo para correcta distribución

            # --- DATOS DEL CLIENTE: DOS COLUMNAS ---
            client_data = [
                [Paragraph(f"<b>Nombre:</b> {self.client_name_input.text()}", ParagraphStyle('Normal', textColor=colors.gray)),
                Paragraph(f"<b>Rut:</b> {self.client_rut_input.text()}", ParagraphStyle('Normal', textColor=colors.gray))],
                [Paragraph(f"<b>Ciudad:</b> {self.client_city_input.text()}", ParagraphStyle('Normal', textColor=colors.gray))]
            ]
            client_table = Table(client_data, colWidths=[250, 250])
            elements.append(client_table)

            elements.append(Spacer(1, 20))

            # --- TABLA DE PRODUCTOS ---
            table_data = [["CANT", "DETALLE", "NETO", "IVA", "TOTAL"]]  # Encabezados

            for row in range(self.table.rowCount()):
                cantidad = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
                detalle = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                neto = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
                iva = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
                total = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
                table_data.append([cantidad, detalle, neto, iva, total])

            # Aplicar estilo de letras naranjo para encabezados y negro para datos
            table_style = TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.orange),  # Encabezados en naranjo
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Datos en negro
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Fondo para el encabezado
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en negrita para encabezados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Fuente normal para datos
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),  # Borde general de la tabla (más grueso)
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Líneas internas más suaves
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 5),  # Simulación de bordes redondeados
            ])

            # CREACIÓN DE TABLA
            table = Table(table_data, colWidths=[50, 250, 80, 80, 80])
            table.setStyle(table_style)

            elements.append(table)
            elements.append(Spacer(1, 20))

            # --- SECCIÓN INFERIOR ---
            footer_table = Table([
                [Paragraph("<b><font color='orange'>TIEMPO DE ENTREGA A CONVENIR</font></b>", styles["Normal"]),
                Paragraph("<b><font color='orange'>Transferencia / Depósito Bancario</font></b>", styles["Normal"])],
                [Paragraph("<b><font color='gray'>ENVIAR ORDEN DE COMPRA</font></b>", styles["Normal"]),
                Paragraph(f"<b><font color='orange'>Banco:</font></b> <font color='orange'>{company_details.get('bank_name', 'N/A')}</font>", styles["Normal"])],
                [Paragraph("<b><font color='gray'>VERIFICAR VALORES NETOS</font></b>", styles["Normal"]),
                Paragraph(f"<b><font color='orange'>Cuenta:</font></b> <font color='orange'>{company_details.get('account_number', 'N/A')}</font>", styles["Normal"])],
                ["", Paragraph(f"<b><font color='orange'>Tipo de Cuenta:</font></b> <font color='orange'>{company_details.get('account_type', 'N/A')}</font>", styles["Normal"])],
                ["", Paragraph(f"<font color='orange'>{company_details.get('representative_name', 'N/A')}</font>", styles["Normal"])],
                ["", Paragraph(f"<font color='orange'>{company_details.get('rut', 'N/A')}</font>", styles["Normal"])],
                ["", Paragraph(f"<font color='orange'>{company_details.get('representative_email', 'N/A')}</font>", styles["Normal"])],
            ], colWidths=[250, 250])
            elements.append(footer_table)

            elements.append(Spacer(1, 10))

            # --- TOTALES EN LA PARTE INFERIOR DERECHA ---
            totals_table = Table([
                ["", "NETO", self.net_total_label.text().replace("Neto: $", "").replace(" CLP", "").strip()],
                ["", "I.V.A.", self.iva_total_label.text().replace("IVA: $", "").replace(" CLP", "").strip()],
                ["", "TOTAL", self.total_label.text().replace("Total: $", "").replace(" CLP", "").strip()]
            ], colWidths=[250, 100, 100])
            elements.append(totals_table)

            elements.append(Spacer(1, 20))

            # --- SECCIÓN DE CONTACTO Y AGRADECIMIENTO ---
            contact_info = Paragraph(f"""
                <div align='center'>
                <b>Si tienes alguna pregunta sobre esta cotización, contáctanos:</b><br/>
                <b>Representante:</b> {company_details.get('representative_name', 'N/A')}<br/>
                <b>Teléfono:</b> {company_details.get('representative_phone', 'N/A')}<br/>
                <b>Email:</b> {company_details.get('email', 'N/A')}<br/>
                <b>¡Gracias por su confianza!</b>
                </div>
            """, styles["Normal"])

            # Enmarcar la sección de contacto
            contact_table = Table([[contact_info]], colWidths=[500])
            contact_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('PADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(contact_table)

            # GENERAR PDF
            try:
                doc.build(elements)
                QMessageBox.information(self, "PDF Exportado", f"La cotización ha sido guardada en:\n{file_path}")

                # Incrementar el número de cotización en la base de datos
                save_quotation_number()

                # Obtener y asignar el siguiente número para la próxima cotización
                self.quotation_number_input.setText(get_next_quotation_number())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo PDF:\n{str(e)}")

    def format_rut(self, text):
        """Formatea el RUT en formato chileno."""
        clean_rut = re.sub(r'[^0-9Kk]', '', text)

        if len(clean_rut) < 2:
            self.client_rut_input.setText(text)  # No aplicar formato si es muy corto
            return

        # Separar número y dígito verificador
        num_part = clean_rut[:-1]  # Todo menos el último dígito
        dv = clean_rut[-1]  # Último dígito

        # Insertar puntos cada tres dígitos desde el final
        formatted_num = ".".join(re.findall(r'\d{1,3}', num_part[::-1]))[::-1]

        # Formato final con guion
        formatted_text = f"{formatted_num}-{dv.upper()}"

        # Asignar el texto formateado al campo de entrada
        self.client_rut_input.setText(formatted_text)