#!/usr/bin/env python3
"""
main.py

Command-line runner for the 3SAT -> 2SAT pipeline:

  parse 3-CNF (DIMACS or a simple 3-int-per-line format) ->
  transform via transformer.transform_3sat_to_2sat ->
  run two-sat solver ->
  enumerate + filter spurious assignments using filter.solve_and_filter ->
  project results to original variables and print/save.

Usage examples:
  python src/main.py --input examples/example_3sat.cnf
  python src/main.py --input examples/example_3sat.cnf --max-models 5000 --out results.txt
"""
from typing import List, Tuple
import argparse
import sys
import os

from transformer import transform_3sat_to_2sat
from filter import solve_and_filter
from two_sat_solver import TwoSAT

def parse_dimacs_3cnf(path: str) -> Tuple[List[Tuple[int,int,int]], int]:
    """
    Parse a DIMACS CNF file and return a list of 3-literal clauses and num_vars.
    Only supports clauses with exactly 3 literals (will raise otherwise).
    """
    clauses = []
    num_vars = None
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if len(parts) >= 4 and parts[1] == 'cnf':
                    num_vars = int(parts[2])
                continue
            # clause lines: sequence of ints terminated by 0
            toks = list(map(int, line.split()))
            if toks[-1] != 0:
                raise ValueError(f"Clause line not terminated by 0: {line}")
            lits = toks[:-1]
            if len(lits) != 3:
                raise ValueError(f"Only 3-literal clauses supported. Found {len(lits)} in line: {line}")
            clauses.append((lits[0], lits[1], lits[2]))
    if num_vars is None:
        # fallback: compute max var index present
        maxv = 0
        for (a,b,c) in clauses:
            maxv = max(maxv, abs(a), abs(b), abs(c))
        num_vars = maxv
    return clauses, num_vars

def parse_simple_3cnf(path: str) -> Tuple[List[Tuple[int,int,int]], int]:
    """
    Parse a simple 3-literal-per-line format:
      each non-empty line contains 3 signed ints separated by whitespace
      comments start with '#'.
    """
    clauses = []
    maxv = 0
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Expected 3 ints per line, got: {line}")
            lits = tuple(int(x) for x in parts)
            clauses.append(lits)
            maxv = max(maxv, abs(lits[0]), abs(lits[1]), abs(lits[2]))
    return clauses, maxv

def read_3cnf(path: str):
    """
    Detect format heuristically: DIMACS if first non-empty non-comment line starts with 'p' or contains '0' at line ends.
    Otherwise try simple format.
    """
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith('c'):
                continue
            if line.startswith('p') or line.endswith(' 0') or line.endswith(' 0\n') or ' 0' in line:
                # assume DIMACS
                return parse_dimacs_3cnf(path)
            else:
                # assume simple
                return parse_simple_3cnf(path)
    raise ValueError("Empty or invalid input file")

def format_assignment(assign: List[bool]) -> str:
    # human-friendly: v1=1 v2=0 v3=1 ...
    return " ".join(f"v{i+1}={'1' if val else '0'}" for i, val in enumerate(assign))

def main():
    p = argparse.ArgumentParser(description="3SAT -> 2SAT transform + 2SAT solve + filtering pipeline")
    p.add_argument("--input", "-i", required=True, help="Path to 3-CNF input file (DIMACS or simple 3-ints-per-line)")
    p.add_argument("--out", "-o", default=None, help="Output file to write projected assignments (default: printed only)")
    p.add_argument("--max-models", type=int, default=1000, help="Maximum number of 2-SAT models to enumerate (to bound runtime)")
    p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = p.parse_args()

    path = args.input
    if not os.path.exists(path):
        print(f"Input file not found: {path}", file=sys.stderr)
        sys.exit(2)

    try:
        clauses, num_vars = read_3cnf(path)
    except Exception as e:
        print(f"Failed to parse input: {e}", file=sys.stderr)
        sys.exit(2)

    if args.verbose:
        print(f"Read {len(clauses)} clauses over {num_vars} original variables")

    # transform
    ts: TwoSAT
    try:
        ts, aux_map, exclude_conditions = transform_3sat_to_2sat(clauses, num_vars)
    except Exception as e:
        print(f"Transformation failed: {e}", file=sys.stderr)
        sys.exit(3)

    # quick check: if 2SAT unsat => original unsat
    sat, _ = ts.solve()
    if not sat:
        print("UNSAT (2-SAT relaxation is unsatisfiable => original 3-SAT unsatisfiable)")
        # write empty output if requested
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write("# UNSAT\n")
        sys.exit(0)

    # otherwise enumerate + filter (bounded by max_models)
    sat_flag, projected = solve_and_filter(ts, aux_map, exclude_conditions, num_vars, max_models=args.max_models)

    if not sat_flag:
        print("UNSAT (no surviving assignments after filtering)")
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write("# UNSAT after filtering\n")
        sys.exit(0)

    # Otherwise print results
    print(f"SAT (found {len(projected)} distinct assignment(s) for original {num_vars} variables)")
    for idx, ass in enumerate(projected, start=1):
        print(f"Model {idx}: {format_assignment(ass)}")

    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(f"# Projected assignments for original {num_vars} vars\n")
            for ass in projected:
                f.write(format_assignment(ass) + "\n")
        if args.verbose:
            print(f"Wrote results to {args.out}")

if __name__ == "__main__":
    main()

# Example usage: python3 src/main.py --input examples/example_3sat.cnf --max-models 1000 --out examples/example_output.txt --verbose
