"""two_sat_solver.py

A compact, dependency-free 2-SAT solver using Kosaraju's algorithm for SCCs.
Provides a TwoSAT class with the following interface:

    ts = TwoSAT(n)
    ts.add_clause(i, is_true_i, j, is_true_j)  # add (lit_i ∨ lit_j)
    sat, assignment = ts.solve()  # returns (is_satisfiable, Optional[assignment list])

Literals are given as (variable_index, boolean):
    - variable_index: 0-based index of variable
    - boolean flag: True for the positive literal (x), False for negation (¬x)

Assignment (when satisfiable) is a list of booleans of length n mapping variable -> boolean value.

This implementation is production-quality for experiments and teaching: clear API, type hints,
docstrings, and predictable behavior.
"""

from typing import List, Tuple, Optional

class TwoSAT:
    def __init__(self, n: int) -> None:
        """Initialize a TwoSAT solver for `n` boolean variables (indexed 0..n-1)."""
        if n <= 0:
            raise ValueError("n must be positive")
        self.n = n
        self.N = 2 * n  # number of literal nodes
        self.g: List[List[int]] = [[] for _ in range(self.N)]
        self.rg: List[List[int]] = [[] for _ in range(self.N)]
        self.clauses: List[Tuple[Tuple[int,bool], Tuple[int,bool]]] = []

    @staticmethod
    def _lit_index(var: int, is_true: bool) -> int:
        """Return internal index for literal (var, is_true).
        Encoding: index = 2*var + (0 if is_true else 1).
        The negation of a literal index l is l ^ 1.
        """
        return 2 * var + (0 if is_true else 1)

    def _add_implication(self, u: int, v: int) -> None:
        """Add edge u -> v to the implication graph (and reverse graph)."""
        self.g[u].append(v)
        self.rg[v].append(u)

    def add_clause(self, i: int, is_true_i: bool, j: int, is_true_j: bool) -> None:
        """Add clause (lit_i ∨ lit_j) where lit_i = (i if is_true_i else ¬i).
        This is encoded as two implications: (¬lit_i ⇒ lit_j) and (¬lit_j ⇒ lit_i).
        Parameters must satisfy 0 <= i,j < n.
        """
        if not (0 <= i < self.n and 0 <= j < self.n):
            raise IndexError("variable index out of range")
        li = self._lit_index(i, is_true_i)
        lj = self._lit_index(j, is_true_j)
        # ¬li -> lj
        self._add_implication(li ^ 1, lj)
        # ¬lj -> li
        self._add_implication(lj ^ 1, li)
        self.clauses.append(((i, is_true_i), (j, is_true_j)))

    def solve(self) -> Tuple[bool, Optional[List[bool]]]:
        """Decide satisfiability. If satisfiable, return (True, assignment_list).
        Otherwise return (False, None).

        Complexity: O(N + E) where N=2*n (literals) and E is number of implications.
        """
        order: List[int] = []
        used = [False] * self.N

        def dfs(v: int) -> None:
            used[v] = True
            for to in self.g[v]:
                if not used[to]:
                    dfs(to)
            order.append(v)

        for v in range(self.N):
            if not used[v]:
                dfs(v)

        comp = [-1] * self.N
        cid = 0

        def rdfs(v: int, cl: int) -> None:
            comp[v] = cl
            for to in self.rg[v]:
                if comp[to] == -1:
                    rdfs(to, cl)

        for v in reversed(order):
            if comp[v] == -1:
                rdfs(v, cid)
                cid += 1

        # check for contradictions
        for var in range(self.n):
            if comp[2 * var] == comp[2 * var + 1]:
                return False, None

        # build assignment: variable is true iff comp[true_lit] > comp[false_lit]
        assignment = [False] * self.n
        for var in range(self.n):
            assignment[var] = comp[2 * var] > comp[2 * var + 1]

        return True, assignment

    def get_clauses(self) -> List[Tuple[Tuple[int,bool], Tuple[int,bool]]]:
        """Return a copy of stored clauses."""
        return list(self.clauses)


# Helper utility: parse a small textual format for 2-SAT clauses
def parse_clause_line(line: str):
    """Parse a line like '1 -2' or '-1 3' into ((var0, sign0), (var1, sign1)).
    Variables in the textual format are 1-based; negative sign indicates negation.
    Returns a tuple ((v0, is_true0), (v1, is_true1)).
    """
    parts = line.strip().split()
    if len(parts) != 2:
        raise ValueError("Expected exactly two literals per line for 2-CNF format")
    def lit_from_token(tok: str):
        val = int(tok)
        is_true = val > 0
        var = abs(val) - 1
        return (var, is_true)
    return lit_from_token(parts[0]), lit_from_token(parts[1])
