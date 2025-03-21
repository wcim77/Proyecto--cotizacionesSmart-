import json
import os
import bcrypt
import sqlite3
import random
import string
from db.database import get_db_connection

CONFIG_FILE = "config_dev.json"

def is_developer_mode():
    """ Verifica si el modo programador está activado a través del archivo de configuración. """
    print("Verificando modo desarrollador...")
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
                developer_mode = config.get("developer_mode", False)
                print(f"Modo desarrollador: {developer_mode}")
                return developer_mode
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error al leer el archivo de configuración: {e}")
            return False
    print("Archivo de configuración no encontrado.")
    return False

def get_all_companies():
    """ Obtiene todas las empresas registradas. """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, rut FROM companies')
    companies = cursor.fetchall()
    conn.close()
    return [{"name": row["name"], "rut": row["rut"]} for row in companies]

def get_companies_by_rut(rut):
    """ Obtiene las empresas a las que tiene acceso un usuario según su RUT. """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.name 
        FROM companies c
        JOIN user_companies uc ON c.id = uc.company_id
        JOIN users u ON uc.user_id = u.id
        WHERE u.rut = ?
    ''', (rut,))
    companies = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return companies

def get_all_users():
    """ Obtiene todos los usuarios registrados. """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT rut, role FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def hash_password(password):
    """ Encripta una contraseña. """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """ Verifica si una contraseña coincide con su hash. """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def authenticate_user(rut, password):
    """ Autentica al usuario y redirige según su rol. """
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT rut, password, role FROM users WHERE rut = ?', (rut,)).fetchone()
    conn.close()
    
    if user and check_password(password, user["password"]):
        role = user["role"].lower()
        if role == "admin":
            return {"rut": user["rut"], "role": "Programador", "dashboard": "programmer"}
        else:
            return {"rut": user["rut"], "role": role, "dashboard": "user"}

    # Modo programador activado manualmente en config_dev.json
    if is_developer_mode():
        print("🔹 Accediendo en MODO PROGRAMADOR...")
        return {"rut": "DEV", "role": "Programador", "dashboard": "programmer"}

    return None  # Si no se encuentra el usuario, retorna None

def add_user(rut, password, role):
    """ Crea un nuevo usuario. """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute('SELECT COUNT(*) FROM users WHERE rut = ?', (rut,))
        if cursor.fetchone()[0] > 0:
            raise ValueError("El usuario ya existe")

        # Validar la contraseña
        if len(password) < 6 or not any(char.isupper() for char in password):
            raise ValueError("La contraseña debe tener al menos 6 caracteres y una mayúscula")

        # Insertar el usuario
        cursor.execute('INSERT INTO users (rut, password, role) VALUES (?, ?, ?)',
                       (rut, hash_password(password), role))

        conn.commit()

def reset_password(rut):
    """ Restablece la contraseña de un usuario generando una nueva aleatoria. """
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE rut = ?', (rut,)).fetchone()
    
    if user:
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_password = hash_password(new_password)
        cursor.execute('UPDATE users SET password = ? WHERE rut = ?', (hashed_password, rut))
        conn.commit()
        conn.close()
        return new_password
    else:
        conn.close()
        return None

def add_company(name, address, logo_path, email, legal_name, rut, phone, city):
    """ Agrega una nueva empresa a la base de datos. """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO companies (name, address, logo_path, email, legal_name, rut, phone, city) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (name, address, logo_path, email, legal_name, rut, phone, city)
    )
    conn.commit()
    conn.close()

def assign_user_to_company(user_rut, company_rut):
    """ Asigna un usuario a una empresa evitando duplicados. """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener el ID del usuario
    cursor.execute('SELECT id FROM users WHERE rut = ?', (user_rut,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise ValueError("Usuario no encontrado.")

    # Obtener el ID de la empresa
    cursor.execute('SELECT id FROM companies WHERE rut = ?', (company_rut,))
    company = cursor.fetchone()
    if not company:
        conn.close()
        raise ValueError("Empresa no encontrada.")

    user_id = user["id"]
    company_id = company["id"]

    # Verificar si la relación ya existe
    cursor.execute('SELECT * FROM user_companies WHERE user_id = ? AND company_id = ?', (user_id, company_id))
    existing_entry = cursor.fetchone()

    if existing_entry:
        conn.close()
        raise ValueError("El usuario ya está asignado a esta empresa.")

    # Insertar en la tabla de relación user_companies
    cursor.execute('INSERT INTO user_companies (user_id, company_id) VALUES (?, ?)', (user_id, company_id))

    conn.commit()
    conn.close()

def get_user(rut):
    """ Obtiene los datos de un usuario por su RUT. """
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE rut = ?', (rut,)).fetchone()
    conn.close()
    return user

def update_user_password(rut, new_password):
    """ Permite a un usuario cambiar su propia contraseña. """
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(new_password)
    cursor.execute('UPDATE users SET password = ? WHERE rut = ?', (hashed_password, rut))
    conn.commit()
    conn.close()

def delete_user(rut):
    """ Elimina a un usuario de la base de datos. """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE rut = ?', (rut,))
    conn.commit()
    conn.close()

def recover_password_button(rut):
    """ Genera y devuelve una nueva contraseña para el usuario. """
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE rut = ?', (rut,)).fetchone()
    conn.close()
    
    if user:
        new_password = reset_password(rut)
        return f"Su nueva contraseña es: {new_password}"
    else:
        return "Usuario no encontrado"

def update_user(rut, new_password, new_role):
    """ Actualiza la información de un usuario. """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Validar la contraseña
        if new_password and (len(new_password) < 6 or not any(char.isupper() for char in new_password)):
            raise ValueError("La contraseña debe tener al menos 6 caracteres y una mayúscula")
        
        # Actualizar el rol del usuario
        cursor.execute('UPDATE users SET role = ? WHERE rut = ?', (new_role, rut))
        
        # Actualizar la contraseña si se proporciona una nueva
        if new_password:
            cursor.execute('UPDATE users SET password = ? WHERE rut = ?', (hash_password(new_password), rut))
        
        conn.commit()

def update_company(rut, new_name, new_address, new_logo_path, new_email, new_phone, new_city, new_giro, new_representative_name, new_representative_id, new_representative_email, new_representative_phone, new_bank_name, new_account_type, new_account_number):
    """ Actualiza la información de una empresa. """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Actualizar la información de la empresa
        cursor.execute('''
            UPDATE companies 
            SET name = ?, address = ?, logo_path = ?, email = ?, phone = ?, city = ?, giro = ?, representative_name = ?, representative_id = ?, representative_email = ?, representative_phone = ?, bank_name = ?, account_type = ?, account_number = ?
            WHERE rut = ?
        ''', (new_name, new_address, new_logo_path, new_email, new_phone, new_city, new_giro, new_representative_name, new_representative_id, new_representative_email, new_representative_phone, new_bank_name, new_account_type, new_account_number, rut))
        
        conn.commit()
