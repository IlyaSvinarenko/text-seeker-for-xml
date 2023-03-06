import sys
import sys, csv, sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_file = 'data.db'
        self.table_name = 'posts'
        add_csv_button = QtWidgets.QPushButton("Добавить CSV файл")
        add_csv_button.clicked.connect(self.add_csv_file)

        clear_db_button = QtWidgets.QPushButton("Очистить базу данных")
        clear_db_button.clicked.connect(self.clear_database)
        self.text_output = QtWidgets.QTextEdit()
        self.text_output.setText('* Нажмите "Добавить CSV-файл" и выберите интересующий вас файл.\n\n'
                                 '* После добавления файла, внизу можете ввести текст для поиска.\n\n'
                                 '* После введения текста, нажмите кнопку "Найти".\n\n'
                                 '* Для удаления записи из базы данных: введите id записи в поле для id, и нажмите '
                                 'удалить\n\n'
                                 'Важно!!  В обрабатываемом CSV-файле обязательно должны присутствовать поля: "text" '
                                 'и "created_date" в '
                                 'верхней строке.\n Все потому что поля базы данных формируются из верхней строки csv файла, и в дальнейшем поиск совпадений ведется по тексту в поле "text", а удаление запизей производится по "id"!')
        self.text_input = QtWidgets.QLineEdit()
        self.text_input.setPlaceholderText("Введите текст здесь")
        find_button = QtWidgets.QPushButton("Найти")
        find_button.clicked.connect(self.find_text)

        self.id_input = QtWidgets.QLineEdit()
        self.id_input.setPlaceholderText("Введите id записи, для удаления")
        del_botton = QtWidgets.QPushButton("Удалить")
        del_botton.clicked.connect(self.del_record)

        vbox = QtWidgets.QVBoxLayout()
        hbox_top = QtWidgets.QHBoxLayout()
        hbox_top.addWidget(add_csv_button)
        hbox_top.addWidget(clear_db_button)
        vbox.addLayout(hbox_top)
        vbox.addWidget(self.text_output)
        hbox_bottom = QtWidgets.QHBoxLayout()
        hbox_bottom.addWidget(self.text_input)
        hbox_bottom.addWidget(find_button)
        hbox_lower_bottom = QtWidgets.QHBoxLayout()
        hbox_lower_bottom.addWidget(self.id_input)
        hbox_lower_bottom.addWidget(del_botton)
        vbox.addLayout(hbox_bottom)
        vbox.addLayout(hbox_lower_bottom)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

    def clear_database(self):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        conn.commit()
        conn.close()
        self.text_output.setText('База данных очищена')

    def del_record(self):
        id = self.id_input.text()
        try:
            conn = sqlite3.connect(self.db_file)
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {self.table_name} WHERE id = {id}")
            print(f"{id}  deleted")
            conn.commit()
            conn.close()
            msgBox = QMessageBox()
            msgBox.setText(f'Зпаись с id({id}) была удалена из базы данных')
            msgBox.setWindowTitle('Оповещение')
            msgBox.exec_()
        except:
            msgBox = QMessageBox()
            msgBox.setText(f'Что-то пошло не так(')
            msgBox.setWindowTitle('Оповещение')
            msgBox.exec_()

    def find_text(self):
        text = self.text_input.text()
        try:
            count = 0
            conn = sqlite3.connect(self.db_file)
            cur = conn.cursor()
            res = cur.execute(f"SELECT * FROM {self.table_name} "
                              f"WHERE text LIKE '%{text}%'"
                              f"ORDER BY created_date DESC").fetchmany(20)
            text = ''
            for row in res:
                count += 1
                print(count)
                text += ('id: ' + str(row[0]) + ',\n' + 'text: ' + str(row[1]) + ',\n' + 'date_time: ' + str(row[2]) +
                         ',\n' + 'rubrics: ' + str(row[3]) + ',\n')
            self.text_output.setText(text)
            conn.close()
        except:
            self.text_output.setText("база данных пуста, сначала добавте файл")

    def add_csv_file(self):
        fname, filetype = QFileDialog.getOpenFileName(self, "Open file", ".", "(*.csv)")
        if fname:
            with open(fname, 'r', encoding='utf-8') as csv_file:
                self.csv_to_sqlite(csv_file, self.db_file, self.table_name)

    def csv_to_sqlite(self, csv_file, db_file, table_name):
        try:
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            csv_reader = csv.reader(csv_file)
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, "
                        f"{', '.join(next(csv_reader))})")
            for row in csv_reader:
                cur.execute(f"INSERT INTO {table_name} VALUES (NULL, {', '.join('?' for _ in row)})", row)
            conn.commit()
            conn.close()
            self.text_output.setText("Файл успешно добавлен в базу данных, можете приступать к поиску")
        except:
            self.text_output.setText("При переносе csv файла в базу данных произошла ошибка")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowTitle('Поиск текста в БД')
    main_window.setGeometry(200, 200, 700, 700)
    main_window.show()
    sys.exit(app.exec())
