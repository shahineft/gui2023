import sys
import sqlite3
import os
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMenu, QAction, QTableWidget, \
    QGridLayout, QTableWidgetItem, QWidget, QMessageBox, QHeaderView, QComboBox
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication


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
    # Komponenten des Fensters werde hier deklariert
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blutzuckerwerte")
        self.resize(1000, 800)

        self.name_edit = QLineEdit()
        self.first_name_edit = QLineEdit()

        self.birthday_day_combo = QComboBox()
        self.birthday_month_combo = QComboBox()
        self.birthday_year_combo = QComboBox()

        # für das Geburtsdatum Eingabe wird hier für Tag, Monat und Jahr die Werte vorgeneriert
        for day in range(0, 32):
            if (day==0):
                self.birthday_day_combo.addItem('')
            else:
                self.birthday_day_combo.addItem(str(day))
        for month in range(0, 13):
            if (month == 0):
                self.birthday_month_combo.addItem('')
            else:
                self.birthday_month_combo.addItem(str(month))
        for year in range(QDate.currentDate().year() - 51, QDate.currentDate().year() + 1):
            if (year == QDate.currentDate().year() - 51):
                self.birthday_year_combo.addItem('')
            else:
                self.birthday_year_combo.addItem(str(year))

        # editierbare Flächen werdden definiert
        self.blood_sugar_value_edit = QLineEdit()
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["", "mmol/L", "mg/dL"])
        self.meal_size_edit = QLineEdit()
        self.medication_edit = QLineEdit()
        self.notes_edit = QLineEdit()

        # SAVE und AUSWERTEN Knöpfe werden hier deklariert
        self.save_button = QPushButton("Speichern")
        self.evaluate_button = QPushButton("Auswerten")

        # Datei und Beenden Knöpfe werden hier deklariert
        self.file_menu = QMenu("Datei", self)
        self.exit_action = QAction("Beenden", self)
        self.file_menu.addAction(self.exit_action)
        self.menuBar().addMenu(self.file_menu)

        # die Tabelle zur Anzeige wird hier deklariert
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Vorname", "Name", "Datum und Uhrzeit", "Blutzuckerwert", "Farbe"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Suche-Bar wird hier deklariert
        #self.search_edit = QLineEdit()
        self.search_button = QPushButton("Suchen")
        self.search_button.clicked.connect(self.search_patients)

        # die ganzen deklarierten Flächen werden hier initialisiert
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("Name:"), 0, 0)
        self.layout.addWidget(self.name_edit, 0, 1)
        self.layout.addWidget(QLabel("Vorname:"), 1, 0)
        self.layout.addWidget(self.first_name_edit, 1, 1)
        self.layout.addWidget(QLabel("Geburtstag:"), 2, 0)
        self.layout.addWidget(self.birthday_day_combo, 2, 1)
        self.layout.addWidget(self.birthday_month_combo, 2, 2)
        self.layout.addWidget(self.birthday_year_combo, 2, 3)
        self.layout.addWidget(QLabel("Blutzuckerwert:"), 3, 0)
        self.layout.addWidget(self.blood_sugar_value_edit, 3, 1)
        self.layout.addWidget(QLabel("Einheit:"), 4, 0)
        self.layout.addWidget(self.unit_combo, 4, 1)
        self.layout.addWidget(QLabel("Mahlzeitengröße:"), 5, 0)
        self.layout.addWidget(self.meal_size_edit, 5, 1)
        self.layout.addWidget(QLabel("Medikation:"), 6, 0)
        self.layout.addWidget(self.medication_edit, 6, 1)
        self.layout.addWidget(QLabel("Notizen:"), 7, 0)
        self.layout.addWidget(self.notes_edit, 7, 1)
        self.layout.addWidget(self.save_button, 8, 0)
        self.layout.addWidget(self.evaluate_button, 8, 1)
        self.layout.addWidget(self.search_button, 8, 2)
        self.layout.addWidget(self.table_widget, 9, 0, 1, 2)
        #self.layout.addWidget(QLabel("Patient suchen:"), 10, 0)
        #self.layout.addWidget(self.search_edit, 10, 1)


        # load_patients nimmt alle Daten aus DB und zeigt diese in der Anzeige "table_widget"
        self.visualize_data()
        # der save_button und evaluate_button werden mit den entsprechenden Funktionen verbunden: save_data und evaluate_data
        self.save_button.clicked.connect(self.save_data)
        self.evaluate_button.clicked.connect(self.evaluate_data)

        # Das Fenster wird hier angezeigt als GUI
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        # der Button exit_action wird mit der funktion close gekoppelt
        self.exit_action.triggered.connect(self.close)

        # diese Funktion kreiiert eine DB
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
        birthday_day = int(self.birthday_day_combo.currentText())
        birthday_month = int(self.birthday_month_combo.currentText())
        birthday_year = int(self.birthday_year_combo.currentText())

        # Get the current datetime and format it as a string
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
        """, (
        name, first_name, birthday_day, birthday_month, birthday_year, date_time, blood_sugar_value, unit, meal_size,
        medication, notes))
        connection.commit()
        connection.close()

        self.show_message("Daten gespeichert")

    def visualize_data(self):
        connection = sqlite3.connect("blood_sugar_values.db")
        cursor = connection.cursor()
        cursor.execute("SELECT first_name, name, date_time, blood_sugar_value, unit FROM blood_sugar_values")
        data = cursor.fetchall()
        connection.close()

        self.table_widget.setRowCount(len(data))
        for i, (first_name, name, date_time, blood_sugar_value, unit) in enumerate(data):
            color = get_color(blood_sugar_value, unit)
            self.table_widget.setItem(i, 0, QTableWidgetItem(first_name))
            self.table_widget.setItem(i, 1, QTableWidgetItem(name))
            self.table_widget.setItem(i, 2, QTableWidgetItem(str(date_time)))
            self.table_widget.setItem(i, 3, QTableWidgetItem(str(blood_sugar_value)))
            self.table_widget.setItem(i, 4, QTableWidgetItem(color))
            self.table_widget.item(i, 0).setTextAlignment(Qt.AlignCenter)

        self.table_widget.viewport().update()

    def evaluate_data(self):
        name = self.name_edit.text().strip().lower()
        first_name = self.first_name_edit.text().strip().lower()
        birthday_day = self.birthday_day_combo.currentText()
        birthday_month = self.birthday_month_combo.currentText()
        birthday_year = self.birthday_year_combo.currentText()
        connection = sqlite3.connect("blood_sugar_values.db")
        cursor = connection.cursor()

        # Verwenden von Parametern anstelle von String-Konkatenation für die SQL-Abfrage
        cursor.execute("""
            SELECT AVG(blood_sugar_value) AS average, COUNT(*) AS count 
            FROM blood_sugar_values
            WHERE LOWER(name) LIKE ? AND LOWER(first_name) LIKE ? AND birthday_day = ? AND birthday_month = ? AND birthday_year = ?
        """, ('%' + name + '%', '%' + first_name + '%', birthday_day, birthday_month, birthday_year))

        data = cursor.fetchone()
        connection.close()

        # Überprüfen, ob Daten vorhanden sind
        if data and data[0] is not None:
            average = data[0]
            count = data[1]
            self.show_message(f"Durchschnitt: {average:.2f}\nAnzahl der Datensätze: {count}")
        else:
            self.show_message("Keine Daten gefunden für den angegebenen Namen.")

    def search_patients(self):
        name = self.name_edit.text().strip().lower()
        first_name = self.first_name_edit.text().strip().lower()
        birthday_day = self.birthday_day_combo.currentText()
        birthday_month = self.birthday_month_combo.currentText()
        birthday_year = self.birthday_year_combo.currentText()

        # Basis-Query
        query = """
            SELECT first_name, name, date_time, blood_sugar_value, unit
            FROM blood_sugar_values
            WHERE 1=1
        """
        params = []

        # Bedingungen für Name und Vorname
        if name:
            query += " AND LOWER(name) = ?"
            params.append(name)
        if first_name:
            query += " AND LOWER(first_name) = ?"
            params.append(first_name)

        # Bedingung für das Geburtsdatum, nur wenn alle Felder ausgefüllt sind
        if birthday_day and birthday_month and birthday_year:
            query += " AND birthday_day = ? AND birthday_month = ? AND birthday_year = ?"
            params.extend([int(birthday_day), int(birthday_month), int(birthday_year)])

        connection = sqlite3.connect("blood_sugar_values.db")
        cursor = connection.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        print(data)
        connection.close()



        self.table_widget.setRowCount(len(data))
        for i, (first_name, name, date_time, blood_sugar_value, unit) in enumerate(data):
            color = get_color(blood_sugar_value, unit)
            self.table_widget.setItem(i, 0, QTableWidgetItem(first_name))
            self.table_widget.setItem(i, 1, QTableWidgetItem(name))
            self.table_widget.setItem(i, 2, QTableWidgetItem(str(date_time)))
            self.table_widget.setItem(i, 3, QTableWidgetItem(str(blood_sugar_value)))
            self.table_widget.setItem(i, 4, QTableWidgetItem(color))
            self.table_widget.item(i, 0).setTextAlignment(Qt.AlignCenter)

        self.table_widget.viewport().update()

    # ... [Your existing visualize_data and evaluate_data methods]
    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Nachricht")
        msg_box.setText(message)
        msg_box.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
