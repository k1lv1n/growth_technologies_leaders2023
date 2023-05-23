'''
Проверка мутека, 3 разные групировки
'''

import os
import sys

sys.path.insert(1, os.path.dirname('src'))

from src.schedule_calculator import ScheduleCalculator
from src.input_manager import InputManager

import time
import numpy as np

if __name__ == '__main__':
    manager = InputManager()
    calculator = ScheduleCalculator()
    d = manager.basic_data_pipeline(['KinoSat_110301'],
                                    ['Moscow'],
                                    50)

    calculator.calculate(
        config_data=None,
        num_opportunities=len(d),
        cap=10 ** 9,
        s_mutex=manager.get_mutex(d),
        s_img=manager.get_imaging_indexes(d),
        s_dl=manager.get_downlink_indexes(d),
        op_sat_id=manager.get_belongings(d),
        op_sat_id_dict=manager.get_belongings_dict(d),
        opportunity_memory_sizes=manager.get_opportunity_memory_sizes(d),
        alpha=1e-5,
        d=np.ones(len(d)),
        priorities=manager.get_priorites(d)
    )
