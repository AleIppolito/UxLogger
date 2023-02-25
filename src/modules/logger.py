from serial import Serial
from re import compile, VERBOSE
from logging import getLogger, Formatter, FileHandler, NOTSET


class SerialLogger:
    def __init__(self):
        self.__serial_object = None
        self.__stream_ongoing: bool = True
        self.__logger = getLogger('UxLogger')
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

        self.__sys_string_format: str = '%(asctime)s.%(msecs)03d -- [SYS] -- %(message)s'
        self.__ivi_string_format: str = '%(asctime)s.%(msecs)03d -- [IVI] -- %(message)s'
        self.__std_string_format: str = '%(asctime)s.%(msecs)03d -- %(message)s'
        self.__date_format: str = '%yyyy-%mm-%dd %HH:%MM:%SS'

        self.__sys_formatter: Formatter = Formatter(self.__sys_string_format, datefmt=self.__date_format)
        self.__ivi_formatter: Formatter = Formatter(self.__ivi_string_format, datefmt=self.__date_format)
        self.__std_formatter: Formatter = Formatter(self.__std_string_format, datefmt=self.__date_format)

        self.__logging_path: str = ''
        self.__handler = None

    def init_logger(self, *args):
        self.__port, self.__baudrate, self.__logging_path = args
        self.__serial_object = Serial(self.__port, self.__baudrate)
        self.__handler = FileHandler(self.__logging_path, encoding='windows-1252', errors='xmlcharrefreplace')
        self.__logger.addHandler(self.__handler)
        self.__logger.setLevel(NOTSET)

    def start_stream(self):
        while self.__stream_ongoing:
            escaped_dict = self.__escape_ANSI(self.__serial_object.readline()).groupdict()
            if escaped_dict['ansi'] == '\x1b[0m':  # white
                self.__handler.setFormatter(self.__sys_formatter)
            elif escaped_dict['ansi'] == '\x1b[32m':  # green
                self.__handler.setFormatter(self.__ivi_formatter)
            else:  # other colours
                self.__handler.setFormatter(self.__std_formatter)
            self.__logger.info(escaped_dict['message'])

        self.__handler.close()

    def stop_stream(self):
        self.__stream_ongoing = False
