from itertools import combinations

import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt

def generate_connections(nodes, mutex):
    def __get_pairs(s):
        return tuple(combinations(s, 2))

    all_possible_pairs = set()
    forbidden_pairs = set()
    for el in mutex:
        for p in __get_pairs(el):
            forbidden_pairs.add(p)
    for pair in __get_pairs(nodes):
        all_possible_pairs.add(pair)

    # print(forbidden_pairs)
    # print(all_possible_pairs)
    res = all_possible_pairs - forbidden_pairs
    # print(res)
    return res



DG = nx.DiGraph()
DG.add_edges_from([[0, 1],
                   [1, 2],
                   [2, 3],
                   [1, 3],
                   [0, 2],
                   ['s', 0],
                   ['s', 1],
                   ['s', 2],
                   ['s', 3],
                   [0, 'e'],
                   [1, 'e'],
                   [2, 'e'],
                   [3, 'e']
                   ])

df = pd.DataFrame(DG.edges, columns=['start', 'end'])
print(df)

i = 1

anc = nx.ancestors(DG, i)
des = nx.descendants(DG, i)
print('des', des)
print('asf', df[((df.end.isin(des)) & (df.start == i)) | (df.start.isin(des) & df.end.isin(des))])

DG_left = nx.DiGraph(list(df[((df.start.isin(anc)) & (df.end == i)) | (df.start.isin(anc) & df.end.isin(anc))].values))
DG_right = nx.DiGraph(list(df[((df.end.isin(des)) & (df.start == i)) | (df.start.isin(des) & df.end.isin(des))].values))

# print(DG_left.edges)
# print('~~~')
# print(DG_right.edges)
# print(DG_right.edges)

print()
print()

end_i = nx.dag_longest_path_length(DG_left) + nx.dag_longest_path_length(DG_right)
print(end_i)

