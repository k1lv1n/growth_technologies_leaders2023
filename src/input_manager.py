"""
Файл с классом InputManager. InputManager отвечает за обработку входных файлов.
"""
import time
from math import ceil
from typing import List

import numpy as np
import pandas as pd
# from alive_progress import alive_bar

from src.data_loader import DataLoader

from memory_profiler import memory_usage


def measure_memory_and_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        peak_memory, result = memory_usage((func, args, kwargs), max_usage=True, retval=True)
        end_time = time.time()
        print(
            f"Peak memory usage: {peak_memory:.2f} MiB. Function {func.__name__} took {end_time - start_time:.5f} seconds to run.")
        return result

    return wrapper


class InputManager:

    def __init__(self):
        pass

    @measure_memory_and_time
    def get_mutex_no_russia(self, df):
        """
        Generates mutexes. Находит наличие одинаковых возможностей у разных спутников.
        :param new_table: словарь типа "имя спутника : [возможности для этого спутнкиа]"
        :return:
        """

        tmp_df = pd.DataFrame()
        tmp_df['origin'] = df.origin
        tmp_df = tmp_df[~tmp_df['origin'].str.contains('Russia')]
        tmp_df['data'] = df[['start_datetime', 'end_datetime']].apply(tuple, axis=1)

        res_mutex = [list(group.index) for _, group in tmp_df.groupby('data') if len(group) > 1]
        return res_mutex

    @measure_memory_and_time
    def get_mutex_for_sat(self, df, sat_name):
        tmp_df = df[df['origin'].str[-len(sat_name):] == sat_name].copy()
        tmp_df['data'] = df[['start_datetime', 'end_datetime']].apply(tuple, axis=1)
        res_mutex_for_sat = [list(group.index) for _, group in tmp_df.groupby('data') if len(group) > 1]
        return res_mutex_for_sat

    @measure_memory_and_time
    def get_mutex(self, d, satellites):
        all_mutex = self.get_mutex_no_russia(d)
        # with alive_bar(len(satellites), bar='halloween') as bar:
        for s in satellites:
            all_mutex += self.get_mutex_for_sat(d, s)
            # bar()
        return all_mutex

    def get_capacities(self, prepared_data, kinosat_cap=10 ** 6, zorkiy_cap=0.5 * 10 ** 6):
        res_capcity = np.zeros(len(prepared_data))

        mask = prepared_data.origin.str[-4:-2].astype(int) <= 5
        res_capcity[mask] = kinosat_cap
        res_capcity[~mask] = zorkiy_cap

        return res_capcity

    @measure_memory_and_time
    def load_data_for_calculation(self,
                                  satellites: List[str],
                                  stations: List[str]):
        data_loader = DataLoader()
        result_dict = []
        # load data for Earth
        for sat in satellites:
            earth_sat_data = data_loader.get_data_for_sat_russia(sat, datetime_in_ms=True)
            result_dict.append(earth_sat_data)
        for station in stations:
            # result_dict[station] = []
            for sat in satellites:
                station_sat_data = data_loader.get_data_for_sat_station(sat, station, datetime_in_ms=True)
                result_dict.append(station_sat_data)
        return result_dict

    @measure_memory_and_time
    def load_data_for_calculation_dl(self, satellites: List[str], stations: List[str]):
        data_loader = DataLoader()
        data = []
        # load data for Earth
        for sat in satellites:
            for station in stations:
                earth_sat_data = data_loader.get_data_for_sat_station(sat, station, datetime_in_ms=True)
                data.append(earth_sat_data)

        return data

    @measure_memory_and_time
    def restrict_by_duration(self, df, max_duration):
        new_df_size = sum(df.duration // max_duration) + sum(df.duration % max_duration != 1)
        df_list = [None] * max_duration
        for _, row in df.iterrows():
            if row['duration'] <= max_duration:
                df_list.append(row)
            else:
                n_splits = ceil(row['duration'] / max_duration)
                for i in range(n_splits):
                    new_row = row.copy()
                    new_row['start_datetime'] = row['start_datetime'] + i * max_duration
                    new_row['duration'] = min(max_duration, row['duration'] - i * max_duration)
                    new_row['end_datetime'] = new_row['start_datetime'] + new_row['duration']
                    df_list.append(new_row)
        res_df = pd.DataFrame(df_list)

        return res_df

    @measure_memory_and_time
    def restrict_by_duration_ai(self, df, max_duration):
        df_filtered = df.loc[df['duration'] <= max_duration]
        df_splits = [row for _, row in df.loc[df['duration'] > max_duration].iterrows()
                     for i in range(int(row['duration'] // max_duration))]
        df_splits += [row.copy() for _, row in df.loc[df['duration'] > max_duration].iterrows()
                      if row['duration'] % max_duration > 0]
        for i, row in enumerate(df_splits):
            row['start_datetime'] += i * max_duration
            row['duration'] = min(max_duration, row['duration'] - i * max_duration)
            row['end_datetime'] = row['start_datetime'] + row['duration']
        res_df = pd.concat([df_filtered, pd.DataFrame(df_splits)]).reset_index(drop=True)
        return res_df

    @measure_memory_and_time
    def separate_by_others(self, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        points = []
        is_begins = []
        origin_dfs = []
        for df in dfs:
            for _, row in df.iterrows():
                points.extend([row.start_datetime, row.end_datetime])
                is_begins.extend([1, 0])
                origin_dfs.extend([row.connection, row.connection])

        tmp_df = pd.DataFrame.from_dict({'point': points,
                                         'is_begin': is_begins,
                                         'origin_df': origin_dfs
                                         }).sort_values('point')

        opened = set()
        result_starts = []
        result_ends = []
        result_origin_dfs = []
        prev_point = None

        for _, row in tmp_df.iterrows():
            for o in opened:
                result_starts.append(prev_point)
                result_ends.append(row.point)
                result_origin_dfs.append(o)
            if row.is_begin:
                opened.add(row.origin_df)
            else:
                opened.remove(row.origin_df)
            prev_point = row.point

        result_df = pd.DataFrame.from_dict({'start_datetime': result_starts,
                                            'end_datetime': result_ends,
                                            'origin': result_origin_dfs
                                            })
        result_df['duration'] = result_df.end_datetime - result_df.start_datetime
        return result_df

    def basic_data_pipeline_all(self,
                                satellites: List[str],
                                stations: List[str],
                                modeling_start,
                                modeling_end,
                                max_duration) -> pd.DataFrame:
        data = self.load_data_for_calculation(satellites, stations)
        data_after_separation = self.separate_by_others(data)
        data_for_time_window = self.partition_data_by_modeling_interval(modeling_start,
                                                                        modeling_end,
                                                                        data_after_separation)
        data_after_separation_no_short = data_for_time_window[data_for_time_window.duration > 1]
        data_with_restrict = self.restrict_by_duration(data_after_separation_no_short, max_duration)  # 20 sec
        return data_with_restrict.reset_index().sort_index()

    # def basic_data_pipeline_dl(self,
    #                            satellites: List[str],
    #                            stations: List[str],
    #                            max_duration):
    #     data = self.load_data_for_calculation_dl(satellites, stations)
    #     data_after_separation = self.separate_by_others(data)
    #     data_after_separation_no_short = data_after_separation[data_after_separation.duration > 1]
    #     if max_duration:
    #         data_with_restrict = self.restrict_by_duration(data_after_separation_no_short, max_duration)  # 20 sec
    #         return data_with_restrict.sort_index()
    #     else:
    #         return data_after_separation_no_short.sort_index()

    @measure_memory_and_time
    def partition_data_by_modeling_interval(self, modeling_start, modeling_end, prepared_data):
        ts, te = modeling_start.timestamp(), modeling_end.timestamp()

        return prepared_data[(prepared_data.start_datetime >= ts) & (prepared_data.end_datetime <= te)]

    def basic_data_pipeline_imging(self,
                                   satellites: List[str],
                                   max_duration):
        data_loader = DataLoader()
        data = []
        # load data for Earth
        for sat in satellites:
            russia_sat_data = data_loader.get_data_for_sat_russia(sat, datetime_in_ms=True)
            data.append(russia_sat_data)
        data_after_separation = self.separate_by_others(data)
        data_after_separation_no_short = data_after_separation[data_after_separation.duration > 1]
        data_with_restrict = self.restrict_by_duration(data_after_separation_no_short, max_duration)  # 20 sec
        return data_with_restrict.sort_index()

    def get_russia_mask(self, prepared_data):
        return prepared_data['origin'].str.contains('Russia')
        # return prepared_data.index.isin(prepared_data[prepared_data['origin'].str.contains('Russia')].index)

    @measure_memory_and_time
    def get_priorites(self, prepared_data):
        priorites = np.zeros(len(prepared_data))
        mask = self.get_russia_mask(prepared_data)
        priorites[mask] = 1
        return priorites

    @measure_memory_and_time
    def get_opportunity_memory_sizes(self, prepared_data, imaging_speed=512, kinosat_dl_speed=128, zorkiy_dl_speed=32):

        opportunity_memory_sizes = prepared_data.duration.copy()
        mask = self.get_russia_mask(prepared_data)
        opportunity_memory_sizes[mask] *= imaging_speed

        mask_sattelite_type = prepared_data.origin.str[-4:-2].astype(int) <= 5

        opportunity_memory_sizes[(~mask) & (mask_sattelite_type)] *= kinosat_dl_speed
        opportunity_memory_sizes[(~mask) & (~mask_sattelite_type)] *= zorkiy_dl_speed

        return opportunity_memory_sizes

    def get_imaging_indexes(self, prepared_data):
        mask = self.get_russia_mask(prepared_data)
        return np.where(mask)[0]

    def get_downlink_indexes(self, prepared_data):
        mask = self.get_russia_mask(prepared_data)
        return np.where(~mask)[0]

    @measure_memory_and_time
    def get_belongings(self, prepared_data):
        return prepared_data['origin'].str[-14:]

    @measure_memory_and_time
    def get_belongings_dict(self, prepared_data):
        belongings = list(self.get_belongings(prepared_data))
        my_dict = {}
        for i, b in enumerate(belongings):
            if b in my_dict:
                my_dict[b].append(i)
            else:
                my_dict[b] = [i]
        return my_dict


if __name__ == "__main__":
    manager = InputManager()

    d = manager.basic_data_pipeline_all(['KinoSat_110301'], ['Moscow'], 50)
    # mutex = manager.get_mutex(d)
    # p = manager.get_priorites(d)
    a = manager.get_belongings(d)
    b = manager.get_belongings_dict(d)
    print()
