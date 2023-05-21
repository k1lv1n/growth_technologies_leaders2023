"""
sample test
"""
import unittest 
import sys
import os
import numpy as np
sys.path.insert(1, os.path.dirname('src'))
from src.schedule_calculator import ScheduleCalculator


class TestScheduleCalculator(unittest.TestCase):
    def setUp(self):
        self.sched_calc = ScheduleCalculator()

    def test_get_pairs(self):
        input_data = "abc"
        expected_output = [("a", "b"), ("a", "c"), ("b", "c")]
        self.assertEqual(self.sched_calc._ScheduleCalculator__get_pairs(input_data), expected_output)

    def test_prev_con_id(self):
        con_id = 2
        op_sat_id = [1, 2, 1, 2]
        op_sat_id_dict = {1: [0, 2], 2: [1, 3]}
        expected_output = 0
        self.assertEqual(self.sched_calc._ScheduleCalculator__prev_con_id(con_id, op_sat_id, op_sat_id_dict), expected_output)

    def test_cond_for_moment_i(self):
        con_id = 2
        op_sat_id_dict = {1: [0, 2], 2: [1, 3]}
        expected_output = {1: 2, 2:3}
        self.assertEqual(self.sched_calc._ScheduleCalculator__cond_for_moment_i(con_id, op_sat_id_dict), expected_output)

    # def test_calculate(self):
    #     config_data = ""
    #     data = {
    #         "num_opportunities": 4,
    #         "cap": 1,
    #         "s_mutex": [(1, 2)],
    #         "op_sat_id": [1, 2, 1, 2],
    #         "op_sat_id_dict": {1: [0, 2], 2: [1, 3]},
    #         "s_img": [0, 2],
    #         "a": [0, 1, 0, 1],
    #         "s_dl": [1, 3],
    #         "c": [1, 2, 3, 4],
    #         "alpha": 2,
    #         "d": [5, 6, 7, 8]
    #     }
    #     expected_output = pd.DataFrame({'x': [0.0, 1.0, 0.0, 1.0], 'y': [0.0, 1.0, 0.0, 0.0]})
    #     self.assertTrue(self.sched_calc.calculate(config_data, **data).equals(expected_output))


if __name__ == '__main__': 
    unittest.main()