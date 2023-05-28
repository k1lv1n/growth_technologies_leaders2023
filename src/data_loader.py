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
        if int(sat_group_id) <= 5:
            file_name = f'Russia-To-Satellite-SatPlanes_1_5.txt'
        else:
            file_name = f'Russia-To-Satellite-SatPlanes_6_20.txt'
        try:
            path = os.path.join(pathlib.Path(__file__).parent.parent, 'data', 'Russia2Constellation', file_name)
            # path = f'{pathlib.Path(__file__).parent.parent}\\data\\Russia2Constellation\\{file_name}'
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
            path = os.path.join(pathlib.Path(__file__).parent.parent, 'data', 'Facility2Constellation', file_name)
            # path = f'{pathlib.Path(__file__).parent.parent}\\data\\Facility2Constellation\\{file_name}'
            with open(path) as f:
                data = f.read()
        except FileNotFoundError:
            logger.error(f'No information about {station_name}')
            print(f'{station_name}-To-{sat_name}')
        pure_data_starter = data.find(f'{station_name}-To-{sat_name}\n')
        res = sat_block_to_df(data[pure_data_starter:], datetime_in_ms)

        return res


if __name__ == '__main__':
    dl = DataLoader()
    qwer = dl.get_data_for_sat_station('KinoSat_110309', 'RioGallegos')
    print(qwer[0], qwer[1])
