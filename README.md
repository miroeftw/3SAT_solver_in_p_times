# Exploring P = NP through a 3SAT → 2SAT Transformation
This repository presents an experimental approach to transforming 3SAT instances into 2SAT ones in an attempt to study the complexity boundary between P and NP. The central idea is a proposed Transformer that approximates a 3-literal clause using a set of 2-literal clauses plus an auxiliary variable.

While the transformation is not strictly equivalent, it allows exploration of how close such a reduction could come to bridging the P vs NP divide.

Here’s a clear and professional **README.md** draft for your public GitHub repository based on the content of your *P=NP.pdf*.
It highlights your motivation, summarizes the idea, and provides structure for sharing your code and results without overstating any claims.

---

## Background

In computational complexity theory:

* **P**: problems solvable efficiently (in polynomial time).
* **NP**: problems verifiable efficiently.
* **3SAT**: a canonical NP-complete problem.
* **2SAT**: a related but polynomial-time solvable problem.

Since 3SAT is NP-complete and 2SAT is in P, a valid reduction from 3SAT to 2SAT that preserves satisfiability could imply **P = NP**.

This project documents one such attempt and its analysis.

---

## Proposed Transformation

### Notation

* Let $\Phi$ be a CNF formula where each clause has exactly three literals (3SAT instance).
* For each clause $C=(l_1\vee l_2\vee l_3)$ we introduce a fresh auxiliary variable $a_C$.
* Let $\Psi$ be the 2-CNF obtained by replacing each such $C$ by $\textsf{Transformer}(l_1,l_2,l_3,a_C)$.

### Proposition

If $\Phi$ is satisfiable then $\Psi$ is satisfiable.

**Proof (sketch).** Let $v$ be a satisfying assignment for $\Phi$. For each clause $C=(l_1\vee l_2\vee l_3)$ set $a_C := v(l_1)\lor v(l_2)$. Check that all three 2-clauses are satisfied:

* If $v(l_1)$ or $v(l_2)$ is `TRUE` then $a_C$ is `TRUE` and $(\neg l_1\vee a_C)$ and $(\neg l_2\vee a_C)$ hold; $(a_C\vee l_3)$ holds since $a_C$ is `TRUE`.
* If both $v(l_1)$ and $v(l_2)$ are `FALSE` then the clause $C$ must have $v(l_3)$ is `TRUE`, so with $a_C$ is `FALSE` we have $(a_C\vee l_3)$ true and $(\neg l_1\vee a_C)=(\neg l_1\vee\textsf{FALSE})=\neg l_1$ holds because $l_1$ is `FALSE` (so $\neg l_1$ true), and similarly for $\neg l_2$. Hence all clauses of $\Psi$ are satisfied.

### Counterexample

There exist assignments satisfying $\Psi$ that do **not** satisfy $\Phi$. A canonical counterexample for a single clause:
\[
v(l_1)=\textsf{FALSE},\quad v(l_2)=\textsf{FALSE},\quad v(a)=\textsf{TRUE},\quad v(l_3)=\textsf{FALSE},
\]
satisfies $\textsf{Transformer}(l_1,l_2,l_3,a)$ but falsifies $(l_1\vee l_2\vee l_3)$.

Thus $\Psi$ is a *relaxation* of $\Phi$: $\Phi \models \Psi$ but $\Psi \not\models \Phi$.

### Algorithmic pipeline

1. Input: 3SAT instance $\Phi$ with $n$ variables and $m$ clauses.
2. Transform: for each clause $C_i$ introduce $a_i$ and add the 3 two-literal clauses from the transformer.
   Complexity: (O(m)) time and (O(m)) new variables.
3. Run a polynomial-time 2SAT solver on $\Psi$.

   * If $\Psi$ is unsatisfiable ⇒ $\Phi$ is unsatisfiable (by Proposition 1 contrapositive).
   * If $\Psi$ is satisfiable, collect satisfying assignments of $\Psi$ and **filter** those that violate the invariant
     \[
     \text{for any clause }C_i: ; \neg l_{1,i} \land \neg l_{2,i} \land a_i
     \]
     (these are the spurious assignments).
4. If after filtering at least one assignment remains, return `SAT` and the projected assignment onto the original variables. Otherwise return `UNSAT`.

---

## Repository Structure

```
3SAT_solver_in_p_times/
│
├── README.md              # This file
├── docs/                  # Explanatory documents
├── src/
│   ├── transformer.py     # 3SAT → 2SAT transformer
│   ├── two_sat_solver.py  # Polynomial-time 2SAT solver
│   ├── filter.py          # Assignment filtering logic
│   └── main.py            # Entry point for running experiments
├── examples/
│   ├── example_3sat.txt   # Example clauses
│   └── example_output.txt # Result after filtering
└── tests/
```

---

## Goals

* Explore how transformations between NP-complete and polynomial problems behave.
* Provide a clear, reproducible experimental setup.
* Encourage open discussion about algorithmic boundaries.

---

## Contributing

Contributions, critiques, and discussions are welcome!
If you find an edge case, counterexample, or potential refinement of the transformation, please open an issue or submit a pull request.