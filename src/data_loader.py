from typing import List

from data.sat_block_to_df import sat_block_to_df
import os

class DataLoader:
    def __init__(self):
        pass

    def load_data(self, sats: List[str], stations: List[str]):  # todo
        res = []

    def get_data_for_sat_russia(self, sat_name):
        """
        This function retrieves data for a specific satellite in Russia from a text file and returns it as a
        pandas dataframe.
        
        :param sat_name: The name of the satellite for which data is being requested
        :return: a pandas DataFrame containing data for a specific satellite in the Russia2Constellation
        project.
        """
        sat_group_id = sat_name[-4:-2]
        file_name = f'AreaTarget-Russia-To-Satellite-KinoSat_{sat_group_id}_plane.txt'
        path = os.path.join(os.path.dirname(os.getcwd()), 'data', 'Russia2Constellation', file_name)
        with open(path) as f:
            data = f.read()
        pure_data_starter = data.find(f'Russia-To-{sat_name}\n')
        res = sat_block_to_df(data[pure_data_starter:])
        return res

    def get_data_for_sat_station(self, sat_name, station_name):
        file_name = f'Facility-{station_name}.txt'
        path = os.path.join(os.getcwd(), 'data', 'Facility2Constellation', file_name)
        with open(path) as f:
            data = f.read()
        pure_data_starter = data.find(f'{station_name}-To-{sat_name}\n')
        res = sat_block_to_df(data[pure_data_starter:])
        return res


if __name__ == '__main__':
    dl = DataLoader()
    qwer = dl.get_data_for_sat_station('KinoSat_110309', 'RioGallegos')
    print(qwer[0], qwer[1])
