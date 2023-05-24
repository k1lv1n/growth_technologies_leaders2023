"""
Файл с классом калькулятора расписаний.
"""
import pandas as pd
from ortools.linear_solver import pywraplp
import numpy as np
from itertools import combinations
import sys

from src.input_manager import timing_decorator


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
        def find_position(arr, new_elem):
            left = 0
            right = len(arr) - 1
            while left <= right:
                mid = (left + right) // 2
                if new_elem == arr[mid]:
                    return mid
                elif new_elem < arr[mid]:
                    right = mid - 1
                else:
                    left = mid + 1
            return left

        res = {}
        for k in op_sat_id_dict:
            pos = find_position(op_sat_id_dict[k], con_id)
            if pos == 0:
                if op_sat_id_dict[k][0] <= con_id:
                    res[k] = op_sat_id_dict[k][0]
            else:
                if pos == len(op_sat_id_dict[k]) or con_id < op_sat_id_dict[k][pos]:
                    res_pos = pos - 1
                else:
                    res_pos = pos
                res[k] = op_sat_id_dict[k][res_pos]

        return res

    @timing_decorator
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
        solver = pywraplp.Solver('Satellite', pywraplp.Solver.CLP_LINEAR_PROGRAMMING)  # fastest yet

        x = [solver.IntVar(0, 1, f'x{i}') for i in range(num_opportunities)]
        y = [solver.NumVar(0, cap, f'y{i}') for i in range(num_opportunities)]

        objective = solver.Objective()

        for el in s_mutex:
            for l, r in self.__get_pairs(el):
                solver.Add(x[l] + x[r] <= 1)

        # Определяем ограничения
        for i in range(num_opportunities):
            # if i in s_img:
            # solver.Add(x[i] <= y[i])
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

        original_stdout = sys.stdout  # Save a reference to the original standard output
        with open('out.txt', 'w') as f:
            sys.stdout = f  # Change the standard output to the file we created.
            print(f'{solver.wall_time()} ms')

            # Выводим результаты
            if status == pywraplp.Solver.OPTIMAL:
                print('Решение найдено')
                print(f'Сумма приоритетов: {objective.Value()}')
                for i in range(num_opportunities):
                    print(i, op_sat_id[i], i in op_sat_id_dict['KinoSat_110301'], i in op_sat_id_dict['KinoSat_110302'])
                    s = sum([round(y[k].solution_value()) for k in
                             self.__cond_for_moment_i(i, op_sat_id_dict).values()])
                    print(
                        f'x{i}: {x[i].solution_value()}, {[round(y[k].solution_value()) for k in self.__cond_for_moment_i(i, op_sat_id_dict).values()]}, {op_sat_id[i]} , {self.__cond_for_moment_i(i, op_sat_id_dict)}')
            else:
                print('Решение не найдено')
            sys.stdout = original_stdout

        transfered_data = []
        s_prev = 0
        for i in range(num_opportunities):
            s = sum([round(y[k].solution_value()) for k in self.__cond_for_moment_i(i, op_sat_id_dict).values()])
            if s_prev != s and x[i].solution_value() > 0:
                transfered_data.append(s - s_prev)
                s_prev = s
            else:
                transfered_data.append(0)

        x_series = pd.Series([x[i].solution_value() for i in range(num_opportunities)], copy=False)

        out_df = pd.DataFrame()
        out_df['is_used_opportunity'] = x_series
        out_df['transfered_date'] = transfered_data
        cleared_df = out_df.drop(out_df[(out_df['is_used_opportunity'] > 0) & (out_df['transfered_date'] == 0)].index)
        return cleared_df
