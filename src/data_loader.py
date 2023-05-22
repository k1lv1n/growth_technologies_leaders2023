import os
import pathlib

from loguru import logger

from data.sat_block_to_df import sat_block_to_df


class DataLoader:
    def __init__(self):
        pass

    def get_data_for_sat_russia(self, sat_name, datetime_in_ms=False):
        """
        This function retrieves data for a specific satellite in Russia from a text file and returns it as a
        pandas dataframe.
        
        :param sat_name: The name of the satellite for which data is being requested
        :return: a pandas DataFrame containing data for a specific satellite in the Russia2Constellation
        project.
        """
        sat_group_id = sat_name[-4:-2]
        file_name = f'AreaTarget-Russia-To-Satellite-KinoSat_{sat_group_id}_plane.txt'

        try:
            path = f'{pathlib.Path(__file__).parent.parent}\\data\\Russia2Constellation\\{file_name}'
            with open(path) as f:
                data = f.read()
        except FileNotFoundError:
            logger.error(f'No inormation about {sat_group_id} file')
        pure_data_starter = data.find(f'Russia-To-{sat_name}\n')
        res = sat_block_to_df(data[pure_data_starter:], datetime_in_ms)
        return res

    def get_data_for_sat_station(self, sat_name, station_name, datetime_in_ms=False):
        file_name = f'Facility-{station_name}.txt'

        try:
            path = f'{pathlib.Path(__file__).parent.parent}\\data\\Facility2Constellation\\{file_name}'
            with open(path) as f:
                data = f.read()
        except FileNotFoundError:
            logger.error(f'No inormation about {station_name}')
        pure_data_starter = data.find(f'{station_name}-To-{sat_name}\n')
        res = sat_block_to_df(data[pure_data_starter:], datetime_in_ms)

        return res


if __name__ == '__main__':
    dl = DataLoader()
    qwer = dl.get_data_for_sat_station('KinoSat_110309', 'RioGallegos')
    print(qwer[0], qwer[1])
