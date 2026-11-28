"""
UniOS DAA Pedagogical Content Bank
Implements the UniOS Adaptive Learning Content Architecture for Design and Analysis of Algorithms (DAA).
Provides simplified, resourceful, analogy-grounded 5-section lessons for all DAA chapters.
"""

from typing import Optional, List, Dict, Any
from app.schemas.lesson import (
    GeneratedLesson,
    LessonBlock,
    LessonBlockType,
    AssessmentIntent,
    NextLearningAction,
)
from app.schemas.pedagogy import (
    PedagogyDecision,
    TeachingStrategy,
    DifficultyLevel,
    PresentationMode,
    PracticeLevel,
)


def _make_pedagogy(adaptive_strategy: str = "foundational_support", difficulty: DifficultyLevel = DifficultyLevel.BEGINNER) -> PedagogyDecision:
    return PedagogyDecision(
        strategy=TeachingStrategy.FOUNDATIONAL,
        adaptive_strategy=adaptive_strategy,
        difficulty=difficulty,
        presentation_mode=PresentationMode.TRADITIONAL,
        explanation_depth="step-by-step",
        rationale=f"Calibrated with {adaptive_strategy}: plain-language steps with familiar analogies and step-by-step traces.",
        practice_level=PracticeLevel.GUIDED,
        remediation=False,
    )


def build_topic_1_1_intro_to_algorithms(topic: str, context_id: str) -> GeneratedLesson:
    """Topic 1.1 / 1.2 / 1.3: Introduction to Algorithms & Characteristics."""
    obj_content = (
        "## 🎯 Learning Outcomes & Context\n"
        "- Define an algorithm as a finite sequence of clear, unambiguous steps for solving a computational problem.\n"
        "- Understand the 5 essential characteristics of every algorithm: Input, Output, Definiteness, Finiteness, and Effectiveness.\n"
        "- Learn how to plan and trace algorithms using pseudocode and flowcharts before writing code.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Basic familiarity with variables, arithmetic operations, and simple decision structures (`if/else`).\n\n"
        "### 💡 Why This Topic Matters\n"
        "Every software system—from Google Maps finding the shortest route to Instagram recommending posts—runs on algorithms. Understanding how to design and trace step-by-step solutions is the single most important skill in computer science."
    )

    expl_content = (
        "## ☕ An Everyday Analogy: Making a Cup of Tea\n"
        "An algorithm may sound like intimidating mathematics, but you execute algorithms every single day.\n\n"
        "Think about following a recipe to brew a cup of tea:\n"
        "1. **Input**: Water, tea leaves, milk, and sugar.\n"
        "2. **Step 1**: Boil 200ml of water in a pan.\n"
        "3. **Step 2**: Add 1 teaspoon of tea leaves and simmer for 2 minutes.\n"
        "4. **Step 3**: Pour in 50ml of milk and 1 teaspoon of sugar.\n"
        "5. **Step 4**: Strain into a mug.\n"
        "6. **Output**: A hot cup of tea!\n\n"
        "If you skip a step, invert the order, or write an instruction like *'add some tea leaves'* without specifying how much, the result fails. A computer is like a kitchen helper who follows instructions strictly to the letter.\n\n"
        "> [!NOTE]\n"
        "> **Definition of an Algorithm**: A finite, step-by-step sequence of unambiguous instructions designed to transform specific inputs into a correct output.\n\n"
        "### The 5 Essential Properties of an Algorithm\n\n"
        "| Property | Meaning | Everyday Example | Flawed Counterexample |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **1. Input** | Takes 0 or more clearly specified inputs. | Ingredients supplied to a recipe. | An algorithm requiring mysterious data not provided. |\n"
        "| **2. Output** | Produces at least 1 well-defined result. | The prepared dish or computed sum. | A program that finishes running but displays nothing. |\n"
        "| **3. Definiteness** | Every instruction must be completely unambiguous. | 'Add 5 grams of sugar' (precise). | 'Add a pinch of sugar' (too vague for a computer). |\n"
        "| **4. Finiteness** | Must stop after a finite number of steps. | Recipe finishes in 4 steps. | Shampoo bottle: 'Lather, rinse, repeat' (infinite loop!). |\n"
        "| **5. Effectiveness** | Every operation must be feasible and basic. | Basic addition, comparison, assignment. | 'Divide by zero' or 'Predict tomorrow\\'s lottery numbers'. |"
    )

    code_snippet = (
        "# Algorithm: Calculate Total Bill with Tax and Discount\n"
        "def calculate_final_bill(subtotal: float, discount_percent: float, tax_percent: float) -> float:\n"
        "    # Step 1: Validate input values (Precondition check)\n"
        "    if subtotal < 0 or discount_percent < 0 or tax_percent < 0:\n"
        "        raise ValueError('Prices and percentages cannot be negative')\n"
        "    \n"
        "    # Step 2: Compute discount amount\n"
        "    discount_amount = subtotal * (discount_percent / 100.0)\n"
        "    discounted_subtotal = subtotal - discount_amount\n"
        "    \n"
        "    # Step 3: Compute tax on the discounted amount\n"
        "    tax_amount = discounted_subtotal * (tax_percent / 100.0)\n"
        "    \n"
        "    # Step 4: Calculate final payable bill\n"
        "    final_bill = discounted_subtotal + tax_amount\n"
        "    return round(final_bill, 2)\n\n"
        "# Verified test cases\n"
        "assert calculate_final_bill(100.0, 10.0, 5.0) == 94.5\n"
        "assert calculate_final_bill(50.0, 0.0, 8.0) == 54.0"
    )

    code_content = (
        "## 🛠️ Step-by-Step Code Walkthrough\n"
        "Let's trace through a practical program that computes a customer bill. Notice how each line corresponds to an ordered, unambiguous step:\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 Variable State Trace Table\n\n"
        "| Step | Operation | Variables State | Notes |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| Start | Input received | `subtotal = 100.0`, `discount = 10%`, `tax = 5%` | Initial input state |\n"
        "| 1 | Validation check | All values $\\ge 0$ | Passes precondition check |\n"
        "| 2 | Discount applied | `discount_amount = 10.0`, `discounted_subtotal = 90.0` | Subtotal reduced by 10% |\n"
        "| 3 | Tax calculated | `tax_amount = 4.50` | 5% tax calculated on 90.0 |\n"
        "| 4 | Output returned | `final_bill = 94.50` | Unambiguous final result |"
    )

    vis_content = (
        "## 📊 Visual Flowchart: Input to Output\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    A["Start: Receive Input Data"] --> B{"Is Input Valid?"}\n'
        '    B -- "No" --> C["Raise Error & Halt (Definiteness)"]\n'
        '    B -- "Yes" --> D["Step 1: Compute Discount"]\n'
        '    D --> E["Step 2: Compute Tax on Balance"]\n'
        '    E --> F["Step 3: Add Tax to Subtotal"]\n'
        '    F --> G["Output: Return Final Total (Finiteness)"]\n'
        '    G --> H["End"]\n'
        "```\n\n"
        "### 🔄 Key Phases in Algorithm Design\n"
        "1. **Problem Definition**: What are the inputs, outputs, and constraints?\n"
        "2. **Algorithm Design**: Writing pseudocode or drawing a flowchart.\n"
        "3. **Correctness Check**: Verifying that the logic works for normal, boundary, and zero inputs.\n"
        "4. **Complexity Analysis**: Checking how fast it runs as data grows."
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: Write out the 4 ordered steps (or pseudocode) for an algorithm that takes a student's exam score (between 0 and 100) and prints `'Pass'` if the score is 40 or higher, otherwise prints `'Fail'`. If the score is outside 0 to 100, print `'Invalid Score'`.\n\n"
        "> [!TIP]\n"
        "> **Hint**: Check the invalid boundary first (`score < 0 or score > 100`), then check `score >= 40`.\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Algorithm vs. Program**: An algorithm is an abstract, language-independent mathematical design; a program is an implementation of an algorithm in a specific programming language (like Python or C++).\n"
        "2. **The 5 Properties**: Memorize the acronym **F-D-I-O-E** (Finiteness, Definiteness, Input, Output, Effectiveness).\n"
        "3. **Common Exam Mistake**: Don't confuse an infinite loop with an algorithm. A procedure that never terminates is NOT an algorithm."
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Intuitive Concept: What is an Algorithm?", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Step-by-Step Worked Example: Tracing an Algorithm", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Flowchart: Visual Flow of an Algorithm", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("foundational_support"),
        blocks=blocks,
        prerequisites=["Basic Programming Flow"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="beginner", question_count=3, evaluation_criteria=["Comprehension"]),
        next_action=NextLearningAction(action_type="practice", target_topic="Time Complexity", rationale="Advance to time complexity analysis.", urgency="normal"),
    )


def build_topic_1_4_time_complexity(topic: str, context_id: str) -> GeneratedLesson:
    """Topic 1.4: Time Complexity & Growth of Functions."""
    obj_content = (
        "## 🎯 Learning Outcomes & Context\n"
        "- Understand that time complexity measures the rate of growth of operations as input size $n$ increases, not clock time in seconds.\n"
        "- Learn how to count the dominant operations inside single, nested, and halving loops.\n"
        "- Recognize common complexity orders ($O(1), O(\\log n), O(n), O(n^2)$) and their practical implications.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Basic understanding of for-loops, while-loops, and basic algebraic exponents.\n\n"
        "### 💡 Why This Topic Matters\n"
        "A supercomputer running an inefficient $O(n^2)$ algorithm can be easily outperformed by an ordinary smartphone running an efficient $O(n)$ or $O(\\log n)$ algorithm on large datasets."
    )

    expl_content = (
        "## 📖 An Everyday Analogy: Searching Contacts in a Phonebook\n"
        "Imagine you have a phonebook containing $n$ contacts:\n"
        "1. **$O(1)$ (Constant Time)**: Checking the very first name on page 1. Whether the book has 10 contacts or 10,000,000 contacts, looking at the first name always takes exactly 1 second.\n"
        "2. **$O(\\log n)$ (Logarithmic Time)**: Looking up 'Sharma' using binary search. You open to the middle, see 'Patel', and discard half the book. You repeat this halving. For 1,000,000 names, you need only about 20 page turns!\n"
        "3. **$O(n)$ (Linear Time)**: Reading through the entire phonebook page by page to count how many people live on MG Road. If the book doubles in size, the time doubles.\n"
        "4. **$O(n^2)$ (Quadratic Time)**: Comparing every contact's phone number with every other contact to find duplicates. If $n = 1,000$, you perform $1,000,000$ comparisons!\n\n"
        "> [!NOTE]\n"
        "> **Why Don't We Measure Seconds?**: Seconds depend on CPU speed, RAM, operating system background tasks, and programming language overhead. Time complexity counts **fundamental operations** as a function of input size $n$.\n\n"
        "### Common Growth Rates Comparison Table\n\n"
        "| Complexity | Name | Operations ($n = 10$) | Operations ($n = 1,000$) | Practical Performance |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "| $O(1)$ | Constant | 1 | 1 | Instantaneous |\n"
        "| $O(\\log n)$ | Logarithmic | ~3.3 | ~10 | Blazing fast (Binary Search) |\n"
        "| $O(n)$ | Linear | 10 | 1,000 | Excellent (Single loop) |\n"
        "| $O(n \\log n)$ | Linearithmic | ~33 | ~10,000 | Optimal for comparison sorts |\n"
        "| $O(n^2)$ | Quadratic | 100 | 1,000,000 | Sluggish on large datasets |\n"
        "| $O(2^n)$ | Exponential | 1,024 | $10^{301}$ (Unsolvable) | Impractical for $n > 30$ |"
    )

    code_snippet = (
        "# Comparing 3 loop patterns and their operation counts\n"
        "def demonstrate_complexities(n: int):\n"
        "    # 1. Constant time O(1): always 1 step\n"
        "    first_item_step = 1\n"
        "    \n"
        "    # 2. Linear time O(n): loop runs exactly n times\n"
        "    linear_count = 0\n"
        "    for i in range(n):\n"
        "        linear_count += 1\n"
        "    \n"
        "    # 3. Logarithmic time O(log n): variable doubles each step\n"
        "    log_count = 0\n"
        "    k = 1\n"
        "    while k <= n:\n"
        "        log_count += 1\n"
        "        k = k * 2\n"
        "    \n"
        "    return linear_count, log_count\n\n"
        "# Trace verification for n = 16:\n"
        "lin, log = demonstrate_complexities(16)\n"
        "assert lin == 16      # O(n): exactly 16 steps\n"
        "assert log == 5       # O(log2 n): k = 1, 2, 4, 8, 16 -> 5 steps"
    )

    code_content = (
        "## 🛠️ Step-by-Step Code Walkthrough\n"
        "Let's trace how operation counts behave in Python code when $n = 16$:\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 Logarithmic Loop Trace Table ($n = 16$)\n\n"
        "| Iteration | Value of `k` at Start | Condition `k <= 16` | Next `k` (`k * 2`) | Total Steps |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "| 1 | 1 | True | 2 | 1 |\n"
        "| 2 | 2 | True | 4 | 2 |\n"
        "| 3 | 4 | True | 8 | 3 |\n"
        "| 4 | 8 | True | 16 | 4 |\n"
        "| 5 | 16 | True | 32 | 5 |\n"
        "| 6 | 32 | False (Halt) | — | **5 total steps** |"
    )

    vis_content = (
        "## 📊 Visual Hierarchy: Relative Growth Rates\n\n"
        "```mermaid\n"
        "flowchart LR\n"
        '    O1["O(1) Constant"] --> OLog["O(log n) Logarithmic"]\n'
        '    OLog --> ON["O(n) Linear"]\n'
        '    ON --> ONLog["O(n log n) Linearithmic"]\n'
        '    ONLog --> ON2["O(n^2) Quadratic"]\n'
        '    ON2 --> O2N["O(2^n) Exponential"]\n'
        "```\n\n"
        "### 🔄 Dominant Term Rule (Drop the Small Stuff)\n"
        "When analyzing polynomials like $T(n) = 3n^2 + 50n + 1000$:\n"
        "1. As $n \\to \\infty$, the $n^2$ term completely dwarfs $50n$ and $1000$.\n"
        "2. We drop lower-order terms: $3n^2$.\n"
        "3. We drop multiplicative constants: $O(n^2)$."
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: What is the time complexity of the following code snippet? Count how many times `total += 1` executes in terms of $n$.\n\n"
        "```python\n"
        "total = 0\n"
        "for i in range(n):\n"
        "    for j in range(5):\n"
        "        total += 1\n"
        "```\n\n"
        "> [!TIP]\n"
        "> **Hint**: The outer loop runs $n$ times. The inner loop runs a fixed 5 times (constant). Total operations = $5n = O(n)$, NOT $O(n^2)$!\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Drop Constants & Low-Order Terms**: $7n^3 + 100n^2 + 4 = O(n^3)$. Never write $O(3n)$ or $O(n + 5)$.\n"
        "2. **Loop Doubling vs Halving**: If the loop counter multiplies (`i *= 2`) or divides (`i //= 2`), the complexity is almost always $O(\\log n)$.\n"
        "3. **Nested Loops Trap**: Two nested loops are only $O(n^2)$ if both loop bounds depend on $n$."
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Intuitive Concept: How Fast Does an Algorithm Grow?", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example: Tracing Loop Execution & Operation Counts", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Framework: Algorithmic Growth Comparison", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("logical_analytical"),
        blocks=blocks,
        prerequisites=["Loop Structures", "Algebraic Growth"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="beginner", question_count=3, evaluation_criteria=["Complexity Analysis"]),
        next_action=NextLearningAction(action_type="practice", target_topic="Space Complexity", rationale="Study memory requirements alongside time.", urgency="normal"),
    )


def build_topic_1_5_space_complexity(topic: str, context_id: str) -> GeneratedLesson:
    """Topic 1.5: Space Complexity & Auxiliary Memory."""
    obj_content = (
        "## 🎯 Learning Outcomes & Context\n"
        "- Distinguish between total space complexity and auxiliary space (extra memory used beyond inputs).\n"
        "- Understand how recursive calls consume stack memory through call stack frames.\n"
        "- Compare in-place algorithms ($O(1)$ auxiliary space) with algorithms that allocate new data structures ($O(n)$ space).\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Understanding of memory variables, lists/arrays, and basic recursive function calls.\n\n"
        "### 💡 Why This Topic Matters\n"
        "In embedded devices, automotive controllers, and high-frequency cloud microservices, memory is strictly bounded. An algorithm that uses $O(n)$ extra memory can trigger an Out-Of-Memory (OOM) crash where an $O(1)$ in-place algorithm succeeds effortlessly."
    )

    expl_content = (
        "## 🏢 An Everyday Analogy: Desk Workspace & Scratch Paper\n"
        "Imagine you are solving a math assignment at a desk:\n"
        "1. **Input Space**: The textbook on your desk containing the assignment questions. You cannot change this—it already exists.\n"
        "2. **Fixed Space**: Your pencil and eraser. Whether the assignment has 1 question or 50 questions, you always need exactly 1 pencil and 1 eraser ($O(1)$ space).\n"
        "3. **Auxiliary Space**: Extra sheets of blank scratch paper you pull out to do scratch work. If you use 1 sheet of paper per question, solving 100 questions uses 100 sheets ($O(n)$ auxiliary space)!\n"
        "4. **Call Stack Space**: In recursion, every time a function calls itself, it puts a new sheet of paper on top of a stack. It cannot throw away the old sheet until the top sheet finishes!\n\n"
        "> [!NOTE]\n"
        "> **Formula**: $\\text{Total Space} = \\text{Input Space} + \\text{Auxiliary Space}$. In algorithm analysis, we are almost always interested in **Auxiliary Space**—the extra memory the algorithm requires.\n\n"
        "### Memory Components Breakdown Table\n\n"
        "| Component | Description | Example | Complexity |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **Fixed Memory** | Constants, simple scalars, loop counters | `i = 0`, `n = len(arr)` | $O(1)$ |\n"
        "| **Dynamic Data Memory** | Newly allocated arrays, hash tables, lists | `copy = arr.copy()` | $O(n)$ |\n"
        "| **Call Stack Memory** | Active function frames waiting for return | `fib(n) -> fib(n-1) -> ...` | $O(n)$ stack depth |"
    )

    code_snippet = (
        "# Comparing In-Place O(1) Reversal vs O(n) Recursive Reversal\n"
        "\n"
        "# Approach 1: In-place two-pointer reversal -> O(1) Auxiliary Space\n"
        "def reverse_in_place(arr: list) -> list:\n"
        "    left = 0\n"
        "    right = len(arr) - 1\n"
        "    while left < right:\n"
        "        # Swap in-place without allocating a new list\n"
        "        arr[left], arr[right] = arr[right], arr[left]\n"
        "        left += 1\n"
        "        right -= 1\n"
        "    return arr\n\n"
        "# Approach 2: Recursive reversal -> O(n) Call Stack Space\n"
        "def reverse_recursive(s: str) -> str:\n"
        "    if len(s) <= 1:\n"
        "        return s\n"
        "    # Each call adds a new frame to the call stack\n"
        "    return s[-1] + reverse_recursive(s[:-1])\n\n"
        "# Assertions\n"
        "assert reverse_in_place([1, 2, 3, 4]) == [4, 3, 2, 1]\n"
        "assert reverse_recursive('cat') == 'tac'"
    )

    code_content = (
        "## 🛠️ Step-by-Step Code Walkthrough\n"
        "Let's trace how the two reversal methods handle memory:\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 Memory State Trace Table (Reversing 4 elements `[10, 20, 30, 40]`)\n\n"
        "| Step | Approach 1 (Two Pointers) | Approach 2 (Recursive) | Memory State |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| Start | `left=0`, `right=3` | `reverse('10,20,30,40')` | Stack Frame 1 |\n"
        "| 1 | Swap `arr[0]` and `arr[3]` | Calls `reverse('10,20,30')` | Stack Frame 2 created |\n"
        "| 2 | `left=1`, `right=2` -> Swap `arr[1]`, `arr[2]` | Calls `reverse('10,20')` | Stack Frame 3 created |\n"
        "| 3 | `left=2`, `right=1` -> Loop terminates | Calls `reverse('10')` | Stack Frame 4 (Base case) |\n"
        "| End | **0 extra memory allocated: $O(1)$** | **4 active stack frames: $O(n)$** | Frames unwind sequentially |"
    )

    vis_content = (
        "## 📊 Visual Framework: Call Stack Growth in Recursion\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    subgraph Call_Stack_Memory ["Call Stack (Grows Downward with O(n) Frames)"]\n'
        '        F1["Frame 1: reverse(\'cat\') - waiting for \'at\'"]\n'
        '        F2["Frame 2: reverse(\'ca\') - waiting for \'c\'"]\n'
        '        F3["Frame 3: reverse(\'c\') - Base Case returns \'c\'"]\n'
        '        F1 --> F2 --> F3\n'
        '    end\n'
        "```\n\n"
        "### 🔄 In-Place vs Out-of-Place\n"
        "- **In-Place**: The algorithm modifies the input data directly using $O(1)$ extra space.\n"
        "- **Out-of-Place**: The algorithm creates copies or new structures, using $O(n)$ auxiliary space."
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: Determine the auxiliary space complexity of finding the maximum element in a list of $n$ numbers using:\n"
        "1. A simple for-loop with a `max_val` tracking variable.\n"
        "2. Sorting the list by creating a `sorted_copy = sorted(arr)` and returning `sorted_copy[-1]`.\n\n"
        "> [!TIP]\n"
        "> **Hint**: Method 1 only needs 1 scalar variable ($O(1)$ auxiliary space). Method 2 creates a new duplicate array ($O(n)$ auxiliary space).\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Input Space vs Auxiliary Space**: An algorithm receiving a list of $n$ items does NOT automatically have $O(n)$ space complexity. If it uses no extra memory, its auxiliary space is $O(1)$.\n"
        "2. **Recursive Stack Depth**: If recursion recurses $n$ levels deep, it consumes $O(n)$ stack space, even if no variables are created inside the function!\n"
        "3. **Tail Recursion**: Some compilers can optimize tail-recursive functions to use $O(1)$ stack frames, but standard Python does not."
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Intuitive Concept: Auxiliary Space & Call Stacks", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example: Comparing In-Place vs Recursive Memory", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Framework: Call Stack Allocation", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("practical_applied"),
        blocks=blocks,
        prerequisites=["Call Stack Mechanics", "Memory Allocation"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="beginner", question_count=3, evaluation_criteria=["Memory Analysis"]),
        next_action=NextLearningAction(action_type="practice", target_topic="Asymptotic Notations", rationale="Formalize growth bounds with Big-O.", urgency="normal"),
    )


def build_topic_1_6_asymptotic_notations(topic: str, context_id: str) -> GeneratedLesson:
    """Topic 1.6: Asymptotic Notations: Big-O, Big-Omega, Big-Theta."""
    obj_content = (
        "## 🎯 Learning Outcomes & Context\n"
        "- Formulate formal mathematical definitions for Big-O ($O$), Big-Omega ($\\Omega$), and Big-Theta ($\\Theta$).\n"
        "- Understand the difference between an upper bound (ceiling), a lower bound (floor), and a tight bound (bracket).\n"
        "- Learn how to formally prove that $f(n) = O(g(n))$ by finding positive constants $c$ and $n_0$.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Basic algebra, inequalities, and functions.\n\n"
        "### 💡 Why This Topic Matters\n"
        "Asymptotic notations provide a universal mathematical language for software engineers and researchers to communicate performance guarantees without arguing about specific hardware benchmarks."
    )

    expl_content = (
        "## ⏱️ An Everyday Analogy: Flight Travel Times\n"
        "Suppose you ask an airline how long a flight from Delhi to Mumbai takes:\n"
        "1. **Big-O (Upper Bound / Ceiling)**: 'It will take **at most 3 hours**, even with runway delays.' Big-O provides a guarantee that the running time will not exceed this ceiling ($f(n) \\le c \\cdot g(n)$).\n"
        "2. **Big-Omega (Lower Bound / Floor)**: 'The flight takes **at least 1.5 hours**, because an airplane cannot fly faster than the speed of sound.' Big-Omega defines the minimum floor ($f(n) \\ge c \\cdot g(n)$).\n"
        "3. **Big-Theta (Tight Bound / Bracket)**: 'The flight consistently takes **between 1.8 and 2.2 hours**.' When the upper bound and lower bound match, we have a tight asymptotic bound ($c_1 \\cdot g(n) \\le f(n) \\le c_2 \\cdot g(n)$).\n\n"
        "> [!NOTE]\n"
        "> **Mathematical Definition of Big-O**:\n"
        "> $f(n) = O(g(n))$ if and only if there exist positive constants $c > 0$ and $n_0 \\ge 1$ such that:\n"
        "> $$0 \\le f(n) \\le c \\cdot g(n) \\quad \\text{for all } n \\ge n_0$$\n\n"
        "### The 3 Asymptotic Notations Compared\n\n"
        "| Notation | Common Name | Boundary Type | Mathematical Condition (for $n \\ge n_0$) | Meaning |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "| **$O(g(n))$** | Big-O | Upper Bound (Ceiling) | $f(n) \\le c \\cdot g(n)$ | Growth rate is at most $g(n)$ |\n"
        "| **$\\Omega(g(n))$** | Big-Omega | Lower Bound (Floor) | $f(n) \\ge c \\cdot g(n)$ | Growth rate is at least $g(n)$ |\n"
        "| **$\\Theta(g(n))$** | Big-Theta | Tight Bound (Bracket) | $c_1 g(n) \\le f(n) \\le c_2 g(n)$ | Growth rate is sandwiched tightly |"
    )

    code_snippet = (
        "# Formal Verification: Proving 3n + 7 = O(n)\n"
        "# We need to find constants c > 0 and n0 >= 1 such that 3n + 7 <= c * n for all n >= n0.\n"
        "# Choose c = 4. Then 3n + 7 <= 4n  =>  7 <= n  =>  n0 = 7.\n"
        "\n"
        "def verify_big_o_bound(n_values: list) -> bool:\n"
        "    c = 4\n"
        "    n0 = 7\n"
        "    for n in n_values:\n"
        "        if n >= n0:\n"
        "            f_n = 3 * n + 7\n"
        "            bound = c * n\n"
        "            assert f_n <= bound, f'Failed at n={n}: {f_n} > {bound}'\n"
        "    return True\n\n"
        "# Test across a range of n values from 1 to 100\n"
        "test_n = list(range(1, 101))\n"
        "assert verify_big_o_bound(test_n) is True"
    )

    code_content = (
        "## 🛠️ Step-by-Step Worked Mathematical Proof\n"
        "**Problem**: Prove formally that $f(n) = 3n + 7$ is $O(n)$.\n\n"
        "**Step 1: Write down the formal inequality**\n"
        "$$3n + 7 \\le c \\cdot n$$\n\n"
        "**Step 2: Choose a candidate constant $c$**\n"
        "Choose $c = 4$ (any constant greater than the coefficient 3 works).\n\n"
        "**Step 3: Solve for $n_0$**\n"
        "$$3n + 7 \\le 4n \\implies 7 \\le 4n - 3n \\implies n \\ge 7$$\n\n"
        "**Conclusion**: With $c = 4$ and $n_0 = 7$, the condition $3n + 7 \\le 4n$ holds for all $n \\ge 7$. Hence, $3n + 7 = O(n)$! $\\blacksquare$\n\n"
        "### 🔍 Verification Trace Table\n\n"
        "| $n$ | $f(n) = 3n + 7$ | Upper Bound $c \\cdot n = 4n$ | Is $f(n) \\le 4n$? | Notes |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "| 1 | 10 | 4 | No ($10 > 4$) | Before threshold $n_0 = 7$ |\n"
        "| 5 | 22 | 20 | No ($22 > 20$) | Before threshold $n_0 = 7$ |\n"
        "| **7** | **28** | **28** | **Yes ($28 \\le 28$)** | **Threshold $n_0 = 7$ reached!** |\n"
        "| 10 | 37 | 40 | Yes ($37 \\le 40$) | Valid forever after |\n"
        "| 100 | 307 | 400 | Yes ($307 \\le 400$) | Valid forever after |"
    )

    vis_content = (
        "## 📊 Visual Framework: Asymptotic Bounds\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    Upper["Upper Bound: c * g(n) [Big-O Ceiling]"]\n'
        '    Actual["f(n) Actual Execution Curve"]\n'
        '    Lower["Lower Bound: c1 * g(n) [Big-Omega Floor]"]\n'
        '    Upper -.-> Actual\n'
        '    Actual -.-> Lower\n'
        '    Note["For all n >= n0, f(n) is bounded between Floor and Ceiling"]\n'
        "```\n\n"
        "### 🔄 Essential Theorem: Relation Between $O, \\Omega, \\Theta$\n"
        "> [!IMPORTANT]\n"
        "> $f(n) = \\Theta(g(n))$ **if and only if** $f(n) = O(g(n))$ **and** $f(n) = \\Omega(g(n))$.\n"
        "> If an algorithm's worst case and best case both grow at rate $n$, its tight bound is $\\Theta(n)$."
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: Prove that $f(n) = 5n^2 + 20n + 15$ is $O(n^2)$. Find valid constants $c$ and $n_0$.\n\n"
        "> [!TIP]\n"
        "> **Hint**: For $n \\ge 1$, we know $20n \\le 20n^2$ and $15 \\le 15n^2$. Therefore $5n^2 + 20n + 15 \\le 5n^2 + 20n^2 + 15n^2 = 40n^2$. Choose $c = 40$ and $n_0 = 1$!\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Big-O is NOT Always Worst-Case**: Big-O is a mathematical upper bound on any function. An algorithm can have a Big-O for its best case ($O(1)$) and a Big-O for its worst case ($O(n)$).\n"
        "2. **The Constant Multiple Rule**: Never include constant multipliers in Big-O. Writing $O(4n)$ or $O(2n^2)$ will lose marks in exams; write $O(n)$ and $O(n^2)$.\n"
        "3. **Theta Requires Both**: You cannot claim $f(n) = \\Theta(n)$ unless you prove both upper bound ($O(n)$) and lower bound ($\\Omega(n)$)."
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Intuitive Concept: Upper, Lower, and Tight Bounds", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example: Formal Asymptotic Proofs", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Framework: Asymptotic Bounds", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("logical_analytical"),
        blocks=blocks,
        prerequisites=["Function Growth Rates", "Inequalities"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="beginner", question_count=3, evaluation_criteria=["Mathematical Proof"]),
        next_action=NextLearningAction(action_type="practice", target_topic="Best, Average and Worst-Case Analysis", rationale="Apply bounds to input scenarios.", urgency="normal"),
    )


def build_topic_1_7_case_analysis(topic: str, context_id: str) -> GeneratedLesson:
    """Topic 1.7: Best, Average, and Worst-Case Analysis."""
    obj_content = (
        "## 🎯 Learning Outcomes & Context\n"
        "- Understand how algorithm running times vary depending on the arrangement and values of input data, not just input size.\n"
        "- Define Best Case ($B(n)$), Worst Case ($W(n)$), and Average Case ($A(n)$).\n"
        "- Trace linear search step-by-step across all 3 scenarios and understand why engineers prioritize worst-case analysis.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Basic array indexing, linear search loops, and Big-O notation.\n\n"
        "### 💡 Why This Topic Matters\n"
        "In critical safety systems (like aviation autopilots, medical ventilators, and stock exchange matching engines), software cannot afford to rely on 'lucky' best-case inputs. Engineers design around guaranteed worst-case bounds."
    )

    expl_content = (
        "## 🎒 An Everyday Analogy: Searching for Keys in a 10-Pocket Backpack\n"
        "Imagine you have a travel backpack with 10 zippered pockets, and your house keys are inside one of them:\n"
        "1. **Best Case (Lucky Day)**: You open the very first pocket, and there are your keys! It took exactly **1 check**. You cannot do better than this ($O(1)$).\n"
        "2. **Average Case (Typical Day)**: On most days, the keys might be in the 3rd, 5th, or 7th pocket. Averaged over many trials, you will open about half the pockets: $10 / 2 = 5$ checks ($O(n/2) = O(n)$).\n"
        "3. **Worst Case (Unlucky Day)**: The keys are in the very last 10th pocket (or you left them at the office, so you check all 10 pockets and find nothing). It took **10 checks** ($O(n)$).\n\n"
        "> [!NOTE]\n"
        "> **Why Do We Focus on Worst Case?**:\n"
        "> 1. **Guaranteed Ceiling**: The algorithm will NEVER take longer than its worst case.\n"
        "> 2. **Frequent Reality**: In searching and database lookups, absent keys (worst-case) are common.\n"
        "> 3. **Average Case is Often Same Order**: For linear search, average case $n/2$ is still $O(n)$, identical in growth order to worst case $n$!\n\n"
        "### Case Comparison for Standard Algorithms\n\n"
        "| Algorithm | Best Case | Average Case | Worst Case | Worst-Case Condition |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "| **Linear Search** | $O(1)$ | $O(n)$ | $O(n)$ | Target is at end or absent |\n"
        "| **Binary Search** | $O(1)$ | $O(\\log n)$ | $O(\\log n)$ | Target is at leaf or absent |\n"
        "| **Insertion Sort** | $O(n)$ (already sorted) | $O(n^2)$ | $O(n^2)$ | Array in reverse order |\n"
        "| **Merge Sort** | $O(n \\log n)$ | $O(n \\log n)$ | $O(n \\log n)$ | Always divides evenly |\n"
        "| **Quick Sort** | $O(n \\log n)$ | $O(n \\log n)$ | $O(n^2)$ | Poor pivot (e.g. already sorted) |"
    )

    code_snippet = (
        "# Linear Search: Demonstrating Best, Average, and Worst Cases\n"
        "def linear_search_with_steps(arr: list, target: int) -> tuple:\n"
        "    steps = 0\n"
        "    for idx, value in enumerate(arr):\n"
        "        steps += 1\n"
        "        if value == target:\n"
        "            return idx, steps  # Found: return index and steps taken\n"
        "    return -1, steps          # Not found: searched all elements\n\n"
        "# Sample dataset with n = 8 elements\n"
        "data = [42, 15, 88, 34, 91, 23, 76, 50]\n"
        "\n"
        "# Scenario 1: Best Case (Target at index 0)\n"
        "_, best_steps = linear_search_with_steps(data, 42)\n"
        "assert best_steps == 1      # Exactly 1 comparison -> O(1)\n"
        "\n"
        "# Scenario 2: Average Case (Target in middle at index 4)\n"
        "_, avg_steps = linear_search_with_steps(data, 91)\n"
        "assert avg_steps == 5       # About n/2 comparisons -> O(n)\n"
        "\n"
        "# Scenario 3: Worst Case (Target absent or last element)\n"
        "_, worst_steps = linear_search_with_steps(data, 999)\n"
        "assert worst_steps == 8     # Exactly n comparisons -> O(n)"
    )

    code_content = (
        "## 🛠️ Step-by-Step Code Walkthrough\n"
        "Let's trace linear search on an array of $n = 8$ elements (`[42, 15, 88, 34, 91, 23, 76, 50]`):\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 Step-by-Step Scenario Trace Table ($n = 8$)\n\n"
        "| Scenario | Target Searched | Comparison Sequence | Total Steps | Asymptotic Order |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "| **Best Case** | `42` (Index 0) | `arr[0] == 42` (Match!) | **1** | $O(1)$ |\n"
        "| **Average Case** | `91` (Index 4) | `42, 15, 88, 34, 91` (Match!) | **5** ($\approx n/2$) | $O(n)$ |\n"
        "| **Worst Case (Last)** | `50` (Index 7) | `42, 15, 88, 34, 91, 23, 76, 50` | **8** ($n$) | $O(n)$ |\n"
        "| **Worst Case (Absent)**| `999` (Missing) | Checks all 8 elements, none match | **8** ($n$) | $O(n)$ |"
    )

    vis_content = (
        "## 📊 Visual Framework: Decision Branching in Searching\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    Start["Start Linear Search at Index 0"] --> Check{"arr[i] == Target?"}\n'
        '    Check -- "Yes (i = 0)" --> Best["Best Case: 1 Step -> O(1)"]\n'
        '    Check -- "Yes (i = n/2)" --> Avg["Average Case: n/2 Steps -> O(n)"]\n'
        '    Check -- "No (End or Missing)" --> Worst["Worst Case: n Steps -> O(n)"]\n'
        "```\n\n"
        "### 🔄 Mathematical Formulation of Average Case\n"
        "Assuming the target is equally likely to be at any index $1, 2, \\dots, n$:\n"
        "$$A(n) = \\frac{1}{n} \\sum_{i=1}^{n} i = \\frac{1}{n} \\cdot \\frac{n(n+1)}{2} = \\frac{n+1}{2} = O(n)$$"
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: Suppose an algorithm searches for an item in a sorted array of $n = 1024$ items using Binary Search.\n"
        "1. What is the Best Case number of comparisons?\n"
        "2. What is the Worst Case number of comparisons?\n\n"
        "> [!TIP]\n"
        "> **Hint**: In Binary Search, best case is when the target is at the exact middle on the first check (1 comparison). Worst case is $\\log_2(1024) = 10$ comparisons!\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Never Confuse Best Case with Small Input**: Best case is NOT when $n=1$. Best case is the most favorable arrangement of input data for any given size $n$.\n"
        "2. **Average Case Requires Probability**: You cannot compute average case without an assumption about the probability distribution of inputs (usually assumed uniform).\n"
        "3. **Worst Case is the Industry Gold Standard**: Software SLAs (Service Level Agreements) and real-time systems are always engineered to worst-case complexity."
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Intuitive Concept: Best, Average, and Worst Case Scenarios", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example: Tracing Linear Search Scenarios", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Framework: Case Scenarios Comparison", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("foundational_support"),
        blocks=blocks,
        prerequisites=["Asymptotic Bounds", "Linear Search"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="beginner", question_count=3, evaluation_criteria=["Performance Analysis"]),
        next_action=NextLearningAction(action_type="practice", target_topic="Divide and Conquer", rationale="Advance to Chapter 2: Divide and Conquer paradigms.", urgency="normal"),
    )


def build_topic_2_divide_and_conquer(topic: str, context_id: str) -> GeneratedLesson:
    """Chapter 2: Divide and Conquer & Merge Sort / Binary Search / Master Theorem."""
    obj_content = (
        f"## 🎯 Learning Outcomes & Context: {topic}\n"
        "- Master the three-phase Divide-and-Conquer paradigm: **Divide** into subproblems, **Conquer** recursively, and **Combine** sub-solutions.\n"
        "- Formulate and solve recurrence relations using the Master Theorem ($T(n) = aT(n/b) + f(n)$).\n"
        "- Implement stable $O(n \\log n)$ recursive sorting with linear merge passes.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Recursive function call mechanics and asymptotic notation ($O, \\log n$).\n\n"
        "### 💡 Why This Topic Matters\n"
        "Divide and conquer enables massive scale. It powers database indexing, Google search ranking, distributed map-reduce architectures, and fast Fourier transforms in graphics processing."
    )

    expl_content = (
        "## 📚 An Everyday Analogy: Sorting a Giant Stack of Playing Cards\n"
        "Imagine you are given a disorganized deck of 100 playing cards to sort:\n"
        "1. Trying to sort 100 cards all at once in your hands is frustrating and slow ($O(n^2)$).\n"
        "2. Instead, you split the deck into two piles of 50 cards (**Divide**).\n"
        "3. You hand one pile to a friend and keep one yourself, splitting each down until you have piles of just 1 card (**Conquer**).\n"
        "4. A 1-card pile is already sorted! Now, you take two sorted piles and weave them together by comparing only the top cards (**Combine**).\n\n"
        "> [!NOTE]\n"
        "> **The Divide-and-Conquer Paradigm**:\n"
        "> - **Divide**: Split problem of size $n$ into $a$ subproblems of size $n/b$.\n"
        "> - **Conquer**: Solve the subproblems recursively (base case: size $\\le 1$).\n"
        "> - **Combine**: Merge sub-solutions into the final solution in $O(n^d)$ time.\n\n"
        "### Master Theorem Summary Table ($T(n) = aT(n/b) + \\Theta(n^k \\log^p n)$)\n\n"
        "| Case | Condition | Resulting Complexity | Classic Example |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **Case 1** | $\\log_b a > k$ (Subproblems dominate) | $T(n) = \\Theta(n^{\\log_b a})$ | Strassen's Matrix Multiplication ($O(n^{2.81})$) |\n"
        "| **Case 2** | $\\log_b a = k$ (Work evenly split) | $T(n) = \\Theta(n^k \\log^{p+1} n)$ | **Merge Sort**: $2T(n/2) + O(n) \\implies O(n \\log n)$ |\n"
        "| **Case 3** | $\\log_b a < k$ (Root combine dominates) | $T(n) = \\Theta(f(n))$ | Algorithms where combine work dominates |"
    )

    code_snippet = (
        "def merge_sort(arr: list) -> list:\n"
        '    """Sorts an array using divide-and-conquer with O(n log n) runtime."""\n'
        "    # Base case: 0 or 1 element is inherently sorted\n"
        "    if len(arr) <= 1:\n"
        "        return arr\n\n"
        "    # Step 1: Divide\n"
        "    mid = len(arr) // 2\n"
        "    left_half = merge_sort(arr[:mid])\n"
        "    right_half = merge_sort(arr[mid:])\n\n"
        "    # Step 2: Combine (Linear two-pointer merge)\n"
        "    merged = []\n"
        "    i = j = 0\n"
        "    while i < len(left_half) and j < len(right_half):\n"
        "        if left_half[i] <= right_half[j]:  # <= ensures stability\n"
        "            merged.append(left_half[i])\n"
        "            i += 1\n"
        "        else:\n"
        "            merged.append(right_half[j])\n"
        "            j += 1\n"
        "    merged.extend(left_half[i:])\n"
        "    merged.extend(right_half[j:])\n"
        "    return merged\n\n"
        "# Verification\n"
        "assert merge_sort([38, 27, 43, 3, 9, 82, 10]) == [3, 9, 10, 27, 38, 43, 82]\n"
        "assert merge_sort([]) == []\n"
        "assert merge_sort([42]) == [42]"
    )

    code_content = (
        "## 🛠️ Step-by-Step Code Walkthrough\n"
        "Let's trace how Merge Sort divides and merges an array:\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 Two-Pointer Merge Step Trace Table (Merging `[27, 38]` and `[3, 43]`)\n\n"
        "| Step | Pointer `i` (Left) | Pointer `j` (Right) | Comparison | Appended Element | Resulting `merged` |\n"
        "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        "| 1 | `left[0] = 27` | `right[0] = 3` | $27 > 3$ | `3` (from right) | `[3]` |\n"
        "| 2 | `left[0] = 27` | `right[1] = 43` | $27 \\le 43$ | `27` (from left) | `[3, 27]` |\n"
        "| 3 | `left[1] = 38` | `right[1] = 43` | $38 \\le 43$ | `38` (from left) | `[3, 27, 38]` |\n"
        "| 4 | Left exhausted | `right[1] = 43` | Residual append | `43` (from right) | `[3, 27, 38, 43]` |"
    )

    vis_content = (
        "## 📊 Visual Hierarchy: Recursive Divide-and-Conquer Tree\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    A["[38, 27, 43, 3, 9, 82, 10] (Size n)"] --> B["Left: [38, 27, 43, 3] (n/2)"]\n'
        '    A --> C["Right: [9, 82, 10] (n/2)"]\n'
        '    B --> D["[38, 27]"]\n'
        '    B --> E["[43, 3]"]\n'
        '    C --> F["[9]"]\n'
        '    C --> G["[82, 10]"]\n'
        '    D & E --> H["Merged: [3, 27, 38, 43]"]\n'
        '    F & G --> I["Merged: [9, 10, 82]"]\n'
        '    H & I --> J["Final Sorted: [3, 9, 10, 27, 38, 43, 82]"]\n'
        "```\n\n"
        "### 🔄 Tree Height & Work Analysis\n"
        "- **Tree Height**: Dividing by 2 each level creates exactly $\\log_2 n$ levels.\n"
        "- **Work Per Level**: Merging across all sub-arrays at any single level takes $O(n)$ operations.\n"
        "- **Total Complexity**: $\\log_2 n \\times O(n) = O(n \\log n)$."
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: Solve the recurrence relation $T(n) = 2T(n/2) + n$ using the Master Theorem.\n"
        "1. Identify $a, b,$ and $f(n)$.\n"
        "2. Compute $\\log_b a$.\n"
        "3. Compare with $f(n)$ and state the complexity.\n\n"
        "> [!TIP]\n"
        "> **Hint**: $a = 2, b = 2, f(n) = n^1$. Then $\\log_2 2 = 1$. Since $k = 1 = \\log_b a$, this is Case 2: $T(n) = \\Theta(n \\log n)$!\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Merge Sort Stability**: Using `<=` when comparing `left[i] <= right[j]` ensures stable sorting (equal elements retain their original relative order).\n"
        "2. **Merge Sort Space Tradeoff**: Standard Merge Sort requires $O(n)$ auxiliary space to allocate merged sub-arrays.\n"
        "3. **Quick Sort vs Merge Sort**: Quick sort sorts in-place ($O(1)$ auxiliary memory) and has lower constant factors, but degrades to $O(n^2)$ on worst-case pivots. Merge sort guarantees $O(n \\log n)$ worst-case."
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Conceptual Masterclass: Divide, Conquer, Combine", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example: Merge Sort Divide & Merge Pass", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Hierarchy: Recursion Tree", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("logical_analytical"),
        blocks=blocks,
        prerequisites=["Recurrence Relations", "Recursion Tree"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="intermediate", question_count=3, evaluation_criteria=["Divide and Conquer Mastery"]),
        next_action=NextLearningAction(action_type="practice", target_topic="Greedy Algorithms", rationale="Advance to Chapter 3: Greedy Methods.", urgency="normal"),
    )


def build_topic_3_greedy(topic: str, context_id: str) -> GeneratedLesson:
    """Chapter 3: Greedy Algorithms & Fractional Knapsack / Activity Selection."""
    obj_content = (
        f"## 🎯 Learning Outcomes & Context: {topic}\n"
        "- Understand the Greedy Method: making the locally optimal choice at each step with the hope of finding a global optimum.\n"
        "- Learn the two necessary conditions for greedy algorithms: Greedy-Choice Property and Optimal Substructure.\n"
        "- Implement the Fractional Knapsack problem by sorting items by value-to-weight ratio.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Basic array sorting and understanding of optimization objectives (maximize profit / minimize cost).\n\n"
        "### 💡 Why This Topic Matters\n"
        "Greedy algorithms power bandwidth routing in computer networks (Dijkstra's shortest path), file compression in ZIP formats (Huffman coding), and scheduling in cloud servers."
    )

    expl_content = (
        "## 🪙 An Everyday Analogy: Cashier Giving Change\n"
        "Imagine you are a store cashier giving a customer ₹47 in change using denominations of ₹20, ₹10, ₹5, ₹2, and ₹1:\n"
        "1. You pick the largest coin that does not exceed ₹47: a ₹20 note (remaining: ₹27).\n"
        "2. Next largest: another ₹20 note (remaining: ₹7).\n"
        "3. Next largest: a ₹5 coin (remaining: ₹2).\n"
        "4. Next largest: a ₹2 coin (remaining: ₹0).\n"
        "5. Total coins used: 4. By always picking the biggest bite first, you reached the optimal minimum number of coins!\n\n"
        "> [!NOTE]\n"
        "> **The Greedy Choice Property**: A globally optimal solution can always be arrived at by making locally optimal (greedy) choices without ever reconsidering past choices.\n\n"
        "### When Does Greedy Fail? (The Trap)\n"
        "If coin denominations were ₹1, ₹6, and ₹9, giving ₹12 change with greedy gives ₹9 + ₹1 + ₹1 + ₹1 = 4 coins. But the true optimal is two ₹6 coins (2 coins)! Greedy only works when the problem possesses the matroid / greedy-choice property."
    )

    code_snippet = (
        "# Fractional Knapsack Implementation: O(n log n)\n"
        "def fractional_knapsack(capacity: float, items: list) -> float:\n"
        '    """Items format: list of dicts with {"weight": float, "value": float}."""\n'
        "    # Step 1: Calculate value-to-weight ratio and sort descending\n"
        "    sorted_items = sorted(items, key=lambda x: x['value'] / x['weight'], reverse=True)\n"
        "    \n"
        "    total_value = 0.0\n"
        "    remaining_capacity = capacity\n"
        "    \n"
        "    for item in sorted_items:\n"
        "        if remaining_capacity <= 0:\n"
        "            break\n"
        "        if item['weight'] <= remaining_capacity:\n"
        "            # Take entire item\n"
        "            total_value += item['value']\n"
        "            remaining_capacity -= item['weight']\n"
        "        else:\n"
        "            # Take fraction of the item to fill the remaining bag\n"
        "            fraction = remaining_capacity / item['weight']\n"
        "            total_value += item['value'] * fraction\n"
        "            remaining_capacity = 0\n"
        "            \n"
        "    return round(total_value, 2)\n\n"
        "# Test verification with capacity = 50kg\n"
        "test_items = [\n"
        "    {'weight': 10, 'value': 60},   # ratio: 6.0\n"
        "    {'weight': 20, 'value': 100},  # ratio: 5.0\n"
        "    {'weight': 30, 'value': 120},  # ratio: 4.0\n"
        "]\n"
        "assert fractional_knapsack(50, test_items) == 240.0"
    )

    code_content = (
        "## 🛠️ Step-by-Step Code Walkthrough\n"
        "Let's trace how the Fractional Knapsack algorithm processes items for capacity = 50kg:\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 Greedy Selection Trace Table (Capacity = 50kg)\n\n"
        "| Item | Weight | Value | Ratio ($V/W$) | Fraction Taken | Value Added | Remaining Capacity |\n"
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        "| Item 1 | 10kg | ₹60 | **6.0** | 100% (10kg) | ₹60 | 40kg |\n"
        "| Item 2 | 20kg | ₹100 | **5.0** | 100% (20kg) | ₹100 | 20kg |\n"
        "| Item 3 | 30kg | ₹120 | **4.0** | 66.6% (20kg/30kg) | ₹80 | **0kg (Full!)** |\n"
        "| Total | 50kg | — | — | — | **₹240.0** | — |"
    )

    vis_content = (
        "## 📊 Visual Framework: Greedy Selection Flowchart\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    Start["Start: List of Items & Bag Capacity W"] --> Sort["Sort Items by Value / Weight Ratio (O(n log n))"]\n'
        '    Sort --> Check{"Bag Has Remaining Space?"}\n'
        '    Check -- "No" --> Done["Finish: Return Total Profit"]\n'
        '    Check -- "Yes" --> CanFit{"Item Weight <= Remaining W?"}\n'
        '    CanFit -- "Yes" --> TakeAll["Take Entire Item, Deduct Weight"]\n'
        '    CanFit -- "No" --> TakeFraction["Take Fraction (W / Weight), Fill Bag"]\n'
        '    TakeAll --> Check\n'
        '    TakeFraction --> Done\n'
        "```"
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: Suppose you have an Activity Selection problem with 3 activities: A1 [1-4], A2 [3-5], A3 [0-6] (given as [start-finish]).\n"
        "Which activity should be selected first according to the greedy rule?\n\n"
        "> [!TIP]\n"
        "> **Hint**: In Activity Selection, always sort by earliest **finish time**. A1 finishes at 4, A2 at 5, A3 at 6. Select A1 first!\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Fractional vs 0/1 Knapsack**: Fractional Knapsack can be solved greedily in $O(n \\log n)$; 0/1 Knapsack cannot be solved greedily and requires Dynamic Programming!\n"
        "2. **Greedy-Choice vs Dynamic Programming**: Greedy makes its choice before solving subproblems; DP solves subproblems first before making a choice.\n"
        "3. **Standard Greedy Algorithms**: Prim's, Kruskal's, Dijkstra's, Huffman, and Activity Selection."
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Conceptual Masterclass: The Greedy Strategy", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example: Fractional Knapsack Trace", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Framework: Greedy Decision Flow", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("practical_applied"),
        blocks=blocks,
        prerequisites=["Array Sorting", "Optimization Objectives"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="intermediate", question_count=3, evaluation_criteria=["Greedy Algorithm Design"]),
        next_action=NextLearningAction(action_type="practice", target_topic="Dynamic Programming", rationale="Advance to Chapter 4: Dynamic Programming.", urgency="normal"),
    )


def build_topic_4_dynamic_programming(topic: str, context_id: str) -> GeneratedLesson:
    """Chapter 4: Dynamic Programming & 0/1 Knapsack / Memoization / Tabulation."""
    obj_content = (
        f"## 🎯 Learning Outcomes & Context: {topic}\n"
        "- Understand the core philosophy of Dynamic Programming: solving subproblems once and storing results in memory.\n"
        "- Identify the two pillars of DP: **Optimal Substructure** and **Overlapping Subproblems**.\n"
        "- Master the difference between Top-Down Memoization and Bottom-Up Tabulation.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Recursion trees and call stack visualization.\n\n"
        "### 💡 Why This Topic Matters\n"
        "Dynamic Programming transforms impossible $O(2^n)$ exponential problems into practical $O(n \\cdot W)$ polynomial solutions. It is foundational in genomic DNA sequence alignment (Needleman-Wunsch) and financial portfolio optimization."
    )

    expl_content = (
        "## 📝 An Everyday Analogy: Writing Answers on a Scratchpad\n"
        "Suppose your teacher asks you:\n"
        "- Teacher: 'What is $1 + 1 + 1 + 1 + 1$?'\n"
        "- You (counting): '5!'\n"
        "- Teacher (adds '+ 1' to the end): 'What is it now?'\n"
        "- You (instantly): '6!'\n"
        "- Teacher: 'How did you know so fast without recounting from 1?'\n"
        "- You: 'I remembered that earlier it was 5, so I just added 1!'\n\n"
        "That is Dynamic Programming in a nutshell. **Remembering past work so you never recalculate it!**\n\n"
        "> [!NOTE]\n"
        "> **Two Essential Requirements for DP**:\n"
        "> 1. **Optimal Substructure**: The optimal solution to the problem contains optimal solutions to its subproblems.\n"
        "> 2. **Overlapping Subproblems**: The same recursive subproblems are encountered again and again."
    )

    code_snippet = (
        "# Dynamic Programming: Fibonacci Tabulation vs Recursion\n"
        "\n"
        "# Approach: Bottom-up Tabulation O(n) time, O(n) space\n"
        "def fibonacci_dp(n: int) -> int:\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    # Table to store computed answers\n"
        "    dp = [0] * (n + 1)\n"
        "    dp[0] = 0\n"
        "    dp[1] = 1\n"
        "    \n"
        "    # Fill bottom-up\n"
        "    for i in range(2, n + 1):\n"
        "        dp[i] = dp[i - 1] + dp[i - 2]\n"
        "        \n"
        "    return dp[n]\n\n"
        "# Assertions\n"
        "assert fibonacci_dp(0) == 0\n"
        "assert fibonacci_dp(1) == 1\n"
        "assert fibonacci_dp(6) == 8\n"
        "assert fibonacci_dp(10) == 55"
    )

    code_content = (
        "## 🛠️ Step-by-Step Code Walkthrough\n"
        "Let's trace how the DP table is populated from base cases up to $n = 6$:\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 DP Tabulation State Table ($n = 6$)\n\n"
        "| $i$ | State `dp[i]` | Computation `dp[i-1] + dp[i-2]` | Subproblem Reused |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| 0 | 0 | Base case | — |\n"
        "| 1 | 1 | Base case | — |\n"
        "| 2 | 1 | $1 + 0 = 1$ | Reuses $dp[1]$ and $dp[0]$ |\n"
        "| 3 | 2 | $1 + 1 = 2$ | Reuses $dp[2]$ and $dp[1]$ |\n"
        "| 4 | 3 | $2 + 1 = 3$ | Reuses $dp[3]$ and $dp[2]$ |\n"
        "| 5 | 5 | $3 + 2 = 5$ | Reuses $dp[4]$ and $dp[3]$ |\n"
        "| **6** | **8** | $5 + 3 = 8$ | **Final Result in $O(n)$ time!** |"
    )

    vis_content = (
        "## 📊 Visual Framework: Overlapping Subproblems Tree\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    F5["fib(5)"] --> F4["fib(4)"]\n'
        '    F5 --> F3A["fib(3) [Repeated!]"]\n'
        '    F4 --> F3B["fib(3) [Repeated!]"]\n'
        '    F4 --> F2A["fib(2)"]\n'
        '    F3A --> F2B["fib(2)"]\n'
        '    F3A --> F1A["fib(1)"]\n'
        '    Note["Notice fib(3) and fib(2) are computed multiple times. DP caches them!"]\n'
        "```"
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: In the 0/1 Knapsack problem with weights $w = [2, 3]$ and values $v = [10, 20]$ and maximum capacity $W = 5$:\n"
        "Can you take both items? What is the maximum value you can achieve?\n\n"
        "> [!TIP]\n"
        "> **Hint**: Total weight = $2 + 3 = 5 \\le W$. Since both fit, maximum value = $10 + 20 = 30$!\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Memoization vs Tabulation**: Memoization is Top-Down (recursive + dictionary cache); Tabulation is Bottom-Up (iterative loop + array table).\n"
        "2. **0/1 Knapsack Recurrence**: $DP[i][w] = \\max(DP[i-1][w], v[i-1] + DP[i-1][w - wt[i-1]])$.\n"
        "3. **Common Exam Trap**: Fractional knapsack items can be cut; in 0/1 knapsack you must either take the whole item or leave it."
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Conceptual Masterclass: Memoization and Tabulation", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example: DP Fibonacci Tabulation", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Framework: Overlapping Subproblems", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("logical_analytical"),
        blocks=blocks,
        prerequisites=["Recursion Tree", "State Arrays"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="intermediate", question_count=3, evaluation_criteria=["DP Formulation"]),
        next_action=NextLearningAction(action_type="practice", target_topic="Backtracking", rationale="Advance to Chapter 5: Backtracking.", urgency="normal"),
    )


def build_topic_5_backtracking(topic: str, context_id: str) -> GeneratedLesson:
    """Chapter 5 & 6: Backtracking & N-Queens / Branch and Bound."""
    obj_content = (
        f"## 🎯 Learning Outcomes & Context: {topic}\n"
        "- Understand Backtracking: systematically searching a state-space tree and abandoning ('pruning') paths that violate constraints.\n"
        "- Learn the difference between brute-force search and intelligent constraint-based pruning.\n"
        "- Implement the classic N-Queens puzzle using recursive backtracking.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Recursion and 2D grid coordinates (rows, columns, diagonals).\n\n"
        "### 💡 Why This Topic Matters\n"
        "Backtracking powers modern constraint satisfaction solvers, Sudoku algorithms, compiler register allocation, and circuit layout design."
    )

    expl_content = (
        "## 🧭 An Everyday Analogy: Navigating a Maze\n"
        "Imagine you are exploring an underground maze with multiple branching paths:\n"
        "1. You walk down corridor A until you hit a dead end (a wall).\n"
        "2. What do you do? You don't restart from the beginning of the maze!\n"
        "3. You step backward to the last fork in the road (**Backtrack**) and explore corridor B.\n"
        "4. As soon as you realize a path cannot possibly lead to the exit, you abandon it immediately (**Pruning**).\n\n"
        "> [!NOTE]\n"
        "> **Pruning Condition**: Evaluating a bounding function at node $X$. If the node violates constraints, we prune its entire subtree, eliminating millions of fruitless calculations."
    )

    code_snippet = (
        "# Solving 4-Queens using Backtracking\n"
        "def solve_4_queens():\n"
        "    solutions = []\n"
        "    # board representation: queen_cols[row] = col\n"
        "    \n"
        "    def is_safe(row: int, col: int, queen_cols: list) -> bool:\n"
        "        for r in range(row):\n"
        "            c = queen_cols[r]\n"
        "            # Check same column or same diagonal\n"
        "            if c == col or abs(c - col) == abs(r - row):\n"
        "                return False\n"
        "        return True\n"
        "        \n"
        "    def place_queen(row: int, current_board: list):\n"
        "        if row == 4:\n"
        "            solutions.append(list(current_board))\n"
        "            return\n"
        "        for col in range(4):\n"
        "            if is_safe(row, col, current_board):\n"
        "                current_board.append(col)\n"
        "                place_queen(row + 1, current_board)\n"
        "                current_board.pop()  # Backtrack!\n"
        "                \n"
        "    place_queen(0, [])\n"
        "    return solutions\n\n"
        "# Verification: 4-Queens has exactly 2 unique solutions\n"
        "sols = solve_4_queens()\n"
        "assert len(sols) == 2\n"
        "assert sols[0] == [1, 3, 0, 2]  # Row 0 -> Col 1, Row 1 -> Col 3, etc."
    )

    code_content = (
        "## 🛠️ Step-by-Step Code Walkthrough\n"
        "Let's trace how the 4-Queens solver navigates the board:\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 Decision Trace Table (4-Queens Search)\n\n"
        "| Step | Action | Placement | Status | Next Step |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "| 1 | Place Row 0 | `(0, 0)` | Safe | Move to Row 1 |\n"
        "| 2 | Place Row 1 | `(1, 0)` | Attack (Same Col) | Prune! Try Col 1 |\n"
        "| 3 | Place Row 1 | `(1, 1)` | Attack (Diagonal) | Prune! Try Col 2 |\n"
        "| 4 | Place Row 1 | `(1, 2)` | Safe | Move to Row 2 |\n"
        "| 5 | Row 2 | All 4 cols attacked | Dead end! | **Backtrack to Row 1!** |"
    )

    vis_content = (
        "## 📊 Visual Framework: State-Space Search Tree\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    Root["Start: Empty Board"] --> Q00["Row 0: Col 0"]\n'
        '    Root --> Q01["Row 0: Col 1 [Leads to Solution!]"]\n'
        '    Q00 --> Q12["Row 1: Col 2"]\n'
        '    Q12 --> DeadEnd["Row 2: Dead End (Backtrack!)"]\n'
        '    Q01 --> S1["Complete Valid Placement [1, 3, 0, 2]"]\n'
        "```"
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: In a 4x4 chessboard, if a queen is placed at row 0, column 1 (`(0, 1)`), is column 2 safe for a queen at row 1 (`(1, 2)`)?\n\n"
        "> [!TIP]\n"
        "> **Hint**: Check diagonals: $|col_1 - col_0| = |2 - 1| = 1$ and $|row_1 - row_0| = |1 - 0| = 1$. Since they are equal, they are on the same diagonal! It is NOT safe!\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Backtracking vs Branch and Bound**: Backtracking traverses Depth-First (DFS); Branch and Bound traverses Breadth-First (BFS) or Best-First using priority queues.\n"
        "2. **State-Space Tree**: Every path from root to leaf represents a potential candidate solution.\n"
        "3. **Pruning Saves Time**: Without pruning, 8-queens would check $8^8 \\approx 1.67 \\times 10^7$ boards. Backtracking checks only 2,057 nodes!"
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Conceptual Masterclass: Intelligent Backtracking", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example: 4-Queens Backtracking Trace", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Framework: State-Space Tree", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("logical_analytical"),
        blocks=blocks,
        prerequisites=["Recursion", "State Trees"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="intermediate", question_count=3, evaluation_criteria=["Constraint Search"]),
        next_action=NextLearningAction(action_type="practice", target_topic="Graph Algorithms", rationale="Advance to Chapter 7: Graph Algorithms.", urgency="normal"),
    )


def build_topic_7_graph_algorithms(topic: str, context_id: str) -> GeneratedLesson:
    """Chapter 7: Graph Traversals (BFS / DFS) & Shortest Paths."""
    obj_content = (
        f"## 🎯 Learning Outcomes & Context: {topic}\n"
        "- Understand graph traversal mechanics: visiting all vertices in a connected component systematically.\n"
        "- Compare Breadth-First Search (BFS) using a Queue with Depth-First Search (DFS) using a Stack.\n"
        "- Master time and space complexity: $O(V + E)$ using adjacency lists.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Basic knowledge of vertices, edges, directed vs undirected graphs, and Queue/Stack data structures.\n\n"
        "### 💡 Why This Topic Matters\n"
        "Graph algorithms power social network connections ('People You May Know'), GPS turn-by-turn navigation, web search crawlers, and circuit routing."
    )

    expl_content = (
        "## 👥 An Everyday Analogy: Spreading News in a Social Circle\n"
        "Suppose you have an exciting announcement to share with your college friends:\n"
        "1. **Breadth-First Search (BFS - Ripple in a Pond)**: You tell all your immediate friends first (Level 1). Then they tell their immediate friends (Level 2), expanding outward in concentric circles. BFS always discovers the shortest path in unweighted graphs!\n"
        "2. **Depth-First Search (DFS - Down the Rabbit Hole)**: You tell friend Alice. Alice immediately rushes to tell Bob, and Bob rushes to tell Charlie, going as deep as possible before retracing steps. DFS is ideal for maze solving, cycle detection, and topological sorting.\n\n"
        "> [!NOTE]\n"
        "> **Key Data Structures**:\n"
        "> - **BFS**: Uses a **First-In First-Out (FIFO) Queue**.\n"
        "> - **DFS**: Uses a **Last-In First-Out (LIFO) Stack** (or recursion)."
    )

    code_snippet = (
        "# Breadth-First Search (BFS) on an Adjacency List Graph\n"
        "from collections import deque\n\n"
        "def bfs_traversal(graph: dict, start_vertex: str) -> list:\n"
        "    visited = set([start_vertex])\n"
        "    queue = deque([start_vertex])\n"
        "    order = []\n"
        "    \n"
        "    while queue:\n"
        "        curr = queue.popleft()\n"
        "        order.append(curr)\n"
        "        for neighbor in graph.get(curr, []):\n"
        "            if neighbor not in visited:\n"
        "                visited.add(neighbor)\n"
        "                queue.append(neighbor)\n"
        "                \n"
        "    return order\n\n"
        "# Graph representation\n"
        "sample_graph = {\n"
        "    'A': ['B', 'C'],\n"
        "    'B': ['A', 'D', 'E'],\n"
        "    'C': ['A', 'F'],\n"
        "    'D': ['B'],\n"
        "    'E': ['B'],\n"
        "    'F': ['C'],\n"
        "}\n"
        "assert bfs_traversal(sample_graph, 'A') == ['A', 'B', 'C', 'D', 'E', 'F']"
    )

    code_content = (
        "## 🛠️ Step-by-Step Code Walkthrough\n"
        "Let's trace BFS execution starting from vertex `'A'`:\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 BFS Execution Trace Table\n\n"
        "| Step | Dequeued Vertex | Newly Visited Neighbors | Queue State | Visited Set |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "| Start | — | `A` | `['A']` | `{'A'}` |\n"
        "| 1 | `A` | `B`, `C` | `['B', 'C']` | `{'A', 'B', 'C'}` |\n"
        "| 2 | `B` | `D`, `E` | `['C', 'D', 'E']` | `{'A', 'B', 'C', 'D', 'E'}` |\n"
        "| 3 | `C` | `F` | `['D', 'E', 'F']` | `{'A', 'B', 'C', 'D', 'E', 'F'}` |\n"
        "| 4 | `D` | None | `['E', 'F']` | Unchanged |\n"
        "| 5 | `E` | None | `['F']` | Unchanged |\n"
        "| 6 | `F` | None | `[] (Empty, Halt)` | Complete Traversal |"
    )

    vis_content = (
        "## 📊 Visual Framework: Concentric BFS Waves\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    A["A (Level 0: Start)"] --> B["B (Level 1)"]\n'
        '    A --> C["C (Level 1)"]\n'
        '    B --> D["D (Level 2)"]\n'
        '    B --> E["E (Level 2)"]\n'
        '    C --> F["F (Level 2)"]\n'
        "```"
    )

    task_content = (
        "## 🎯 Guided Practice Challenge\n"
        "**Task**: In an undirected graph with 5 vertices and 4 edges forming a line (A - B - C - D - E), what is the shortest path from A to E discovered by BFS?\n\n"
        "> [!TIP]\n"
        "> **Hint**: BFS visits nodes level by level: A (dist 0), B (dist 1), C (dist 2), D (dist 3), E (dist 4). Shortest path = 4 edges!\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Complexity on Adjacency Lists**: BFS and DFS both run in $O(V + E)$ time and $O(V)$ auxiliary space.\n"
        "2. **Shortest Path Guarantee**: BFS guarantees the shortest path **only** on unweighted graphs (or graphs with uniform edge weights).\n"
        "3. **Cycle Detection**: DFS detects cycles in directed graphs when a node has an edge to an active ancestor on the recursion stack (a Back Edge)."
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Learning Outcomes: {topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Conceptual Masterclass: Graph Traversal Dynamics", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example: BFS Queue Trace", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Framework: Level-by-Level Graph Waves", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice & Exam Takeaways: {topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=topic,
        pedagogy_decision=_make_pedagogy("visual_support"),
        blocks=blocks,
        prerequisites=["Graphs", "Adjacency Lists", "Queues"],
        assessment_intent=AssessmentIntent(target_concepts=[topic], assessment_mode="formative", difficulty="intermediate", question_count=3, evaluation_criteria=["Graph Analysis"]),
        next_action=NextLearningAction(action_type="practice", target_topic="P vs NP", rationale="Advance to Complexity Classes.", urgency="normal"),
    )


def get_daa_lesson(topic: str, context_id: str) -> Optional[GeneratedLesson]:
    """Routes specific DAA curriculum topics to high-depth, simplified pedagogical lessons."""
    clean = (topic or "").strip()
    low = clean.lower()

    # Chapter 1: Introduction to Algorithms
    if any(k in low for k in ["introduction to algorithm", "what is an algorithm", "characteristics of algorithm", "algorithm design and analysis", "properties of algorithm"]):
        return build_topic_1_1_intro_to_algorithms(clean, context_id)

    if any(k in low for k in ["time complexity", "growth of function", "operation count"]):
        return build_topic_1_4_time_complexity(clean, context_id)

    if any(k in low for k in ["space complexity", "auxiliary space", "memory requirement"]):
        return build_topic_1_5_space_complexity(clean, context_id)

    if any(k in low for k in ["asymptotic notation", "big-o", "big o", "big-omega", "big-theta", "asymptotic bound"]):
        return build_topic_1_6_asymptotic_notations(clean, context_id)

    if any(k in low for k in ["best, average", "best average", "worst-case", "worst case", "case analysis"]):
        return build_topic_1_7_case_analysis(clean, context_id)

    # Chapter 2: Divide and Conquer / Sorting / Recurrence
    if any(k in low for k in ["divide and conquer", "divide-and-conquer", "merge sort", "quick sort", "master theorem", "binary search", "recurrence relation", "maximum and minimum"]):
        return build_topic_2_divide_and_conquer(clean, context_id)

    # Chapter 3: Greedy Algorithms
    if any(k in low for k in ["greedy", "fractional knapsack", "activity selection", "job sequencing", "huffman", "prim", "kruskal", "dijkstra"]):
        return build_topic_3_greedy(clean, context_id)

    # Chapter 4: Dynamic Programming
    if any(k in low for k in ["dynamic programming", "memoization", "tabulation", "0/1 knapsack", "longest common subsequence", "matrix chain"]):
        return build_topic_4_dynamic_programming(clean, context_id)

    # Chapter 5 & 6: Backtracking / Branch & Bound
    if any(k in low for k in ["backtracking", "n-queens", "n queens", "branch and bound", "traveling salesperson", "subset sum"]):
        return build_topic_5_backtracking(clean, context_id)

    # Chapter 7: Graph Algorithms & Traversals
    if any(k in low for k in ["graph traversal", "breadth-first search", "bfs", "depth-first search", "dfs", "shortest path", "topological sort"]):
        return build_topic_7_graph_algorithms(clean, context_id)

    # General DAA subject fallback (satisfies test_daa_lesson_generates_algorithm_code_not_sql)
    if "design and analysis of algorithms" in low or low == "daa":
        return build_topic_2_divide_and_conquer(clean, context_id)

    return None

