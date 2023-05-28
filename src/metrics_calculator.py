"""
Файл с классом калькулятора метрик.
"""

import pandas as pd


def prep(res: pd.DataFrame):
    res['facility'] = res['origin'].apply(lambda x: x.split('-')[1])
    res['action_type'] = res['origin'].apply(lambda x: 1 if x.split('-')[0] == 'Russia' else -1)
    res['real_duration'] = res['is_used_opportunity'] * res['duration']

    return res


def working_ratio_dl(res):
    # Доля работы при наличии возможности сброса
    return res[res.action_type == -1]['real_duration'].sum() / res[res.action_type == -1]['duration'].sum()


def working_ratio_img(res):
    # Доля работы при наличии возможности сбора
    return res[res.action_type == 1]['real_duration'].sum() / res[res.action_type == 1]['duration'].sum()


def working_ratio(res):
    # Доля работы при наличии возможности
    res['real_duration'].sum() / res['duration'].sum()


def ostatok(res):
    # Остаток на конец периода
    return res['transfered_data'].sum()


def total_imged(res):
    # Общее кол-во записанных данных
    return res[res['action_type'] == 1]['transfered_data'].sum()


def total_dl(res):
    # Общее кол-во сброшенных данных
    return res[res['action_type'] == -1]['transfered_data'].sum() * -1
