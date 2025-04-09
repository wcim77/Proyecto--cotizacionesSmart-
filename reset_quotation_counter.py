import sqlite3

def reset_quotation_number(db_path="db/invoice_manager.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE quotation_numbers SET current_number = 0")
    conn.commit()
    conn.close()
    print("El contador de cotizaciones ha sido reiniciado a 0.")

if __name__ == "__main__":
    reset_quotation_number()
