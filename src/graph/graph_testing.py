from itertools import combinations

import networkx as nx
import pandas as pd
import os
import sys

sys.path.insert(1, os.path.dirname('src'))

from src.input_manager import measure_memory_and_time


@measure_memory_and_time
def generate_edges(nodes: list, mutex):
    def __get_pairs(s):
        return tuple(combinations(s, 2))

    all_possible_pairs = set()
    forbidden_pairs = set()
    for el in mutex:
        for p in __get_pairs(el):
            forbidden_pairs.add(p)
    forbidden_pairs.add(('s', 'e'))
    for pair in __get_pairs(nodes + ['s', 'e']):
        all_possible_pairs.add(pair)
    res = all_possible_pairs - forbidden_pairs
    return res


@measure_memory_and_time
def get_graph_cum_priority(graph):
    return nx.dag_longest_path_length(graph)


@measure_memory_and_time
def get_opportunity_cum_priority(graph, op_id):
    df = pd.DataFrame(graph.edges, columns=['start', 'end'])

    anc = nx.ancestors(graph, op_id)
    des = nx.descendants(graph, op_id)

    left_net = nx.DiGraph(
        list(df[((df.start.isin(anc)) & (df.end == op_id)) | (df.start.isin(anc) & df.end.isin(anc))].values))
    right_net = nx.DiGraph(
        list(df[((df.end.isin(des)) & (df.start == op_id)) | (df.start.isin(des) & df.end.isin(des))].values))

    end_i = nx.dag_longest_path_length(left_net) + nx.dag_longest_path_length(right_net)
    return end_i


if __name__ == '__main__':
    from src.input_manager import InputManager, measure_memory_and_time
    from src.schedule_calculator import ScheduleCalculator

    manager = InputManager()
    calculator = ScheduleCalculator()
    d = manager.basic_data_pipeline_imging(['KinoSat_110101',], max_duration=15000)
    print(len(d))
    m = manager.get_mutex(d, ['KinoSat_110101'])
    nodes = d.index.to_list()

    e = generate_edges(nodes, m)
    g = nx.DiGraph()
    g.add_edges_from(e)
    c_end = get_graph_cum_priority(g)
    print(c_end)
    for i in range(0, 470, 10):
        print(i, get_opportunity_cum_priority(g, i))
