"""
UniOS Domain Classifier Gate
Classifies academic subjects, degree programs, and topics into 5 core archetypes
to prevent Computer Science / Engineering leakage into business, commerce, and humanities curricula.
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class DomainArchetype(str, Enum):
    BUSINESS_MANAGEMENT = "BUSINESS_MANAGEMENT"
    ACCOUNTING_FINANCE_QUANT = "ACCOUNTING_FINANCE_QUANT"
    APPLIED_OFFICE_IT = "APPLIED_OFFICE_IT"
    CODING_CS = "CODING_CS"
    GENERAL_HUMANITIES_SCIENCE = "GENERAL_HUMANITIES_SCIENCE"


# Classification keyword mappings
_APPLIED_OFFICE_IT_KEYWORDS = [
    "computer applications in business",
    "computer application in business",
    "business applications of it",
    "information technology in business",
    "office automation",
    "business computing",
    "ms office",
    "microsoft excel",
    "spreadsheets",
    "spreadsheet",
    "word processing",
    "business presentation",
    "tally",
    "cyber security awareness",
    "cybersecurity for business",
    "office tools",
    "e-business tools",
]

_BUSINESS_MANAGEMENT_KEYWORDS = [
    "principles of management",
    "business management",
    "management principles",
    "business environment",
    "business communication",
    "human values",
    "organizational behavior",
    "organisational behaviour",
    "marketing management",
    "human resource",
    "strategic management",
    "entrepreneurship",
    "operations management",
    "international business",
    "business ethics",
    "corporate governance",
    "general management",
    "bba",
    "mba",
    "bms",
    "bbm",
    "pgdm",
    "retail management",
    "supply chain",
]

_ACCOUNTING_FINANCE_QUANT_KEYWORDS = [
    "financial accounting",
    "cost accounting",
    "management accounting",
    "corporate accounting",
    "business economics",
    "microeconomics",
    "macroeconomics",
    "managerial economics",
    "business mathematics",
    "business statistics",
    "quantitative techniques",
    "quantitative aptitude",
    "quantitative methods",
    "corporate finance",
    "financial management",
    "taxation",
    "income tax",
    "auditing",
    "banking",
    "insurance",
    "econometrics",
    "b.com",
    "bcom",
    "m.com",
    "mcom",
    "finance",
    "accounting",
    "ledger",
    "journal entry",
    "trial balance",
]

_CODING_CS_KEYWORDS = [
    "algorithm",
    "algorithms",
    "daa",
    "data structures",
    "complexity",
    "time complexity",
    "space complexity",
    "asymptotic",
    "big-o",
    "sorting",
    "merge sort",
    "quick sort",
    "bubble sort",
    "insertion sort",
    "worst case",
    "best case",
    "average case",
    "case analysis",
    "binary search",
    "linear search",
    "divide and conquer",
    "greedy",
    "dynamic programming",
    "memoization",
    "tabulation",
    "knapsack",
    "fractional knapsack",
    "0/1 knapsack",
    "backtracking",
    "branch and bound",
    "n-queens",
    "queens",
    "graph",
    "graphs",
    "graph algorithm",
    "graph traversal",
    "breadth-first search",
    "depth-first search",
    "bfs",
    "dfs",
    "shortest path",
    "dijkstra",
    "prim",
    "kruskal",
    "huffman",
    "activity selection",
    "recurrence",
    "master theorem",
    "programming",
    "python",
    "java",
    "c++",
    "c programming",
    "web development",
    "backend",
    "frontend",
    "database management",
    "dbms",
    "sql",
    "operating systems",
    "computer networks",
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "neural networks",
    "artificial neural networks",
    "ann",
    "perceptron",
    "feedforward",
    "backpropagation",
    "activation function",
    "pytorch",
    "tensorflow",
    "cnn",
    "rnn",
    "transformer",
    "llm",
    "cloud computing",
    "compiler design",
    "theory of computation",
    "automata",
    "software engineering",
    "oop",
    "object-oriented",
    "b.tech",
    "btech",
    "m.tech",
    "mtech",
    "bca",
    "mca",
    "computer science",
    "cse",
    "information technology",
]

_HUMANITIES_SCIENCE_KEYWORDS = [
    # Environmental & Earth Sciences
    "environmental studies",
    "environmental science",
    "climate change",
    "earth science",
    "geology",
    "astronomy",
    # Humanities, Social Sciences & Law
    "history",
    "political science",
    "sociology",
    "psychology",
    "philosophy",
    "english",
    "literature",
    "linguistics",
    "anthropology",
    "geography",
    "journalism",
    "mass communication",
    "public administration",
    "law",
    "legal",
    "constitution",
    "jurisprudence",
    "llb",
    "llm",
    "ba",
    "ma",
    # Physical Sciences
    "physics",
    "kinematics",
    "mechanics",
    "thermodynamics",
    "electromagnetism",
    "optics",
    "quantum mechanics",
    "chemistry",
    "organic chemistry",
    "inorganic chemistry",
    "physical chemistry",
    # Life Sciences, Zoology & Botany
    "zoology",
    "zoological",
    "foundations of life",
    "animal diversity",
    "plant diversity",
    "botany",
    "botanical",
    "life science",
    "life sciences",
    "cell biology",
    "molecular biology",
    "ecology",
    "evolution",
    "genetics",
    "invertebrate",
    "invertebrates",
    "vertebrate",
    "vertebrates",
    "chordate",
    "chordates",
    "non-chordate",
    "non-chordates",
    "developmental biology",
    "entomology",
    "taxonomy",
    "morphology",
    "histology",
    "embryology",
    "parasitology",
    "diversity and classification",
    "animal",
    "plant",
    "biology",
    "biotechnology",
    "b.sc",
    "bsc",
    "m.sc",
    "msc",
    # Medical, Healthcare & Pharmacy
    "medical",
    "medicine",
    "mbbs",
    "bds",
    "bams",
    "bhms",
    "nursing",
    "pharmacy",
    "b.pharm",
    "bpharm",
    "m.pharm",
    "mpharm",
    "pharmacology",
    "pharmacognosy",
    "pharmaceutics",
    "pathology",
    "human anatomy",
    "anatomy",
    "human physiology",
    "physiology",
    "microbiology",
    "biochemistry",
    "clinical",
    "clinical medicine",
    "health",
    "healthcare",
    "health sciences",
    "pediatrics",
    "surgery",
    "obstetrics",
    "gynecology",
    "forensic medicine",
    "dermatology",
    "radiology",
    "cardiology",
    "neurology",
    "epidemiology",
    "public health",
    "immunology",
    "virology",
    "hematology",
    "oncology",
    "physiotherapy",
    "bpt",
    "dental",
]


def classify_domain(
    subject: Optional[str] = None,
    degree_program: Optional[str] = None,
    topic: Optional[str] = None,
    academic_domain: Optional[str] = None,
) -> DomainArchetype:
    """
    Classifies a subject, degree program, and topic into one of the 5 domain archetypes.
    Evaluates Applied Office IT first to prevent Computer Science leakage into business courses.
    """
    text_corpus = " ".join(
        [
            str(subject or ""),
            str(degree_program or ""),
            str(topic or ""),
            str(academic_domain or ""),
        ]
    ).strip().lower()

    if not text_corpus:
        return DomainArchetype.CODING_CS

    # 1. Gate: Check Applied Office IT first
    # This ensures courses like "Computer Applications in Business" or "Office Automation"
    # do NOT get falsely routed to CODING_CS.
    for kw in _APPLIED_OFFICE_IT_KEYWORDS:
        if kw in text_corpus:
            return DomainArchetype.APPLIED_OFFICE_IT

    # 2. Gate: Check Accounting, Finance & Quantitative Methods
    for kw in _ACCOUNTING_FINANCE_QUANT_KEYWORDS:
        if kw in text_corpus:
            return DomainArchetype.ACCOUNTING_FINANCE_QUANT

    # 3. Gate: Check Business & Management
    for kw in _BUSINESS_MANAGEMENT_KEYWORDS:
        if kw in text_corpus:
            return DomainArchetype.BUSINESS_MANAGEMENT

    # 4. Gate: Check Coding & Computer Science
    for kw in _CODING_CS_KEYWORDS:
        if kw in text_corpus:
            return DomainArchetype.CODING_CS

    # 5. Gate: Check Humanities, Law, and Sciences
    for kw in _HUMANITIES_SCIENCE_KEYWORDS:
        if kw in text_corpus:
            return DomainArchetype.GENERAL_HUMANITIES_SCIENCE

    # Degree program fallback
    deg_lower = (degree_program or "").lower()
    if any(d in deg_lower for d in ["bba", "mba", "management"]):
        return DomainArchetype.BUSINESS_MANAGEMENT
    if any(d in deg_lower for d in ["b.com", "bcom", "m.com", "mcom", "finance", "accounting"]):
        return DomainArchetype.ACCOUNTING_FINANCE_QUANT
    if any(d in deg_lower for d in ["b.tech", "btech", "bca", "mca", "computer", "cse", "it"]):
        return DomainArchetype.CODING_CS
    if any(d in deg_lower for d in [
        "ba", "ma", "law", "llb", "llm", "bsc", "msc", "b.sc", "m.sc",
        "mbbs", "bds", "bams", "bhms", "nursing", "pharmacy", "b.pharm", "m.pharm", "bpt",
        "medical", "medicine", "zoology", "botany", "biology", "life science"
    ]):
        return DomainArchetype.GENERAL_HUMANITIES_SCIENCE

    # Contextual life / health / science safety check before generic fallback
    if any(w in text_corpus for w in [
        "life", "health", "patient", "clinical", "organism", "cell", "living",
        "animal", "plant", "species", "specimen", "organ", "disease", "diagnosis"
    ]):
        return DomainArchetype.GENERAL_HUMANITIES_SCIENCE

    # Default general archetype
    return DomainArchetype.BUSINESS_MANAGEMENT
