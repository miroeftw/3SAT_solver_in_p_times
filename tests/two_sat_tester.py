from src.two_sat_solver import TwoSAT

def test_case_1():
    # satisfiable: (x ∨ y) ∧ (¬x ∨ ¬y)
    ts = TwoSAT(2)
    ts.add_clause(0, True, 1, True)   # x ∨ y
    ts.add_clause(0, False, 1, False) # ¬x ∨ ¬y
    sat, assign = ts.solve()
    assert sat and assign is not None
    assert (assign[0] != assign[1])  # exactly one true
    print("test_case_1 OK, assignment:", assign)

def test_case_2():
    # unsatisfiable: (x) ∧ (¬x)
    ts = TwoSAT(1)
    ts.add_clause(0, True, 0, True)   # x ∨ x  (fixes x = True)
    ts.add_clause(0, False, 0, False) # ¬x ∨ ¬x (fixes x = False)
    sat, assign = ts.solve()
    assert not sat and assign is None
    print("test_case_2 OK (unsatisfiable)")

def test_case_3():
    # another satisfiable example
    # (x ∨ y) ∧ (¬x ∨ y) ∧ (¬y ∨ z)
    ts = TwoSAT(3)
    ts.add_clause(0, True, 1, True)    # x ∨ y
    ts.add_clause(0, False, 1, True)   # ¬x ∨ y
    ts.add_clause(1, False, 2, True)   # ¬y ∨ z
    sat, assign = ts.solve()
    assert sat and assign is not None
    # verify assignment satisfies clauses
    def lit_val(a):
        var, is_true = a
        return assign[var] if is_true else (not assign[var])
    for c in ts.get_clauses():
        assert lit_val(c[0]) or lit_val(c[1])
    print("test_case_3 OK, assignment:", assign)

if __name__ == "__main__":
    print("two_sat_tester module executed as script: running a few self-tests...")
    test_case_1()
    test_case_2()
    test_case_3()
    print("All tests passed.")
