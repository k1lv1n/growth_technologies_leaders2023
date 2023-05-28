import datetime
import time
from tkinter import *
from tkinter import filedialog, ttk
from tkinter.filedialog import askopenfile
from tkcalendar import Calendar, DateEntry

import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(1, os.path.dirname('data'))
sys.path.insert(2, os.path.dirname('src'))
from data.station_groups import russian_stations, foreign_stations

from data.satallites_groups import *
from src.input_manager import InputManager
from src.metrics_calculator import *
from src.schedule_calculator import ScheduleCalculator

start_dt = datetime.datetime(2027, 6, 1, 0)
end_dt = datetime.datetime(2027, 6, 1, 10)

def calculate_by_data(sputniks, stations, app,
                      start_dt=datetime.datetime(2027, 6, 1, 0),
                      end_dt=datetime.datetime(2027, 6, 1, 10),
                      step=5):
    print(sputniks, stations)
    print(start_dt, end_dt)
    print(step)
    t_start = time.time()
    manager = InputManager()
    calculator = ScheduleCalculator()

    # try:
    #     start_dt_str = app.call_start.get()
    #     end_dt_str = app.call_end.get()
    # except AttributeError:
    #     start_dt_str = app.call_start.get()
    #     end_dt_str = app.call_end.get()

    # start_dt_str = app.call_start.get()
    # end_dt_str = app.call_end.get()
    # start_dt = datetime.datetime.strptime(start_dt_str, r'%d/%m/%Y')
    # end_dt = datetime.datetime.strptime(end_dt_str,  r'%d/%m/%Y')


    time_step = datetime.timedelta(hours=step)

    num_interations = (end_dt - start_dt) // time_step

    partition_restrict = 2000
    print(num_interations)
    # d.to_csv('restricted_all_sats_all_stations.csv')

    res_dfs = []
    for i in range(1, num_interations + 1):
        modeling_start_datetime = start_dt + datetime.timedelta(hours=step * (i - 1))
        modeling_end_datetime = start_dt + datetime.timedelta(hours=step * i)
        start_timestamp = int(modeling_start_datetime.timestamp())
        end_timestamp = int(modeling_end_datetime.timestamp())
        out_filename = f'by_gui_{start_timestamp}_{end_timestamp}'

        d_part = manager.basic_data_pipeline_all(sputniks, stations, start_dt, end_dt,  partition_restrict)
        print(out_filename)

        # d_part = manager.partition_data_by_modeling_interval(modeling_start_datetime, modeling_end_datetime,
        #                                                      d).reset_index(drop=True)

        s_img = manager.get_imaging_indexes(d_part)
        if not any(s_img):
            #     print('no imaging. Go to next')
            continue
        s_mutex = manager.get_mutex(d_part, sputniks)
        s_dl = manager.get_downlink_indexes(d_part)
        op_sat_id = manager.get_belongings(d_part)
        op_sat_id_dict = manager.get_belongings_dict(d_part)
        opportunity_memory_sizes = manager.get_opportunity_memory_sizes(d_part)
        cap_sat_list = manager.get_capacities(d_part)
        priorities = manager.get_priorites(d_part)
        #
        out = calculator.calculate(
            config_data=None,
            num_opportunities=len(d_part),
            cap=cap_sat_list,
            s_mutex=s_mutex,
            s_img=s_img,
            s_dl=s_dl,
            op_sat_id=op_sat_id,
            op_sat_id_dict=op_sat_id_dict,
            opportunity_memory_sizes=opportunity_memory_sizes,
            alpha=1e-7,
            d=np.ones(len(d_part)),
            priorities=priorities,
        )
        #
        d_part.drop(columns='index', inplace=True)

        res = out.merge(d_part, how='left', left_index=True, right_index=True)
        res_dfs.append(res)
        res.to_csv(f'{out_filename}.csv')
        # app.pb['value'] += i / (num_interations + 1)

    total_time = time.time() - t_start
    res_df = pd.concat(res_dfs)

    res_df_prep = prep(res_df)
    res_df_prep.to_csv('res_df_prep.csv')

    print(working_ratio_dl(res_df_prep))
    print(res_df_prep)
    app.l1.config(text=app.l1['text'] + ' ' + str(round(working_ratio_dl(res_df_prep), 2)))
    app.l2.config(text=app.l2['text'] + ' ' + str(round(working_ratio_img(res_df_prep), 2)))
    app.l3.config(text=app.l3['text'] + ' ' + str(working_ratio(res_df_prep)))
    app.l4.config(text=app.l4['text'] + ' ' + str(round(ostatok(res_df_prep), 2)))
    app.l5.config(text=app.l5['text'] + ' ' + str(round(total_imged(res_df_prep), 2)))
    app.l6.config(text=app.l6['text'] + ' ' + str(round(total_dl(res_df_prep), 2)))
    app.l7.config(text=app.l7['text'] + ' ' + str(total_time))
    app.l8.config(text=app.l8['text'] + ' ' + f'{out_filename}.csv')
    # app.working_ratio_img_metric = working_ratio_img(res_df_prep)
    # app.working_ratio_metric = working_ratio(res_df_prep)
    # app.ostatok_metric = ostatok(res_df_prep)
    # app.total_imged_metric = total_imged(res_df_prep)
    # app.total_dl_metric = total_dl(res_df_prep)

    # return


class Application(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()

        self.sputniks = None
        self.stations = None

        self.start_date = None
        self.end_date = None

        # self.pb = None

    def initUI(self):
        self.choice = []

        self.master.title("GUI for algorithm")
        self.pack(fill=BOTH)

        left_frame = LabelFrame(text="Конфигурация расчета")
        left_frame.pack(side=LEFT, padx=5, pady=5, fill=BOTH)
        right_frame = LabelFrame(text="Результат")
        right_frame.pack(side=RIGHT, padx=5, pady=5, fill=BOTH)

        b1 = Button(left_frame, text='Выбор файла',
                    bg='grey', command=lambda: self.upload_file())
        b1.pack(side=TOP, padx=3, pady=3, fill=X)

        b2 = Button(left_frame, text='Выбор набора спутников',
                    bg='grey', command=lambda: self.ask_multiple_choice_sputniks(sat_group_10))
        b2.pack(side=TOP, padx=3, pady=3, fill=X)
        b3 = Button(left_frame, text='Выбор набора наземных станций',
                    bg='grey', command=lambda: self.ask_multiple_choice_stations(russian_stations))
        b3.pack(side=TOP, padx=3, pady=3, fill=X)

        l_cal_start = Label(left_frame, text='Дата начала расчета')
        l_cal_start.pack(side=TOP, padx=3, pady=3, fill=BOTH)

        self.cal_start = DateEntry(left_frame, background="white", foreground="black")
        self.cal_start.pack(side=TOP, padx=3, pady=3, fill=X)
        self.cal_start.set_date(datetime.datetime(2027, 6, 1, 0))
        start_date = datetime.datetime.strptime(self.cal_start.get(), "%m/%d/%y")

        l_cal_end = Label(left_frame, text='Дата конца расчета')
        l_cal_end.pack(side=TOP, padx=3, pady=3, fill=BOTH)

        self.cal_end = DateEntry(left_frame, background="white", foreground="black")
        self.cal_end.pack(side=TOP, padx=3, pady=3, fill=X)
        self.cal_end.set_date(datetime.datetime(2027, 6, 2, 0))
        end_date = datetime.datetime.strptime(self.cal_end.get(), "%m/%d/%y")
        
        # self.pb = ttk.Progressbar(left_frame, orient="horizontal", value=0)
        # self.pb.pack(side=TOP, padx=3, pady=3, fill=X)
        
        l_w1 = Label(left_frame, text='Шаг рассчета в часах')
        l_w1.pack(side=TOP, padx=3, pady=3, fill=BOTH)
        self.w1 = Scale(left_frame, from_=1, to=24, orient='horizontal')
        self.w1.set(5)
        self.w1.pack()

        b4 = Button(left_frame, text='Запустить расчет',
                    bg='light green', command=lambda: calculate_by_data(self.sputniks, 
                                                                        self.stations, self,
                                                                        start_date,
                                                                        end_date, self.w1.get()))
        b4.pack(side=TOP, padx=3, pady=10, fill=X)

        self.l1 = Label(right_frame, text='Доля сброса данных от потенциально возможной:')
        self.l1.pack(side=TOP, padx=3, pady=3, fill=BOTH)
        self.l2 = Label(right_frame, text='Доля сбора данных от потенциально возможной:')
        self.l2.pack(side=TOP, padx=3, pady=3, fill=BOTH)
        self.l3 = Label(right_frame, text='Общая доля работы от потенциально возможной:')
        self.l3.pack(side=TOP, padx=3, pady=3, fill=BOTH)
        self.l4 = Label(right_frame, text='Остаток данных на всех ЗУ на конец периода в Мбайтах:')
        self.l4.pack(side=TOP, padx=3, pady=3, fill=BOTH)
        self.l5 = Label(right_frame, text='Общее кол-во записанных данных в Мбайтах:')
        self.l5.pack(side=TOP, padx=3, pady=3, fill=BOTH)
        self.l6 = Label(right_frame, text='Общее количество сброшенных данных в Мбайтах:')
        self.l6.pack(side=TOP, padx=3, pady=3, fill=BOTH)
        self.l7 = Label(right_frame, text='Общее время работы алгоритма в секундах:')
        self.l7.pack(side=TOP, padx=3, pady=3, fill=BOTH)
        self.l8 = Label(right_frame, text='Результирующий файл:')
        self.l8.pack(side=TOP, padx=3, pady=3, fill=BOTH)


    def upload_file(self):
        file = filedialog.askopenfilename()
        print(file)

    def ask_multiple_choice_sputniks(self, sputniks):
        window = Tk()
        window.title('')
        window.geometry("650x400+200+200")
        window.resizable(height=False, width=False)
        yscrollbar = Scrollbar(window)
        yscrollbar.pack(side=RIGHT, fill=Y)
        label = Label(window,
                      text="Выберите необходимы спутники для расчета:  ",
                      font=("Times New Roman", 10),
                      padx=10, pady=10)
        label.pack()
        lb = Listbox(window, selectmode="multiple",
                     yscrollcommand=yscrollbar.set)
        lb.pack(padx=10, pady=10,
                expand=YES, fill="both")

        for each_item in range(len(sputniks)):
            lb.insert(END, sputniks[each_item])
            lb.itemconfig(each_item, bg="grey")

        # Attach listbox to vertical scrollbar
        yscrollbar.config(command=lb.yview)
        exit = Button(window, text='Сохранить',
                      bg='green', command=lambda: return_and_destroy_sputniks(lb, window, self))
        exit.pack(pady=2)
        window.mainloop()

    def ask_multiple_choice_stations(self, stations):
        window = Tk()
        window.title('')
        window.geometry("650x400+200+200")
        window.resizable(height=False, width=False)
        yscrollbar = Scrollbar(window)
        yscrollbar.pack(side=RIGHT, fill=Y)
        label = Label(window,
                      text="Выберите необходимы спутники для расчета:  ",
                      font=("Times New Roman", 10),
                      padx=10, pady=10)
        label.pack()
        lb = Listbox(window, selectmode="multiple",
                     yscrollcommand=yscrollbar.set)
        lb.pack(padx=10, pady=10,
                expand=YES, fill="both")

        for each_item in range(len(stations)):
            lb.insert(END, stations[each_item])
            lb.itemconfig(each_item, bg="grey")

        # Attach listbox to vertical scrollbar
        yscrollbar.config(command=lb.yview)
        exit = Button(window, text='Сохранить',
                      bg='green', command=lambda: return_and_destroy_stations(lb, window, self))
        exit.pack(pady=2)
        window.mainloop()


def main():
    root = Tk()
    root.geometry("650x400+200+200")
    root.resizable(height=False, width=False)
    app = Application()
    style = ttk.Style(root)

    style.theme_use('clam')
    root.mainloop()


def return_and_destroy_sputniks(lb, window, app):
    # global res
    res = [lb.get(i) for i in lb.curselection()]
    window.destroy()
    # print(res, lb, window)
    app.sputniks = res
    return res


def return_and_destroy_stations(lb, window, app):
    # global res
    res = [lb.get(i) for i in lb.curselection()]
    window.destroy()
    # print(res, lb, window)
    app.stations = res
    return res


if __name__ == '__main__':
    main()

