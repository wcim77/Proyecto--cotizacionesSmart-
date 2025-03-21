import sys
from PySide6.QtWidgets import QApplication
from ui.login import LoginWindow
from db.database import initialize_db

def main():
    initialize_db()
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()