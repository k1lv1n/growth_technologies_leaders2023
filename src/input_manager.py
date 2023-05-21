"""
Файл с классом InputManager. InputManager отвечает за обработку входных файлов.
"""
import pandas as pd


class InputManager:

    def __init__(self):
        pass

    def read_data(self) -> pd.DataFrame:
        """
        Прочитать файл/архив и вернуть
        :return:
        """
        pass

    def read_config(self, config) -> dict:
        """
        Считать информацию о конфигурации расчета (что учитываем и с какими весами)
        :param config:
        :return:
        """
        pass

    def prepare_data(self):
        pass