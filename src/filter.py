"""
filter.py

Utilities to enumerate models of a TwoSAT instance, filter out spurious assignments using
exclude_conditions (produced by transformer.transform_3sat_to_2sat), and project models
back to the original variables (removing auxiliaries).
"""

from typing import List, Dict, Generator, Optional, Tuple, Set
from two_sat_solver import TwoSAT

def _lit_index_for(var: int, val: bool) -> int:
    return 2 * var + (0 if val else 1)

def _propagate_from_literals(ts: TwoSAT, start_lits: List[int]) -> Tuple[bool, Set[int]]:
    g = ts.g
    visited = set()
    stack = list(start_lits)
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        if (v ^ 1) in visited:
            return False, visited
        for to in g[v]:
            if to not in visited:
                stack.append(to)
    for lit in list(visited):
        if (lit ^ 1) in visited:
            return False, visited
    return True, visited

def _derive_partial_assignment_from_true_lits(n_vars: int, true_lits: Set[int]) -> Dict[int, bool]:
    assign = {}
    for lit in true_lits:
        var = lit // 2
        is_true_lit = (lit % 2 == 0)
        if var in assign:
            continue
        assign[var] = is_true_lit
    return assign

def enumerate_2sat_models(ts: TwoSAT, max_models: Optional[int] = None) -> Generator[List[bool], None, None]:
    n = ts.n
    sat, one_assign = ts.solve()
    if not sat:
        return
        yield
    assigned: Dict[int, bool] = {}
    true_lits: Set[int] = set()
    yielded = 0
    def choose_var() -> Optional[int]:
        for i in range(n):
            if i not in assigned:
                return i
        return None
    def backtrack():
        nonlocal yielded
        var = choose_var()
        if var is None:
            full = [False] * n
            for i in range(n):
                full[i] = assigned.get(i, False)
            yielded += 1
            yield full
            if max_models is not None and yielded >= max_models:
                return
            return
        for val in (True, False):
            lit = _lit_index_for(var, val)
            start_lits = list(true_lits) + [lit]
            consistent, new_true_lits = _propagate_from_literals(ts, start_lits)
            if not consistent:
                continue
            implied = _derive_partial_assignment_from_true_lits(n, new_true_lits)
            conflict = False
            for vv, vvval in implied.items():
                if vv in assigned and assigned[vv] != vvval:
                    conflict = True
                    break
            if conflict:
                continue
            newly_set = [k for k in implied.keys() if k not in assigned]
            prev_assigned_vals = {k: assigned.get(k) for k in newly_set}
            for k in newly_set:
                assigned[k] = implied[k]
            prev_true_lits = set(true_lits)
            true_lits.clear()
            true_lits.update(new_true_lits)
            for res in backtrack():
                yield res
                if max_models is not None and yielded >= max_models:
                    break
            for k in newly_set:
                if prev_assigned_vals[k] is None:
                    assigned.pop(k, None)
                else:
                    assigned[k] = prev_assigned_vals[k]
            true_lits.clear()
            true_lits.update(prev_true_lits)
            if max_models is not None and yielded >= max_models:
                return
        return
    for model in backtrack():
        yield model

def matches_exclusion(assignment: List[bool], cond: Dict[int, bool]) -> bool:
    return all(assignment[idx] == val for idx, val in cond.items())

def filter_models(assignments_iterable, exclude_conditions: List[Dict[int,bool]]) -> List[List[bool]]:
    result = []
    for assign in assignments_iterable:
        excluded = False
        for cond in exclude_conditions:
            if matches_exclusion(assign, cond):
                excluded = True
                break
        if not excluded:
            result.append(assign)
    return result

def solve_and_filter(ts: TwoSAT, aux_map: Dict[int,int], exclude_conditions: List[Dict[int,bool]], num_original_vars: int, max_models: Optional[int] = None) -> Tuple[bool, List[List[bool]]]:
    sat, _ = ts.solve()
    if not sat:
        return False, []
    models_iter = enumerate_2sat_models(ts, max_models=max_models)
    filtered = filter_models(models_iter, exclude_conditions)
    projected = []
    seen = set()
    for full in filtered:
        proj = tuple(full[:num_original_vars])
        if proj not in seen:
            seen.add(proj)
            projected.append(list(proj))
    return (len(projected) > 0), projected

if __name__ == '__main__':
    print('filter.py smoke test')
    from transformer import transform_3sat_to_2sat
    clauses = [(1,2,3), (-1,2,-3)]
    n = 3
    ts, aux_map, excludes = transform_3sat_to_2sat(clauses, n)
    print('aux_map:', aux_map)
    print('exclude_conditions:', excludes)
    sat_flag, projected = solve_and_filter(ts, aux_map, excludes, n, max_models=1000)
    print('sat after filtering?', sat_flag)
    print('projected assignments (original vars):', projected)
