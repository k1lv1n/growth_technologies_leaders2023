'''
Проверка мутека, 3 разные групировки
'''

import os
import sys

sys.path.insert(1, os.path.dirname('data'))

from data.satallites_groups import sat_group_8, sat_group_9, sat_group_10, sat_group_all
from data.station_groups import russian_stations

sys.path.insert(1, os.path.dirname('src'))

from src.schedule_calculator import ScheduleCalculator
from src.input_manager import InputManager

import time
import numpy as np

if __name__ == '__main__':
    manager = InputManager()
    calculator = ScheduleCalculator()
    dl_only = False

    sat_group = ['KinoSat_110508', ]

    if dl_only:
        d = manager.basic_data_pipeline_dl(sat_group, russian_stations, 500)
    else:
        d = manager.basic_data_pipeline_all(sat_group, russian_stations, 500)

    # d_part = manager.partition_data_by_modeling_interval(24, d)

    s_mutex = manager.get_mutex(d, sat_group)

    if dl_only:
        s_img = None
    else:
        s_img = manager.get_imaging_indexes(d)

    s_dl = manager.get_downlink_indexes(d)
    op_sat_id = manager.get_belongings(d)
    op_sat_id_dict = manager.get_belongings_dict(d)
    opportunity_memory_sizes = manager.get_opportunity_memory_sizes(d)
    cap_sat_list = manager.get_capacities(d)
    priorities = manager.get_priorites(d)

    out = calculator.calculate(
        config_data=None,
        dl_only=dl_only,
        num_opportunities=len(d),
        cap=cap_sat_list,
        s_mutex=s_mutex,
        s_img=s_img,
        s_dl=s_dl,
        op_sat_id=op_sat_id,
        op_sat_id_dict=op_sat_id_dict,
        opportunity_memory_sizes=opportunity_memory_sizes,
        alpha=1e-5,
        d=np.ones(len(d)),
        priorities=priorities,
    )

    # d.drop(columns='index', inplace=True)

    final = out.merge(d, how='left', left_index=True, right_index=True)
    final.to_csv('123.csv')
    print('ended')
