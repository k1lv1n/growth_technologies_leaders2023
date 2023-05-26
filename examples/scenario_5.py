'''
Все спутники
'''

import os
import sys

sys.path.insert(1, os.path.dirname('src'))

from data.satallites_groups import sat_all_groups, sat_group_10, sat_group_9, sat_half_groups
from data.station_groups import russian_stations, all_stations

sys.path.insert(1, os.path.dirname('src'))

from src.schedule_calculator import ScheduleCalculator
from src.input_manager import InputManager

import time
import numpy as np
import pandas as pd

if __name__ == '__main__':
    manager = InputManager()
    calculator = ScheduleCalculator()

    # FIXME: Вылетает на не русских станциях
    d = manager.basic_data_pipeline(sat_all_groups, russian_stations, 50)
    
    s_mutex = manager.get_mutex(d)
    s_img = manager.get_imaging_indexes(d)
    s_dl = manager.get_downlink_indexes(d)
    op_sat_id = manager.get_belongings(d)
    op_sat_id_dict = manager.get_belongings_dict(d)
    opportunity_memory_sizes = manager.get_opportunity_memory_sizes(d)
    cap_sat_list = manager.get_capacities(d)
    priorities = manager.get_priorites(d)

    pd.Series(s_mutex).to_json('s_mutex.json')
    pd.Series(s_img).to_json('s_img.json')
    pd.Series(s_dl).to_json('s_dl.json')
    pd.Series(op_sat_id).to_json('op_sat_id.json')
    pd.Series(op_sat_id_dict).to_json('op_sat_id_dict.json')
    pd.Series(opportunity_memory_sizes).to_json('opportunity_memory_sizes.json')
    pd.Series(cap_sat_list).to_json('cap_sat_list.json')
    pd.Series(priorities).to_json('priorities.json')

    out = calculator.calculate(
        config_data=None,
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
    try:
        d.drop(columns='index', inplace=True)
    except KeyError:
        pass
    final = out.merge(d, how='left', left_index=True, right_index=True)
    final.to_csv('fin.csv')
    print('ended')