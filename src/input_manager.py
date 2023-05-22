"""
Файл с классом InputManager. InputManager отвечает за обработку входных файлов.
"""
from math import ceil
from typing import List

import numpy as np
import pandas as pd
import datetime

from src.data_loader import DataLoader


class InputManager:

    def __init__(self):
        pass

    def read_data(self) -> pd.DataFrame:
        """
        Прочитать файл/архив и вернуть
        :return:
        """
        pass

    def read_config(self, config) -> dict:
        """
        Считать информацию о конфигурации расчета (что учитываем и с какими весами)
        :param config:
        :return:
        """
        pass

    def prepare_data(self):
        pass

    def get_mutex(self, df):
        """
        Generates mutexes. Находит наличие одинаковых возможностей у разных спутников.
        :param new_table: словарь типа "имя спутника : [возможности для этого спутнкиа]"
        :return:
        """

        tmp_df = pd.DataFrame()
        # tmp_df['index'] = df.index
        tmp_df['origin'] = df.origin
        tmp_df = tmp_df[~tmp_df['origin'].str.contains('Russia')]
        tmp_df['data'] = df[['start_datetime', 'end_datetime']].apply(tuple, axis=1)

        res_mutex = []
        for uv in tmp_df['data'].unique():
            tmp = tmp_df[tmp_df['data'] == uv].index.values
            if len(tmp) > 1:
                res_mutex.append(tmp)
        return res_mutex

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

    def restrict_by_duration(self, df, max_duration):
        df_list = []
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
        res_df = pd.DataFrame(df_list).reset_index()

        return res_df

    def separate_by_others(self, dfs: List[pd.DataFrame]):
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

    def basic_data_pipeline(self,
                            satellites: List[str],
                            stations: List[str],
                            max_duration):
        data = self.load_data_for_calculation(satellites, stations)
        data_after_separation = self.separate_by_others(data)
        data_with_restrict = self.restrict_by_duration(data_after_separation, max_duration)
        data_with_restrict.drop(columns=['index'])
        return data_with_restrict

    def get_mask(self, prepared_data):
        return np.array(prepared_data[prepared_data['origin'].str.contains('Russia')].index.to_list())

    def get_priorites(self, prepared_data):
        priorites = np.zeros(len(prepared_data))
        mask = self.get_mask(prepared_data)
        priorites[mask] = 1
        return priorites

    def get_opportunity_memory_sizes(self, prepared_data, imaging_speed=512, dl_speed=128):
        opportunity_memory_sizes = np.ones(len(prepared_data))
        mask = self.get_mask(prepared_data)
        opportunity_memory_sizes[mask] *= imaging_speed
        opportunity_memory_sizes[~mask] *= dl_speed
        return opportunity_memory_sizes

    def get_imaging_indexes(self, prepared_data):
        mask = self.get_mask(prepared_data)
        return np.where(mask)[0]

    def get_downlink_indexes(self, prepared_data):
        mask = self.get_mask(prepared_data)
        return np.where(~mask)[0]

    def get_belongings(self, prepared_data):
        return prepared_data['origin'].str[-14:]

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

    d = manager.basic_data_pipeline(['KinoSat_110301', 'KinoSat_110302', 'KinoSat_110401', 'KinoSat_110402'],
                                    ['Moscow'], 150)
    mutex = manager.get_mutex(d)
    p = manager.get_priorites(d)
    a = manager.get_belongings(d)
    b = manager.get_belongings_dict(d)
    print()
