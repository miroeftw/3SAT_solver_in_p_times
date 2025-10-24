"""
transformer.py

Clean implementation of the 3SAT -> 2SAT transformer gadget.

Transformer(l1,l2,l3,a) = (¬l1 ∨ a) ∧ (¬l2 ∨ a) ∧ (a ∨ l3)
"""

from typing import List, Tuple, Dict
import sys, os

# ensure local src on path
_this_dir = os.path.dirname(__file__)
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

from two_sat_solver import TwoSAT

def _lit_to_pair(lit: int) -> Tuple[int, bool]:
    if lit == 0:
        raise ValueError("literal cannot be 0")
    return (abs(lit) - 1, lit > 0)

def transform_3sat_to_2sat(clauses: List[Tuple[int,int,int]], num_original_vars: int, aux_prefix: str = 'a') -> Tuple[TwoSAT, Dict[int,int], List[Dict[int,bool]]]:
    m = len(clauses)
    total_vars = num_original_vars + m
    ts = TwoSAT(total_vars)
    aux_map: Dict[int,int] = {}
    exclude_conditions: List[Dict[int,bool]] = []
    for i, (lit1, lit2, lit3) in enumerate(clauses):
        aux_idx = num_original_vars + i
        aux_map[i] = aux_idx
        v1, pos1 = _lit_to_pair(lit1)
        v2, pos2 = _lit_to_pair(lit2)
        v3, pos3 = _lit_to_pair(lit3)
        # (¬l1 ∨ a)
        ts.add_clause(v1, not pos1, aux_idx, True)
        # (¬l2 ∨ a)
        ts.add_clause(v2, not pos2, aux_idx, True)
        # (a ∨ l3)
        ts.add_clause(aux_idx, True, v3, pos3)
        # exclusion: l1 false, l2 false, a true
        cond: Dict[int,bool] = {}
        cond[v1] = (lit1 < 0)
        cond[v2] = (lit2 < 0)
        cond[aux_idx] = True
        exclude_conditions.append(cond)
    return ts, aux_map, exclude_conditions

def transform_to_clause_list(clauses: List[Tuple[int,int,int]], num_original_vars: int):
    clause_list = []
    aux_map = {}
    exclude_conditions = []
    for i, (lit1, lit2, lit3) in enumerate(clauses):
        aux_idx = num_original_vars + i
        aux_map[i] = aux_idx
        v1, pos1 = _lit_to_pair(lit1)
        v2, pos2 = _lit_to_pair(lit2)
        v3, pos3 = _lit_to_pair(lit3)
        clause_list.append(((v1, not pos1), (aux_idx, True)))
        clause_list.append(((v2, not pos2), (aux_idx, True)))
        clause_list.append(((aux_idx, True), (v3, pos3)))
        cond = {v1: (lit1 < 0), v2: (lit2 < 0), aux_idx: True}
        exclude_conditions.append(cond)
    return clause_list, aux_map, exclude_conditions

if __name__ == '__main__':
    print('transformer module smoke test')
    clauses = [(1,2,3), (-1,2,-3)]
    ts, aux_map, excludes = transform_3sat_to_2sat(clauses, 3)
    print('aux_map:', aux_map)
    print('exclude_conditions:', excludes)
    sat, assign = ts.solve()
    print('2SAT sat?', sat)
    if sat:
        print('assignment:', assign)
