import datetime
import os
import numpy as np
import sys

sys.path.insert(1, os.path.dirname('data'))
sys.path.insert(2, os.path.dirname('src'))

from data.satallites_groups import *
from data.station_groups import *
from src.schedule_calculator import ScheduleCalculator
from src.input_manager import InputManager


def full_calculation_by_step(step):
    manager = InputManager()
    calculator = ScheduleCalculator()

    june_first = datetime.datetime(2027, 6, 1, 0, 0)
    june_first_fifteenth = datetime.datetime(2027, 6, 15, 0, 0)
    time_step = datetime.timedelta(hours=step)

    num_interations = (june_first_fifteenth - june_first) // time_step

    sat_group = [*sat_group_all]
    stations = [*all_stations]
    partition_restrict = 500
    print(num_interations)
    for i in range(1, num_interations + 1):
        modeling_start_datetime = june_first + datetime.timedelta(hours=step * (i - 1))
        modeling_end_datetime = june_first + datetime.timedelta(hours=step * i)
        start_timestamp = int(modeling_start_datetime.timestamp())
        end_timestamp = int(modeling_end_datetime.timestamp())
        out_filename = f'full_plan_{start_timestamp}_{end_timestamp}'
        print(out_filename)

        d = manager.basic_data_pipeline_all(sat_group, stations, partition_restrict)

        d_part = manager.partition_data_by_modeling_interval(modeling_start_datetime, modeling_end_datetime,
                                                             d).reset_index(drop=True)

        s_mutex = manager.get_mutex(d_part, sat_group)
        print()
        s_img = manager.get_imaging_indexes(d_part)
        s_dl = manager.get_downlink_indexes(d_part)
        op_sat_id = manager.get_belongings(d_part)
        op_sat_id_dict = manager.get_belongings_dict(d_part)
        opportunity_memory_sizes = manager.get_opportunity_memory_sizes(d_part)
        cap_sat_list = manager.get_capacities(d_part)
        priorities = manager.get_priorites(d_part)

        out = calculator.calculate(
            config_data=None,
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
        final.to_csv(f'{out_filename}.csv')


if __name__ == '__main__':
    full_calculation_by_step(1)