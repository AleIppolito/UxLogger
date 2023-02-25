from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import sys

# On Windows it looks like cp850 is used for my console. We need it to decode the QByteArray correctly.
# Based on https://forum.qt.io/topic/85064/qbytearray-to-string/2
import ctypes



class MainWindow(QMainWindow):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        self.__CP_console = f"cp{ctypes.cdll.kernel32.GetConsoleOutputCP()}"

        # QProcess object for external app
        self.__process = QProcess(self)
        # QProcess emits `readyRead` when there is data to be read
        self.__process.readyRead.connect(self.__data_ready)
        
        # Layout are better for placing widgets
        layout = QVBoxLayout()
        self.__run_button = QPushButton('Run')
        self.__run_button.clicked.connect(self.__call_program)

        self.__output_text = QTextEdit()
        self.__output_text.setStyleSheet("""
            QTextEdit {font: Consolas, background: black},
            QScrollBar {color: white}
            """)

        layout.addWidget(self.__output_text)
        layout.addWidget(self.__run_button)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.__process.started.connect(lambda: self.__run_button.setEnabled(False))
        self.__process.finished.connect(lambda: self.__run_button.setEnabled(True))

    def __data_ready(self):
        cursor = self.__output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)

        # Here we have to decode the QByteArray
        cursor.insertText(str(self.__process.readAll().data().decode(self.__CP_console)))
        self.__output_text.ensureCursorVisible()

    def __call_program(self):
        # run the process
        # 'start' takes the exec and a list of arguments
        self.__process.start('ping', ['127.0.0.1'])
        # self.__process.start('python3', ['script.py'])


# Function Main Start


def main():
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec())
# Function Main END


if __name__ == '__main__':
    main()
