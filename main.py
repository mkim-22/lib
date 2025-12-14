import sys
from PyQt6.QtWidgets import QApplication
from auth.login_wind import LoginWindow

def main():
    application = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(application.exec())

if __name__ == "__main__":
    main()
