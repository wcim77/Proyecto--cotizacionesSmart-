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
    """Load data from SQL files in the data directory."""
    root_dir = get_project_root()
    data_dir = os.path.join(root_dir, "db", "data")
    
    if not os.path.exists(data_dir):
        print(f"Data directory not found at: {data_dir}")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all SQL files in the data directory
    sql_files = glob.glob(os.path.join(data_dir, "*.sql"))
    
    if not sql_files:
        print(f"No SQL files found in: {data_dir}")
        conn.close()
        return
    
    try:
        for sql_file in sql_files:
            file_name = os.path.basename(sql_file)
            print(f"Loading data from: {file_name}")
            
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                
            # Split by semicolon to execute multiple statements
            statements = sql_content.split(';')
            
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
            
            print(f"Successfully loaded: {file_name}")
        
        conn.commit()
        print("All SQL data loaded successfully")
    except sqlite3.Error as e:
        print(f"SQLite error loading data: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Error loading SQL data: {e}")
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
