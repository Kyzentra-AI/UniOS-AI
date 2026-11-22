"""
UniOS Canonical Curricula Bank
Authoritative academic syllabi structures based on UniOS Adaptive Learning Content Architecture.
"""

from typing import Any, Dict, List, Optional

DAA_CANONICAL_CURRICULUM: Dict[str, Any] = {
    "subject": "Design and Analysis of Algorithms",
    "subject_code": "DAA",
    "degree": "B.Tech Computer Science & Engineering",
    "chapters": [
        {
            "chapter_number": 1,
            "title": "Introduction to Algorithms",
            "outcome": "The student can define an algorithm, identify its properties, analyze time and space requirements, interpret asymptotic notation, and compare best-, average- and worst-case behaviour.",
            "topics": [
                {
                    "id": "1.1",
                    "title": "Introduction to Algorithms",
                    "objective": "Define an algorithm as a finite sequence of clear steps for solving a problem.",
                    "prerequisites": ["Basic Programming Flow", "Discrete Mathematics"],
                },
                {
                    "id": "1.2",
                    "title": "Characteristics of Algorithms",
                    "objective": "Cover input, output, definiteness, finiteness and effectiveness.",
                    "prerequisites": ["Definition of Algorithm"],
                },
                {
                    "id": "1.3",
                    "title": "Algorithm Design and Analysis",
                    "objective": "Explain problem specification, solution design, correctness and resource analysis.",
                    "prerequisites": ["Algorithm Characteristics"],
                },
                {
                    "id": "1.4",
                    "title": "Time Complexity",
                    "objective": "Explain growth in operation count as input size increases.",
                    "prerequisites": ["Loop Structures", "Algebraic Growth"],
                },
                {
                    "id": "1.5",
                    "title": "Space Complexity",
                    "objective": "Explain memory requirements and distinguish input storage from auxiliary space.",
                    "prerequisites": ["Call Stack Mechanics", "Memory Allocation"],
                },
                {
                    "id": "1.6",
                    "title": "Asymptotic Notations: Big-O, Big-Omega and Big-Theta",
                    "objective": "Introduce Big-O, Big-Omega and Big-Theta as upper, lower and tight asymptotic bounds.",
                    "prerequisites": ["Function Growth Rates", "Inequalities"],
                },
                {
                    "id": "1.7",
                    "title": "Best, Average and Worst-Case Analysis",
                    "objective": "Explain performance across different input arrangements using searching.",
                    "prerequisites": ["Asymptotic Bounds", "Linear Search"],
                },
            ],
        },
        {
            "chapter_number": 2,
            "title": "Divide and Conquer",
            "outcome": "Decompose complex computational problems recursively into independent subproblems, formulate recurrence relations, apply the Master Theorem, and implement sorting and selection routines.",
            "topics": [
                {"id": "2.1", "title": "Divide-and-Conquer Strategy", "objective": "Understand the three-step paradigm: Divide, Conquer, Combine."},
                {"id": "2.2", "title": "Recursion and Recurrence Relations", "objective": "Formulate mathematical recurrence relations for recursive algorithms."},
                {"id": "2.3", "title": "Recursion Tree and Substitution Methods", "objective": "Solve recurrence relations using visual expansion trees and inductive substitution proofs."},
                {"id": "2.4", "title": "Master Theorem", "objective": "Apply the Master Theorem cases to directly derive asymptotic complexity."},
                {"id": "2.5", "title": "Binary Search", "objective": "Analyze O(log N) divide-and-conquer search invariant on ordered datasets."},
                {"id": "2.6", "title": "Merge Sort", "objective": "Implement stable O(N log N) recursive sorting with linear merge passes."},
                {"id": "2.7", "title": "Quick Sort", "objective": "Implement in-place partitioning, pivot selection strategies, and worst/average case analysis."},
                {"id": "2.8", "title": "Maximum and Minimum", "objective": "Find simultaneous extrema with minimal pairwise comparisons via divide and conquer."},
            ],
        },
        {
            "chapter_number": 3,
            "title": "Greedy Algorithms",
            "outcome": "Identify greedy-choice properties and optimal substructure, formulate greedy strategies, and solve scheduling, coding, and graph optimization problems.",
            "topics": [
                {"id": "3.1", "title": "Greedy Method and Greedy-Choice Property", "objective": "Understand locally optimal choices leading to globally optimal solutions."},
                {"id": "3.2", "title": "Activity Selection", "objective": "Maximize non-overlapping interval scheduling sorted by finish times."},
                {"id": "3.3", "title": "Fractional Knapsack", "objective": "Optimize continuous resource allocation by value-to-weight ratio."},
                {"id": "3.4", "title": "Job Sequencing with Deadlines", "objective": "Schedule discrete tasks within deadlines to maximize cumulative profit."},
                {"id": "3.5", "title": "Huffman Coding", "objective": "Construct prefix-free optimal binary encoding trees for data compression."},
                {"id": "3.6", "title": "Minimum Spanning Trees", "objective": "Define spanning trees, cut properties, and cycle properties in weighted graphs."},
                {"id": "3.7", "title": "Prim's Algorithm", "objective": "Grow MST incrementally from a starting vertex using priority queues."},
                {"id": "3.8", "title": "Kruskal's Algorithm", "objective": "Construct MST by edge sorting and Disjoint Set Union (DSU) cycle detection."},
                {"id": "3.9", "title": "Dijkstra's Algorithm", "objective": "Compute single-source shortest paths on non-negative weighted graphs via edge relaxation."},
            ],
        },
        {
            "chapter_number": 4,
            "title": "Dynamic Programming",
            "outcome": "Differentiate dynamic programming from greedy and divide-and-conquer, verify optimal substructure and overlapping subproblems, and implement memoized and tabulated solutions.",
            "topics": [
                {"id": "4.1", "title": "Introduction to Dynamic Programming", "objective": "Understand the multi-stage decision process and contrast with divide-and-conquer."},
                {"id": "4.2", "title": "Optimal Substructure", "objective": "Prove that an optimal global solution contains optimal subproblem solutions."},
                {"id": "4.3", "title": "Overlapping Subproblems", "objective": "Identify repeated subcomputations in recursion trees."},
                {"id": "4.4", "title": "Memoization and Tabulation", "objective": "Master top-down caching with recursion versus bottom-up table formulation."},
                {"id": "4.5", "title": "Fibonacci Sequence", "objective": "Demonstrate the transition from O(2^N) naive recursion to O(N) linear dynamic programming."},
                {"id": "4.6", "title": "0/1 Knapsack", "objective": "Formulate 2D state-space DP table for discrete item selection under capacity constraints."},
                {"id": "4.7", "title": "Longest Common Subsequence (LCS)", "objective": "Compute string similarity alignments via optimal substructure table derivation."},
                {"id": "4.8", "title": "Matrix Chain Multiplication", "objective": "Minimize scalar multiplications by optimal parenthesization of matrix chains."},
                {"id": "4.9", "title": "Floyd–Warshall Algorithm", "objective": "Compute all-pairs shortest paths via dynamic intermediate vertex relaxation."},
            ],
        },
        {
            "chapter_number": 5,
            "title": "Backtracking",
            "outcome": "Explore combinatorial solution spaces systematically via state-space trees, depth-first search, and bounding functions.",
            "topics": [
                {"id": "5.1", "title": "Introduction to Backtracking", "objective": "Understand systematic trial-and-error state-space search with pruning."},
                {"id": "5.2", "title": "State-Space Trees", "objective": "Model problem states, live nodes, and dead-end pruning."},
                {"id": "5.3", "title": "N-Queens Problem", "objective": "Place N non-attacking queens on an N×N board using row/column/diagonal conflict checks."},
                {"id": "5.4", "title": "Sum of Subsets", "objective": "Find subsets of integers whose sum matches target value using bounding bounds."},
                {"id": "5.5", "title": "Graph Coloring", "objective": "Assign minimal colors to graph vertices such that no two adjacent vertices share a color."},
                {"id": "5.6", "title": "Hamiltonian Cycle", "objective": "Find closed cycles visiting every graph vertex exactly once using path backtracking."},
            ],
        },
        {
            "chapter_number": 6,
            "title": "Branch and Bound",
            "outcome": "Solve optimization problems over state spaces using lower/upper bounds, priority search frontiers, and pruning.",
            "topics": [
                {"id": "6.1", "title": "Introduction to Branch and Bound", "objective": "Understand branch-and-bound optimization for combinatorial maximization/minimization."},
                {"id": "6.2", "title": "State-Space Search and Bounding", "objective": "Compute heuristic bounds to prune subtrees that cannot yield better solutions."},
                {"id": "6.3", "title": "FIFO Branch and Bound", "objective": "Explore state-space trees using queue-based breadth-first generation."},
                {"id": "6.4", "title": "Least-Cost Branch and Bound (LCBB)", "objective": "Select next exploration node using priority queues ordered by estimated bound."},
                {"id": "6.5", "title": "Travelling Salesperson Problem (TSP)", "objective": "Solve asymmetric/symmetric TSP using cost matrix reduction and bounding."},
                {"id": "6.6", "title": "0/1 Knapsack using Branch and Bound", "objective": "Solve knapsack using fractional relaxation upper bounds and pruning."},
            ],
        },
        {
            "chapter_number": 7,
            "title": "Graph Algorithms and Complexity Theory",
            "outcome": "Traverse complex graphs, classify problems into P, NP, NP-Complete, and NP-Hard, and formulate polynomial-time reductions.",
            "topics": [
                {"id": "7.1", "title": "Graph Representations", "objective": "Compare adjacency matrix versus adjacency list trade-offs across dense and sparse graphs."},
                {"id": "7.2", "title": "Breadth-First Search (BFS)", "objective": "Perform level-order graph traversal and compute unweighted shortest paths in O(V + E)."},
                {"id": "7.3", "title": "Depth-First Search (DFS)", "objective": "Execute recursive graph traversal, discovery/finish timestamps, and cycle detection."},
                {"id": "7.4", "title": "Topological Sorting", "objective": "Linearize Directed Acyclic Graphs (DAGs) using DFS finish times or Kahn's in-degree queue."},
                {"id": "7.5", "title": "Shortest-Path Algorithms", "objective": "Compare Bellman-Ford (negative weights) and Dijkstra across graph topologies."},
                {"id": "7.6", "title": "P and NP Complexity Classes", "objective": "Define deterministic polynomial time (P) versus non-deterministic polynomial time verification (NP)."},
                {"id": "7.7", "title": "NP-Hard Problems", "objective": "Define problems at least as hard as the hardest problems in NP."},
                {"id": "7.8", "title": "NP-Complete Problems", "objective": "Understand Cook-Levin Theorem and formal membership in NP and NP-Hard."},
                {"id": "7.9", "title": "Introduction to Polynomial-Time Reductions", "objective": "Prove NP-Completeness via polynomial-time reductions (A <=p B)."},
            ],
        },
    ],
}


def get_canonical_curriculum(subject_query: str) -> Optional[Dict[str, Any]]:
    """Returns canonical curriculum if matched by query, else None."""
    query = (subject_query or "").strip().lower()
    if any(q in query for q in ["daa", "design and analysis of algorithm", "algorithm design", "algorithms"]):
        return DAA_CANONICAL_CURRICULUM
    return None
