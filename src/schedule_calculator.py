"""
Файл с классом калькулятора расписаний.
"""
import pandas as pd
from ortools.linear_solver import pywraplp
import numpy as np
from itertools import combinations
import sys


class ScheduleCalculator:

    def __init__(self):
        pass

    def __get_pairs(self, s) -> list:
        return list(combinations(s, 2))

    def __prev_con_id(self, con_id, op_sat_id, op_sat_id_dict) -> int:
        prev_con = None
        sat_key = op_sat_id[con_id]
        for el in op_sat_id_dict[sat_key]:
            if el == con_id:
                return prev_con
            prev_con = el

    def __cond_for_moment_i(self, con_id, op_sat_id_dict):
        res = {}
        for k in op_sat_id_dict:
            for el in op_sat_id_dict[k]:
                if el >= con_id:
                    break
            res[k] = el
        return res

    def calculate(
            self,
            config_data,
            num_opportunities,
            cap,
            s_mutex,
            s_img,
            s_dl,
            op_sat_id,
            op_sat_id_dict,
            opportunity_memory_sizes,
            alpha,
            priorities,
            d=None,
    ) -> pd.DataFrame:
        if d is None:
            d = np.ones(num_opportunities)
        solver = pywraplp.Solver('Satellite', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

        x = [solver.IntVar(0, 1, f'x{i}') for i in range(num_opportunities)]
        y = [solver.NumVar(0, cap, f'y{i}') for i in range(num_opportunities)]

        objective = solver.Objective()

        for el in s_mutex:
            for l, r in self.__get_pairs(el):
                solver.Add(x[l] + x[r] <= 1)

        # Определяем ограничения
        for i in range(num_opportunities):
            # if i in s_img:
            #     solver.Add(x[i] <= y[i])
            pr_con_id = self.__prev_con_id(i, op_sat_id, op_sat_id_dict)
            tmp = 0
            if pr_con_id is not None:
                tmp = y[pr_con_id]
            if i in s_img:
                solver.Add(y[i] == tmp + opportunity_memory_sizes[i] * x[i])
            if i in s_dl:
                solver.Add(y[i] >= tmp - opportunity_memory_sizes[i] * x[i])
                solver.Add(y[i] <= tmp)

        res = 0
        for i in range(num_opportunities):
            res -= x[i] * priorities[i]
            for k in self.__cond_for_moment_i(i, op_sat_id_dict).values():
                res += y[k] * alpha * d[k]
        solver.Minimize(res)

        # Решаем задачу
        # solver.SetTimeLimit(10)
        status = solver.Solve()

        original_stdout = sys.stdout # Save a reference to the original standard output
        with open('out.txt', 'w') as f:
            sys.stdout = f # Change the standard output to the file we created.
            print(f'{solver.wall_time()} ms')

            # Выводим результаты
            if status == pywraplp.Solver.OPTIMAL:
                print('Решение найдено')
                print(f'Сумма приоритетов: {objective.Value()}')
                for i in range(num_opportunities):
                    s = sum([round(y[k].solution_value()) for k in
                            self.__cond_for_moment_i(i, op_sat_id_dict).values()])
                    print(
                        f'x{i}: {x[i].solution_value()}, y{i}: {round(y[i].solution_value())}, sat # {op_sat_id[i]}, sum={s}')
            else:
                print('Решение не найдено')
            sys.stdout = original_stdout 
