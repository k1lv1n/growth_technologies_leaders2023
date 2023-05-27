'''
Проверка мутека, 3 разные групировки
'''
import datetime
import os
import sys

sys.path.insert(1, os.path.dirname('data'))

from data.satallites_groups import *
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
    sat_group = [
        *sat_group_all
        # * sat_group_3,
        # * sat_group_3,
    ]
    stations = russian_stations
    partition_restrict = 500
    modeling_start_datetime = datetime.datetime(2027, 6, 1, 0)
    modeling_end_datetime = datetime.datetime(2027, 6, 1, 12)
    out_name = f'{len(sat_group)}_sats_{len(stations)}_stats_{modeling_start_datetime.date()}_start_{modeling_end_datetime.date()}_end'
    print(modeling_end_datetime - modeling_start_datetime)
    # modeling_interval_in_hours = 24

    if dl_only:
        d = manager.basic_data_pipeline_dl(sat_group, stations, partition_restrict)
    else:
        d = manager.basic_data_pipeline_all(sat_group, stations, partition_restrict)

    d_part = manager.partition_data_by_modeling_interval(modeling_start_datetime, modeling_end_datetime, d)

    s_mutex = manager.get_mutex(d_part, sat_group)

    if dl_only:
        s_img = None
    else:
        s_img = manager.get_imaging_indexes(d_part)

    s_dl = manager.get_downlink_indexes(d_part)
    op_sat_id = manager.get_belongings(d_part)
    op_sat_id_dict = manager.get_belongings_dict(d_part)
    opportunity_memory_sizes = manager.get_opportunity_memory_sizes(d_part)
    cap_sat_list = manager.get_capacities(d_part)
    priorities = manager.get_priorites(d_part)

    out = calculator.calculate(
        config_data=None,
        dl_only=dl_only,
        num_opportunities=len(d_part),
        cap=cap_sat_list,
        s_mutex=s_mutex,
        s_img=s_img,
        s_dl=s_dl,
        op_sat_id=op_sat_id,
        op_sat_id_dict=op_sat_id_dict,
        opportunity_memory_sizes=opportunity_memory_sizes,
        alpha=1e-7,
        d=np.ones(len(d_part)),
        priorities=priorities,
    )

    d_part.drop(columns='index', inplace=True)

    final = out.merge(d_part, how='left', left_index=True, right_index=True)
    final.to_csv(f'{out_name}.csv')
    print('ended')
