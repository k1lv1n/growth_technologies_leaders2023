from datetime import datetime

import pandas as pd


# data = open('1234.txt').read()
def sat_block_to_df(sat_block, datetime_in_ms):
    first_line_marker = sat_block.find('\n')
    first_line = sat_block[:first_line_marker]
    agent_1, _, agent_2 = first_line.split('-')
    second_line_marker = sat_block.find('-\n')
    data_after_column_names = sat_block[sat_block.find('(sec)'):]
    pure_data = data_after_column_names[data_after_column_names.find('-\n') + 2:]
    nums = []
    start_datetimes = []
    end_datetimes = []
    durs = []
    try:
        while True:
            line = pure_data[:pure_data.find('\n')]
            num, start_day, start_month, start_year, start_time, end_day, end_month, end_year, end_time, duration = line.split()
            nums.append(num)
            durs.append(float(duration))
            if not datetime_in_ms:
                start_datetimes.append(
                    pd.to_datetime(start_day + ' ' + start_month + ' ' + start_year + ' ' + start_time))
                end_datetimes.append(pd.to_datetime(end_day + ' ' + end_month + ' ' + end_year + ' ' + end_time))
            else:
                start_datetimes.append(
                    datetime.strptime(start_day + ' ' + start_month + ' ' + start_year + ' ' + start_time,
                                      '%d %b %Y %H:%M:%S.%f').timestamp())
                end_datetimes.append(datetime.strptime(end_day + ' ' + end_month + ' ' + end_year + ' ' + end_time,
                                                       '%d %b %Y %H:%M:%S.%f').timestamp())
            pure_data = pure_data[pure_data.find('\n') + 1:]
    except ValueError:
        pass
    df = pd.DataFrame.from_dict({
        'access': nums,
        'start_datetime': start_datetimes,
        'end_datetime': end_datetimes,
        'duration': durs
    })
    df['counter_agent'] = agent_1
    df['satellite'] = agent_2
    df['connection'] = agent_1 + '-' + agent_2
    return df


if __name__ == '__main__':
    sat_block = open('msc_to_110301.txt').read()
    a, b, c = sat_block_to_df(sat_block)
    print()
