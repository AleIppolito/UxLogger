import time
import ctypes
from serial import Serial
from threading import Thread
from re import compile, VERBOSE
from logging import getLogger, Formatter, FileHandler, DEBUG


class SerialLogger:
    def __init__(self):
        self.__stream_pipe: list = []
        self.__console_pipe: list = []
        self.__serial_object = None
        self.__stream_ongoing: bool = True
        self.__console_exists: bool = False
        self.__logger = getLogger('UxLogger')
        self.__logger.setLevel(DEBUG)
        self.__port: str = ''
        self.__baudrate: int = 9600
        self.__escape_ANSI = compile(r"""
            (?P<ansi>(\x1b     # literal ESC
            \[       # literal [
            [;\d]*   # zero or more digits or semicolons
            [A-Za-z] # a letter
            )*)
            (?P<message>.*)
            """, VERBOSE).match
        self.__CP_console = f"cp{ctypes.cdll.kernel32.GetConsoleOutputCP()}"

        self.__sys_string_format: str = '%(asctime)s.%(msecs)03d -- [SYS] -- %(message)s'
        self.__ivi_string_format: str = '%(asctime)s.%(msecs)03d -- [IVI] -- %(message)s'
        self.__std_string_format: str = '%(asctime)s.%(msecs)03d -- %(message)s'
        self.__date_format: str = '%Y-%m-%d %H:%M:%S'
        # self.__encoding: str = 'windows-1252'

        self.__sys_formatter: Formatter = Formatter(self.__sys_string_format, datefmt=self.__date_format)
        self.__ivi_formatter: Formatter = Formatter(self.__ivi_string_format, datefmt=self.__date_format)
        self.__std_formatter: Formatter = Formatter(self.__std_string_format, datefmt=self.__date_format)

        self.__logging_path: str = ''
        self.__handler = None

    def init_logger(self, *args):
        self.__port, self.__baudrate, self.__logging_path = args
        self.__serial_object = Serial(self.__port, self.__baudrate)
        self.__handler = FileHandler(self.__logging_path, encoding=self.__CP_console, errors='xmlcharrefreplace')

    def start_stream(self):
        while self.__stream_ongoing:
            read_line = self.__serial_object.readline()[:-2].decode(self.__CP_console)
            escaped_dict = self.__escape_ANSI(read_line).groupdict()
            if escaped_dict['ansi'] == '\x1b[0m':  # white
                self.__handler.setFormatter(self.__sys_formatter)
            elif escaped_dict['ansi'] == '\x1b[32m':  # green
                self.__handler.setFormatter(self.__ivi_formatter)
            else:  # other colours
                self.__handler.setFormatter(self.__std_formatter)
            self.__logger.addHandler(self.__handler)
            self.__logger.info(escaped_dict['message'])  # Modified by Formatter for file
            if self.__console_exists:
                self.__console_pipe.append(read_line)  # Keeps color information for console
            else:
                print(read_line)

        self.__handler.close()

    def stop_stream(self):
        self.__stream_ongoing = False

    def get_baudrate(self):
        return self.__baudrate

    def get_port(self):
        return self.__port


if __name__ == '__main__':
    log = SerialLogger()
    log.init_logger(*('COM4', 115200, r'C:\Users\Alessandro\Downloads\dumb_logging\serial.log'))
    pushing_thread = Thread(target=log.start_stream)
    pushing_thread.start()
    time.sleep(10)
    log.stop_stream()
    print('stream finished')
