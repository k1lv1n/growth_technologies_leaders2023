"""
Файл с классом InputManager. InputManager отвечает за обработку входных файлов.
"""
import pandas as pd
import datetime

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

    
    def generate_mutex(self, new_table):
        res = []
        for k in new_table.keys():
            for v in new_table[k]:
                res.append((k, tuple(v), v[0]))
        df = pd.DataFrame.from_records(res)
        df = df.sort_values(by=[2]).reset_index()

        mutex = []
        for uv in df[1].unique():
            tmp = df[df[1] == uv].index.values
            if len(tmp) > 1:
                mutex.append(tmp)

        return mutex
    

    def long_partition(self, timeline, max_time_seconds=175):
        """
        Capacity in MBs
        """
        # imaging_speed = 4 * 128  # Mb / s

        # taking mean
        # max_imaging_time_seconds = 234 # capacity / imaging_speed

        new_timeline = {}
        for satellite in timeline.keys():
            new_intervals = []
            for interval in timeline[satellite]:
                duration = (interval[1] - interval[0]).seconds
                if duration > max_time_seconds:
                    partitions = int(duration // max_time_seconds)
                    l = interval[0]
                    for _ in range(partitions - 1):
                        new_intervals.append([l, l + datetime.timedelta(seconds=max_time_seconds)])
                        l += datetime.timedelta(seconds=max_time_seconds)
                    new_intervals.append([l, interval[1]])
                else:
                    new_intervals.append([interval[0], interval[1]])
                    
            new_timeline[satellite] = new_intervals
        
        return new_timeline


    

    def timeline_partition_overlapping(self, list_dfs, list_satellite_names, start_name='start_datetime', end_name='end_datetime'):
        """
        Example of timeline input
        [
            (Timestamp('2027-06-01 00:00:01'), 'k2'),
            (Timestamp('2027-06-01 00:05:28.157000'), 'k2'),
            (Timestamp('2027-06-01 00:07:48.814000'), 'k1'),
                                ....
        ]
        """
        timeline = []
        for df, satellite_name in zip(list_dfs, list_satellite_names):
            for _, el in df.iterrows():
                timeline.append((el[start_name], satellite_name))
                timeline.append((el[end_name], satellite_name))
        new_table = {}
        is_opened = {}

        for el in sorted(timeline):
            if el[1] not in new_table.keys():
                new_table[el[1]] = [[el[0], None]]
                is_opened[el[1]] = True
                
            opened = [i for i in is_opened.items() if i[1]]
            if not is_opened[el[1]]:
                is_opened[el[1]] = True
                new_table[el[1]].append([el[0], None])

            for opened_el in opened:
                if new_table[opened_el[0]][-1][0] != el[0]:
                    new_table[opened_el[0]][-1][1] = el[0]
                    if opened_el[0] != el[1]:
                        new_table[opened_el[0]].append([el[0], None])
                    else:
                        is_opened[el[1]] = False
        
        return new_table
    

if __name__ == "__main__":
    import time
    import pprint

    manager = InputManager()
    t1 = datetime.datetime.now()
    time.sleep(5)
    t2 = datetime.datetime.now()

    t3 = datetime.datetime.now()
    time.sleep(1)
    t4 = datetime.datetime.now()

    dictionary = {'1': [[t1, t2], [t3, t4]]}

    pprint.pprint(dictionary)
    print()

    a = manager.capacity_partition(timeline=dictionary, capacity=4 * 128)

    pprint.pprint(a)