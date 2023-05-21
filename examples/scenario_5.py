'''
Проверка мутека, фотки и отправка
'''

import os
import sys

sys.path.insert(1, os.path.dirname('src'))

from src.data_loader import DataLoader
from src.input_manager import InputManager



if __name__ == '__main__':
    loader = DataLoader()
    manager = InputManager()
    for group in range(3, 21):
        for i in range(1, 11):
            g = f'0{group}' if group < 10 else f'{group}'
            sp = f'0{i}' if i < 10 else f'{i}'
            data_k1_downlink = loader.get_data_for_sat_station(f'KinoSat_11{g}{sp}', 'Moscow')
            data_k1_imaging = loader.get_data_for_sat_russia(f'KinoSat_11{g}{sp}')

            timeline = manager.timeline_partition_overlapping(
                list_dfs=[
                    data_k1_downlink[2], 
                    data_k1_imaging[2], 
                ], 
                list_satellite_names=[
                    data_k1_downlink[1] + '_downlink', 
                    data_k1_imaging[1] + '_imaging',
                ]
            )

            mutex = manager.generate_mutex(timeline)

            if len(mutex) != 0:
                print(f'group: {g}\nsp: {sp}\nmutex len: {len(mutex)}')
                print()