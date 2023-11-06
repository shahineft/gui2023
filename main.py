import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMenu, QAction, QTableWidget, QGridLayout, QTableWidgetItem, QWidget, QMessageBox, QHeaderView, QComboBox
import sqlite3
from PyQt5.QtCore import Qt, QDate
import os

def get_color(blood_sugar_value, unit):
    if unit == "mg/dL":
        if blood_sugar_value < 70:
            return "red"
        elif blood_sugar_value < 140:
            return "green"
        else:
            return "red"
    elif unit == "mmol/L":
        if blood_sugar_value < 3.9:
            return "red"
        elif blood_sugar_value < 7.8:
            return "green"
        else:
            return "red"
    else:
        raise ValueError("Invalid unit: {}".format(unit))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blutzuckerwerte")
        self.resize(800, 500)

        self.name_edit = QLineEdit()
        self.first_name_edit = QLineEdit()

        self.birthday_day_combo = QComboBox()
        self.birthday_month_combo = QComboBox()
        self.birthday_year_combo = QComboBox()

        for day in range(1, 32):
            self.birthday_day_combo.addItem(str(day))
        for month in range(1, 13):
            self.birthday_month_combo.addItem(str(month))
        for year in range(QDate.currentDate().year() - 120, QDate.currentDate().year() + 1):
            self.birthday_year_combo.addItem(str(year))

        self.date_time_display = QLineEdit()
        self.date_time_display.setReadOnly(True)
        self.blood_sugar_value_edit = QLineEdit()
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["mmol/L", "mg/dL"])
        self.meal_size_edit = QLineEdit()
        self.medication_edit = QLineEdit()
        self.notes_edit = QLineEdit()

        self.save_button = QPushButton("Speichern")
        self.evaluate_button = QPushButton("Auswerten")

        self.file_menu = QMenu("Datei", self)
        self.exit_action = QAction("Beenden", self)
        self.file_menu.addAction(self.exit_action)
        self.menuBar().addMenu(self.file_menu)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Datum und Uhrzeit", "Blutzuckerwert", "Farbe"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("Name:"), 0, 0)
        self.layout.addWidget(self.name_edit, 0, 1)
        self.layout.addWidget(QLabel("Vorname:"), 1, 0)
        self.layout.addWidget(self.first_name_edit, 1, 1)
        self.layout.addWidget(QLabel("Geburtstag:"), 2, 0)
        self.layout.addWidget(self.birthday_day_combo, 2, 1)
        self.layout.addWidget(self.birthday_month_combo, 2, 2)
        self.layout.addWidget(self.birthday_year_combo, 2, 3)
        self.layout.addWidget(QLabel("Datum und Uhrzeit:"), 3, 0)
        self.layout.addWidget(self.date_time_display, 3, 1)
        self.layout.addWidget(QLabel("Blutzuckerwert:"), 4, 0)
        self.layout.addWidget(self.blood_sugar_value_edit, 4, 1)
        self.layout.addWidget(QLabel("Einheit:"), 5, 0)
        self.layout.addWidget(self.unit_combo, 5, 1)
        self.layout.addWidget(QLabel("Mahlzeitengröße:"), 6, 0)
        self.layout.addWidget(self.meal_size_edit, 6, 1)
        self.layout.addWidget(QLabel("Medikation:"), 7, 0)
        self.layout.addWidget(self.medication_edit, 7, 1)
        self.layout.addWidget(QLabel("Notizen:"), 8, 0)
        self.layout.addWidget(self.notes_edit, 8, 1)
        self.layout.addWidget(self.save_button, 9, 0)
        self.layout.addWidget(self.evaluate_button, 9, 1)
        self.layout.addWidget(self.table_widget, 10, 0, 1, 2)

        self.save_button.clicked.connect(self.save_data)
        self.evaluate_button.clicked.connect(self.evaluate_data)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        self.exit_action.triggered.connect(self.close)

        self.create_database()

    def create_database(self):
        if not os.path.exists("blood_sugar_values.db"):
            connection = sqlite3.connect("blood_sugar_values.db")
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blood_sugar_values (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    first_name TEXT,
                    birthday_day INTEGER,
                    birthday_month INTEGER,
                    birthday_year INTEGER,
                    date_time DATETIME,
                    blood_sugar_value REAL,
                    unit TEXT,
                    meal_size REAL,
                    medication TEXT,
                    notes TEXT
                )
            """)
            connection.commit()
            connection.close()

    def save_data(self):
        name = self.name_edit.text()
        first_name = self.first_name_edit.text()
        birthday_day = self.birthday_day_combo.currentText()
        birthday_month = self.birthday_month_combo.currentText()
        birthday_year = self.birthday_year_combo.currentText()
        date_time = self.date_time_display.text()
        blood_sugar_value = float(self.blood_sugar_value_edit.text())
        unit = self.unit_combo.currentText()
        meal_size = float(self.meal_size_edit.text())
        medication = self.medication_edit.text()
        notes = self.notes_edit.text()

        connection = sqlite3.connect("blood_sugar_values.db")
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO blood_sugar_values (
                name,
                first_name,
                birthday_day,
                birthday_month,
                birthday_year,
                date_time,
                blood_sugar_value,
                unit,
                meal_size,
                medication,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, first_name, birthday_day, birthday_month, birthday_year, date_time, blood_sugar_value, unit, meal_size, medication, notes))
        connection.commit()
        connection.close()

        self.show_message("Daten gespeichert")

    def visualize_data(self):
        connection = sqlite3.connect("blood_sugar_values.db")
        cursor = connection.cursor()
        cursor.execute("SELECT date_time, blood_sugar_value, unit FROM blood_sugar_values")
        data = cursor.fetchall()
        connection.close()

        self.table_widget.setRowCount(len(data))
        for i, (date_time, blood_sugar_value, unit) in enumerate(data):
            color = get_color(blood_sugar_value, unit)
            self.table_widget.setItem(i, 0, QTableWidgetItem(date_time))
            self.table_widget.setItem(i, 1, QTableWidgetItem(str(blood_sugar_value)))
            self.table_widget.setItem(i, 2, QTableWidgetItem(color))
            self.table_widget.item(i, 0).setTextAlignment(Qt.AlignCenter)
        self.table_widget.viewport().update()
    def evaluate_data(self):
        connection = sqlite3.connect("blood_sugar_values.db")
        cursor = connection.cursor()
        cursor.execute("SELECT AVG(blood_sugar_value) AS average, COUNT(*) AS count FROM blood_sugar_values")
        data = cursor.fetchone()
        connection.close()

        average = data[0]
        count = data[1]

        self.show_message(f"Durchschnitt: {average:.2f}\nAnzahl der Datensätze: {count}")

    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Nachricht")
        msg_box.setText(message)
        msg_box.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
