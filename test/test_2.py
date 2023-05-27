import pytest
import pandas as pd
import os
import pprint

out_filename = 'final_left_join_index.csv'

class TestInfoConservation:
    def test_total_summ_data(self, out_file_path=os.path.join(os.path.dirname(os.getcwd()), out_filename)):
        df = pd.read_csv(out_file_path)
        s = sum(df['transfered_data'])
        assert s == 0, 'Total sum of imaging and downlinking amount of data must be equal to 0'
    

    def test_check_one_zero_opp_data_amount(self, out_file_path=os.path.join(os.path.dirname(os.getcwd()), out_filename)):
        df = pd.read_csv(out_file_path)
        for _, el in df.iterrows():
            normal = True
            if el['is_used_opportunity'] == 0 and el['transfered_data'] == 1:
                normal = False
            assert normal == True, 'If 0 amount data transferred - opp must not be used'


    def test_check_memory_overflow_satellite(self, out_file_path=os.path.join(os.path.dirname(os.getcwd()), out_filename),
                                        kinosat_cap=10 ** 6, zorkiy_cap=0.5 * 10 ** 6):
        df = pd.read_csv(out_file_path)

        sattelites_data_dict = dict()
        for _, el in df.iterrows():
            if el['origin'][-14:] not in sattelites_data_dict:
                sattelites_data_dict[el['origin'][-14:]] = el['transfered_data']
            else:
                sattelites_data_dict[el['origin'][-14:]] += el['transfered_data']

            max_cap = kinosat_cap if int(el['origin'][-4:-2]) <= 5 else zorkiy_cap

            assert sattelites_data_dict[el['origin'][-14:]] <= max_cap, f'Sattelite memory overflowed!\n\ndict: {sattelites_data_dict}'


    def test_check_proper_sign_for_downlink_and_imaging(self, out_file_path=os.path.join(os.path.dirname(os.getcwd()), out_filename)):
        df = pd.read_csv(out_file_path)

        is_ok_downlinking = True
        is_ok_imaging = True
        for index, el in df.iterrows():
            if el['origin'][0:6] == 'Russia' and el['transfered_data'] < 0:
                is_ok_imaging = False

            if el['origin'][0:6] != 'Russia' and el['transfered_data'] > 0:
                is_ok_downlinking = False
            
            assert is_ok_imaging and is_ok_downlinking, f'Wrong sign of transferring data\n ' \
                                                        f'imaging {is_ok_imaging}\n downlinking {is_ok_downlinking}\n ' \
                                                        f'Way: {el["origin"]}\n ' \
                                                        f'Amount data: {el["transfered_data"]}\n '\
                                                        f'Index: {index}'