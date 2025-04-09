import shutil
import sqlite3
import os
import sys
import glob

def get_project_root():
    """Get the root directory of the project regardless of how the app is executed."""
    # Handle both development environment and bundled app
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        return os.path.dirname(sys.executable)
    else:
        # Running in development environment
        # Get the directory where the script is located
        current_path = os.path.dirname(os.path.abspath(__file__))
        # Navigate to the project root (one level up from db/)
        return os.path.dirname(current_path)

def get_db_path():
    """Get full path to database file."""
    root_dir = get_project_root()
    db_dir = os.path.join(root_dir, "db")
    os.makedirs(db_dir, exist_ok=True)  # Ensure db directory exists
    return os.path.join(db_dir, "invoice_manager.db")

def get_db_connection():
    """Get connection to SQLite database with proper path handling."""
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def validate_and_create_db():
    """Check if database exists, create it and initialize tables if it doesn't."""
    db_path = get_db_path()
    db_exists = os.path.isfile(db_path)
    
    if not db_exists:
        print(f"Database not found. Creating new database at: {db_path}")
        # Create empty database file
        conn = sqlite3.connect(db_path)
        conn.close()
        
        # Initialize tables
        initialize_db()
        
        # Load data from SQL files
        load_sql_data()
        return False
    else:
        print(f"Database found at: {db_path}")
        return True

def load_sql_data():
    """Load data directly from Python code instead of SQL files."""
    print("Loading data directly from Python...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Companies data
        print("Loading companies data...")
        companies_data = """INSERT INTO companies(id,name,address,logo_path,email,rut,phone,city,giro,representative_name,representative_id,representative_email,representative_phone,bank_name,account_type,account_number) VALUES(1,'Agencia Onblack Spa','Doctor Cossio #333','images/logos/OnBlack.png','agenciaonblack@gmail.com','77.203.666-3','43-2492700','Los Ángeles,Chile','Marketing y Publicidad','Cristian Montero Seguel','17.870.191-6','cristian@agenciaonblack.cl ','+569-65971427','Santander','Corriente','0-000-9679550-5'),(2,'Oficina virtual Spa','Doctor Cossio #333','images/logos/OnOffice(1).png','contacto@onoffice.cl','77.239.418-7','43-2492700','Los Ángeles, Chile','Arriendo de oficinas virtuales','Cristian Montero Seguel','17.870.191-6','contacto@onoffice.cl','+569-65971427','Santander','Vista','0-070-18-70288-0'),(4,'ArtePrint','Doctor Cossio #333','images/logos/ArtePrint.png','publicidadarteprint@gmail.com ','12.262.345-9','4322492700','Los Ángeles,chile','Publicidad e imprenta','Felipe M. Muñoz Sáez','12.262.345-9','felipe@publicidadarteprint.cl','+56979692604','Estado','Vista','537-000-27-411')"""
        
        # Users data (add your users data here from the users_users.sql file)
        print("Loading users data...")
        users_data = """INSERT INTO users(id,rut,password,role) VALUES(10,'19.372.940-1','$2b$12$ldNauDPzX3y8TeuGhnSsiuN1lx5Jz2SEGDn3jk9YLyHq/Ydatn25m','User'),(15,'20.954.371-0','$2b$12$MOUvQzIVFrnGR51zbOyasew698fQ7Xot5qiHAlxuvDzCg3tmBZx0y','Admin'),(16,'15.628.651-6','$2b$12$piqVZEDvvV2Oknl34/9H7O1EJNg9XDq9yphr9GM0IYtxgc276IzFK','User'),(17,'17.870.191-6','$2b$12$3H4w0vHxfGagVF3rjNjfPe8M7KPHXN7fz91mh/VHALCcSTKDXdupy','User'),(18,'12.262.345-8','$2b$12$j4UzjtKb.c0cQG4m5Ex6mumalHnrTVQhg/3MmA4EWe76dkNWM6Sd6','User')"""
        
        # User-Companies relationships
        print("Loading user-companies relationships...")
        user_companies_data = """INSERT INTO user_companies(user_id,company_id) VALUES(1,3),(2,1),(2,2),(3,3),(4,2),(4,1),(5,2),(5,1),(6,2),(6,1),(5,3),(7,3),(7,1),(7,2),(8,1),(8,2),(9,1),(9,2),(10,2),(10,1),(11,3),(12,2),(12,1),(13,2),(13,1),(13,3),(14,3),(15,3),(15,2),(15,1),(16,4),(17,2),(17,1),(18,2),(18,1),(18,4)"""
        
        # Execute all statements
        for statement in [companies_data, users_data, user_companies_data]:
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        print("All data loaded successfully")
    except sqlite3.Error as e:
        print(f"SQLite error loading data: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Error loading data: {e}")
        conn.rollback()
    finally:
        conn.close()

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Tabla de empresas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                address TEXT NOT NULL,
                logo_path TEXT NOT NULL,
                email TEXT,
                rut TEXT NOT NULL UNIQUE,
                phone TEXT,
                city TEXT NOT NULL,
                giro TEXT NOT NULL,
                representative_name TEXT NOT NULL,
                representative_id TEXT NOT NULL,
                representative_email TEXT NOT NULL,
                representative_phone TEXT NOT NULL,
                bank_name TEXT NOT NULL,
                account_type TEXT CHECK(account_type IN ('Ahorro', 'Corriente', 'Vista')) NOT NULL,
                account_number TEXT NOT NULL
            )
        ''')

        # Tabla de usuarios (inicio de sesión con RUT)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rut TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Admin', 'User', 'Viewer'))
            )
        ''')

        # Relación usuario-empresa (para restringir acceso por empresa)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_companies (
                user_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, company_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')

        # Tabla de cotizaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                client_name TEXT NOT NULL,
                project_name TEXT NOT NULL,
                date TEXT NOT NULL,
                net_total REAL NOT NULL,
                iva REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')

        # Detalles de las cotizaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotation_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quotation_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                description TEXT NOT NULL,
                net REAL NOT NULL,
                iva REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (quotation_id) REFERENCES quotations (id)
            )
        ''')

        # Tabla para almacenar el número de cotización actual
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotation_numbers (
                id INTEGER PRIMARY KEY,
                current_number INTEGER NOT NULL
            )
        ''')

        # Insertar el número inicial de cotización si no existe
        cursor.execute('''
            INSERT INTO quotation_numbers (id, current_number)
            SELECT 1, 1 WHERE NOT EXISTS (SELECT 1 FROM quotation_numbers WHERE id = 1)
        ''')

        # Asegurar que la carpeta de imágenes existe
        root_dir = get_project_root()
        logos_dir = os.path.join(root_dir, "images", "logos")
        os.makedirs(logos_dir, exist_ok=True)
        
        conn.commit()
        print("Database tables created successfully")

    finally:
        conn.close()

def add_company(name, address, logo_path, email, rut, phone, city, giro, representative_name, representative_id, representative_email, representative_phone, bank_name, account_type, account_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO companies (name, address, logo_path, email, rut, phone, city, giro, representative_name, representative_id, representative_email, representative_phone, bank_name, account_type, account_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (name, address, logo_path, email, rut, phone, city, giro, representative_name, representative_id, representative_email, representative_phone, bank_name, account_type, account_number)
    )
    company_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return company_id

def add_user(rut, password, role):
    """Crea un nuevo usuario."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (rut, password, role) VALUES (?, ?, ?)',
        (rut, password, role)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def assign_user_to_company(user_rut, company_rut):
    """Asigna un usuario a una empresa según el RUT."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM users WHERE rut = ?', (user_rut,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise ValueError("Usuario no encontrado.")

    cursor.execute('SELECT id FROM companies WHERE rut = ?', (company_rut,))
    company = cursor.fetchone()
    if not company:
        conn.close()
        raise ValueError("Empresa no encontrada.")

    cursor.execute(
        'INSERT INTO user_companies (user_id, company_id) VALUES (?, ?)',
        (user["id"], company["id"])
    )

    conn.commit()
    conn.close()

def save_logo(file_path):
    logo_dir = os.path.join(get_project_root(), "images", "logos")
    os.makedirs(logo_dir, exist_ok=True)
    file_name = os.path.basename(file_path)
    destination = os.path.join(logo_dir, file_name)
    shutil.copy(file_path, destination)
    return destination

def get_company_by_rut(rut):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM companies WHERE rut = ?", (rut,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "name": row["name"],
            "address": row["address"],
            "logo_path": row["logo_path"],
            "email": row["email"],
            "phone": row["phone"],
            "city": row["city"],
            "giro": row["giro"],
            "representative_name": row["representative_name"],
            "representative_id": row["representative_id"],
            "representative_email": row["representative_email"],
            "representative_phone": row["representative_phone"],
            "bank_name": row["bank_name"],
            "account_type": row["account_type"],
            "account_number": row["account_number"],
        }
    
    print(f"⚠️ No se encontró la empresa con RUT {rut}")  # <-- Depuración
    return None

def get_next_quotation_number():
    """Obtiene el último número de cotización desde la base de datos sin incrementarlo automáticamente."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT current_number FROM quotation_numbers WHERE id = 1")
    result = cursor.fetchone()

    if result:
        current_number = str(result["current_number"]).zfill(4)  # Usa el último guardado
    else:
        current_number = "0001"  # Si no hay registros, inicia en 0001

    conn.close()
    return current_number

def is_quotation_number_used(number):
    """Verifica si el número de cotización ya ha sido utilizado."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM quotations WHERE id = ?", (number,))
    result = cursor.fetchone()

    conn.close()
    return result is not None

def save_custom_quotation_number(number):
    """Guarda manualmente el número de cotización ingresado por el usuario como el nuevo valor en la base de datos."""
    if is_quotation_number_used(number):
        raise ValueError("El número de cotización ya ha sido utilizado.")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE quotation_numbers SET current_number = ? WHERE id = 1", (int(number),))

    conn.commit()
    conn.close()

def save_quotation_number():
    """Incrementa el número de cotización en la base de datos después de exportar."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener el número actual
    cursor.execute("SELECT current_number FROM quotation_numbers WHERE id = 1")
    result = cursor.fetchone()

    if result:
        new_number = result["current_number"] + 1  # Incrementar el número
        cursor.execute("UPDATE quotation_numbers SET current_number = ? WHERE id = 1", (new_number,))
    else:
        new_number = 1  # Si no hay registros, inicia en 1
        cursor.execute("INSERT INTO quotation_numbers (id, current_number) VALUES (1, ?)", (new_number,))

    conn.commit()
    conn.close()
    
    return str(new_number).zfill(4)  # Retornar el número formateado con ceros a la izquierda

def delete_company_by_name(name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM companies WHERE name = ?", (name,))
        conn.commit()
        rows_deleted = cursor.rowcount
        conn.close()
        return rows_deleted > 0

def delete_company_by_rut(rut):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE rut = ?", (rut,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted > 0
