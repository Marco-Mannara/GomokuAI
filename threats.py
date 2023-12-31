import itertools
import re
import networkx as nx
import json 
from tqdm import tqdm
from utils import get_index_transform_func


WINNING_THREAT_TYPES = [(5,1)]
FORCING_THREAT_TYPES = [(4,2),(4,1),(3,3),(3,2)]
NON_FORCING_THREAT_TYPES = [(3,1)]
for i in range(1,3):
    NON_FORCING_THREAT_TYPES.extend([(i,j) for j in range(1, 6 - i + 1)])

def replace_char(string : str, index : int, char):
    return string[:index] + char + string[index + 1:]

def generate_all_sequences_of_len(length : int) -> set:
    all_seqs = set(itertools.product('01', repeat = length))
    all_seqs = {''.join(s) for s in all_seqs}
    all_seqs.remove(''.join(['0' for _ in range(length)]))    

    to_remove = set()
    for s in all_seqs:
        if len(re.findall('1{6,}',s)) > 0:
            to_remove.add(s)

        elif length > 6 and s.count('1') >= length - 1:
            to_remove.add(s)

    all_seqs.difference_update(to_remove)
    return all_seqs

def generate_threat_info(seq : str, lvl : int):    
    if len(list(re.finditer('(?<!1)1{5}(?!1)', seq))) == 1:
        return {seq},{},{}

    n_ones = seq.count('1')
    zeros_pos = [m.span()[0] for m in re.finditer('0', seq)]
    perms = itertools.product('01', repeat=len(zeros_pos))    

    possible_moves = set()
    possible_5s = set()
    for p in perms:        
        candidate = seq[:]

        for i in range(len(zeros_pos)):
            candidate = replace_char(candidate, zeros_pos[i], p[i])

        cand_n_ones = candidate.count('1')

        if cand_n_ones < 5:
            continue            
        if cand_n_ones > 5 and n_ones < 5:
            continue
        if p.count('1') != 5 - lvl:
            continue                

        win_seq_match = list(re.finditer('(?<!1)1{5}(?!1)', candidate))
        if len(win_seq_match) == 1:
            possible_5s.add(candidate)
            ones_pos = [zeros_pos[m.span()[0]] for m in re.finditer('1', ''.join(p))]
            for i in range(len(ones_pos)):
                possible_moves.add((ones_pos[i]))

    best_defences = get_best_defence_for_threat(seq,possible_5s)
    return possible_5s, possible_moves, best_defences    

def get_best_defence_for_threat(threat : str, possible_5s : set) -> list:
    zeros_pos = [m.span()[0] for m in re.finditer('0', threat)]
    n_of_blocks = [0 for _ in range(len(zeros_pos))]
    for five in possible_5s:
        for zi in range(len(zeros_pos)):
            if five[zeros_pos[zi]] == '1':
                n_of_blocks[zi] += 1
    
    max_blocks = max(n_of_blocks)
    best_def = {zeros_pos[i] for i in range(len(zeros_pos)) if n_of_blocks[i] == max_blocks}
    return best_def


def precompute_threats(max_seq_len = 7) -> dict:
    threats = {i:dict() for i in range(5, max_seq_len + 1)}
    all_seqs = {i: generate_all_sequences_of_len(i) for i in range(5, max_seq_len + 1)}
    
    for s in all_seqs[5]:
        lvl = s.count('1')
        p_5s,p_moves,b_def = generate_threat_info(s, lvl)
        sev = len(p_5s)
        if sev == 0:
            continue        
        threats[5][s] = {'type' : (lvl, sev), 'p_moves' : list(p_moves), 'b_def' : list(b_def)}

    for l in tqdm(range(6,max_seq_len + 1)):
        for s in all_seqs[l]:
            lvl = max([threats[5][s[i : i + 5]]['type'][0] for i in range(0, l - 4) if s[i : i + 5] in threats[5].keys()])
            p_5s,p_moves,b_def = generate_threat_info(s,lvl)
            sev = len(p_5s)
            if sev == 0:
                continue
            threats[l][s] = {'type' : (lvl, sev), 'p_moves' : list(p_moves), 'b_def' : list(b_def)}
    return threats

def generate_dependency_graph(threats : dict, black : bool = True) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_nodes_from(threats.keys())
    for seq,info in threats.items():
        for m in info['p_moves']:
            graph.add_edge(seq, replace_char(seq,m,'1' if black else '2'), move = m)               
    return graph        

def store_precomputed_threats(threats, filename = 'threat_data.json'):
    with open(filename, 'w') as file:
        json.dump(threats, file)

def load_precomputed_threats(filename = 'threat_data.json'):
    with open(filename, 'r') as file:
        l_threats = json.load(file)

    b_threats = {}
    w_threats = {}    
    for l in l_threats.keys():
        for seq,info in l_threats[l].items():
            type = info['type']
            p_moves = info['p_moves']
            b_def = info['b_def']

            b_threats[seq] = {
                'type' : (int(type[0]), int(type[1])),
                'p_moves' : [int(m) for m in p_moves],
                'b_def' : [int(d) for d in b_def]
            }
            w_threats[seq.replace('1','2')] = {
                'type' : (int(type[0]), int(type[1])),
                'p_moves' : [int(m) for m in p_moves],
                'b_def' : [int(d) for d in b_def]
            }

    return b_threats, w_threats

#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------
#THREAT CLASS
#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------

class Threat:
    def __init__(self, group : str, info : tuple, span : tuple, angle:int):
        self.group = group
        self.info = info
        self.span = span
        self.angle = angle    
        self.t_func = get_index_transform_func(angle)

    def get_grid_span(self) -> tuple:
        return (self.t_func(self.span[0]), self.t_func(self.span[1]))

    def get_open_slots(self) -> set:
        return {self.t_func(m + self.span[0]) for m in self.info['p_moves']}

    def get_counter_moves(self) -> set:
        return {self.t_func(m + self.span[0]) for m in self.info['b_def']}

    def get_counter_moves_with_offsets(self) -> set:
        return {(m, self.t_func(m + self.span[0])) for m in self.info['b_def']}
        
    def __hash__(self) -> int:        
        return 23 * self.span[0] + 29 * self.span[1] + self.angle * 71 
    
    def __eq__(self, other) -> bool:
        if not isinstance(other,Threat):
            return False        
        #Check
        if self.__hash__() == other.__hash__():
            return True
        return False

    def __str__(self) -> str:
        return '(Threat / group = \'%s\', type = %s, span = (%d, %d), angle = %d°)' % (
            self.group,
            str(self.info['type']),
            self.span[0],
            self.span[1],
            self.angle
            )

def _get_threat_class(threat:Threat):
    info = threat.info
    return _get_threat_class_from_info(info)

def _get_threat_class_from_info(info:dict):
    n = info['type'][0]
    w = info['type'][1]
    n = n if n <= 5 else 5
    w = w if w <= 6 - n else 6 - n
    
    if (n,w) in WINNING_THREAT_TYPES:
        return 'winning'
    elif (n,w) in FORCING_THREAT_TYPES:
        return 'forcing'
    else:
        return 'nforcing'
    
    


if __name__ == '__main__':
    # start_time = time.time()
    # threats = precompute_threats(15)
    # store_precomputed_threats(threats)
    # b_threats, w_threats = load_precomputed_threats()
    
    # b_graph = generate_dependency_graph(b_threats)
    # print(b_graph.number_of_nodes(), b_graph.number_of_edges())
        
    # w_graph = generate_dependency_graph(w_threats, False)
    # print(w_graph.number_of_nodes(), w_graph.number_of_edges())
    # for t in b_threats:
    #     pass

    # print('elapsed time:', round(time.time() - start_time,4))
    info0 = {'type' : (3,5)}
    assert _get_threat_class_from_info(info0) == 'forcing'
    info0 = {'type' : (3,1)}
    assert _get_threat_class_from_info(info0) == 'nforcing'
    info0 = {'type' : (1,5)}
    assert _get_threat_class_from_info(info0) == 'nforcing'
    info0 = {'type' : (5,1)}
    assert _get_threat_class_from_info(info0) == 'winning'


B_THREAT_DATA, W_THREAT_DATA = load_precomputed_threats()
B_THREAT_DEP = generate_dependency_graph(B_THREAT_DATA)
W_THREAT_DEP = generate_dependency_graph(W_THREAT_DATA)