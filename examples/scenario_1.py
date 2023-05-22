"""
Сценарий 1. Одна съемка, три последовательных передачи
"""

import sys
import os
import numpy as np
sys.path.insert(1, os.path.dirname('src'))

from src.schedule_calculator import ScheduleCalculator


def scenario_1():
    data = {}
    num_opportunities = 4

    # 1 - фоткаем, - 0 сбрасываем
    c = np.array([1, 0, 0, 0], dtype=np.double)  # Priority weights

    # Штраф за то что храним данные на спутнике
    d = np.ones(num_opportunities)

    # Скорость 4 Гб/c - фоткаем, 1 Гб/c - передаем. а - это время возможности * скорость отправки или передачи
    a = np.array([10*1000, 1*1000, 3*1000, 10*1000], dtype=np.double)

    # Это сеты в которых записано то что мы делаем
    s_img =  {0}
    s_dl = {1,2, 3}

    s_mutex = []

    op_sat_id = [0,0,0,0]
    op_sat_id_dict = {0:[0,1,2,3]}
    n_sat = len(data.keys())
    alpha = 0.000001

    # capacity
    cap = 2000 * 1000

    solver = ScheduleCalculator()
    solver.calculate(
        config_data=None,
        num_opportunities = 4, # len(prepared_data)
        c=c, # priority
        d=d, # vezde 1
        a=a, # opportunity_memory
        s_img=s_img, # image_indexes
        s_dl=s_dl,  # dl_indexes
        s_mutex=s_mutex, # mutex
        op_sat_id=op_sat_id,
        op_sat_id_dict=op_sat_id_dict,
        n_sat=n_sat, # remove
        alpha=alpha, # const,
        cap=cap # const
    )

if __name__ == '__main__':
    scenario_1()