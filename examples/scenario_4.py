'''
Проверка мутека, 3 разные групировки
'''

import os
import sys

sys.path.insert(1, os.path.dirname('src'))

from src.data_loader import DataLoader
from src.input_manager import InputManager



if __name__ == '__main__':
    loader = DataLoader()
    manager = InputManager()
    data_k1 = loader.get_data_for_sat_station('KinoSat_110101', 'RioGallegos')
    data_k2 = loader.get_data_for_sat_station('KinoSat_110102', 'RioGallegos')
    data_k3 = loader.get_data_for_sat_station('KinoSat_110201', 'RioGallegos')
    data_k4 = loader.get_data_for_sat_station('KinoSat_110301', 'RioGallegos')

    timeline = manager.timeline_partition_overlapping(
        list_dfs=[
            data_k1[2], 
            data_k2[2], 
            data_k3[2],
            data_k4[2]
        ], 
        list_satellite_names=[
            data_k1[1], 
            data_k2[1], 
            data_k3[1],
            data_k4[1]
        ]
    )

    mutex = manager.generate_mutex(timeline)


    print()
