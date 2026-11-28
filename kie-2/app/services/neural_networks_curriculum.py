"""
UniOS Artificial Neural Networks Reference Curriculum
Implements the UniOS Adaptive Learn Module Teaching Blueprint for Neural Networks (Section 5).
Reference lesson used to validate the UniOS guided teaching system.
"""

from typing import Optional
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


def _make_pedagogy() -> PedagogyDecision:
    return PedagogyDecision(
        strategy=TeachingStrategy.FOUNDATIONAL,
        adaptive_strategy="foundational_support",
        difficulty=DifficultyLevel.BEGINNER,
        presentation_mode=PresentationMode.TRADITIONAL,
        explanation_depth="step-by-step",
        rationale="Calibrated with curiosity trigger, step-by-step neuron mathematics, PyTorch coding lab, and targeted misconception remediation.",
        practice_level=PracticeLevel.GUIDED,
        remediation=False,
    )


def build_neural_networks_lesson(topic: str = "Artificial Neural Networks", context_id: str = "ctx-nn-001") -> GeneratedLesson:
    """Builds the authoritative reference lesson for Neural Networks according to Section 5."""
    clean_topic = (topic or "Artificial Neural Networks").strip()

    # Stage A: Curiosity trigger & Learning Outcomes
    obj_content = (
        "## 🎯 Curiosity Trigger: How Does a Machine See?\n"
        "How can a smartphone unlock with your face in milliseconds, or how can a postal sorting machine instantly identify handwritten digits on an envelope?\n\n"
        "To a computer, an image is not colors and shapes—it is a numerical grid of pixel values (for example, a $28 \\times 28$ image is just 784 numbers between 0 and 255). "
        "An **Artificial Neural Network (ANN)** learns mathematical patterns from thousands of training examples to map these raw numbers into accurate predictions.\n\n"
        "### 📚 Prerequisites & Readiness\n"
        "- Basic Python programming (variables, functions, lists).\n"
        "- Elementary algebra: linear equations ($y = mx + b$) and vector dot products.\n\n"
        "### 🎯 Explicit Learning Outcomes\n"
        "- **LO1 (Explain)**: Explain the biological inspiration and computational mechanics of an artificial neuron and layered feedforward networks.\n"
        "- **LO2 (Calculate)**: Calculate the pre-activation weighted sum $z = \\sum w_i x_i + b$ and activation output $y = f(z)$ by hand.\n"
        "- **LO3 (Compare)**: Describe the mathematical behavior and practical use cases of ReLU, Sigmoid, and Softmax activation functions.\n"
        "- **LO4 (Distinguish)**: Differentiate forward propagation, loss calculation, backpropagation (chain rule), and gradient optimization.\n"
        "- **LO5 (Implement)**: Build a small modular classifier architecture in PyTorch and trace tensor dimensions."
    )

    # Stage B & C & D & E: Concept Explanation, The Neuron, Activations, How a Network Learns
    expl_content = (
        "## 🧠 Conceptual Masterclass: Architecture of a Neural Network\n"
        "An Artificial Neural Network is a machine-learning model composed of interconnected computational units called **artificial neurons**. "
        "A typical feedforward network organizes neurons into sequential layers where information flows strictly in one direction from input to output:\n\n"
        "- **Input Layer**: Receives raw feature vectors (e.g., 784 pixel intensities).\n"
        "- **Hidden Layers**: Learn intermediate representations through weighted affine transformations and non-linear activation functions.\n"
        "- **Output Layer**: Produces prediction logits or scores corresponding to target classes (e.g., 10 scores for digits 0–9).\n\n"
        "> [!NOTE]\n"
        "> **Mathematical Model of an Artificial Neuron**:\n"
        "> An artificial neuron takes multiple inputs, multiplies each by a learnable weight, adds a learnable bias, and passes the result through an activation function:\n"
        "> $$z = w_1 x_1 + w_2 x_2 + \\dots + w_n x_n + b = \\sum_{i=1}^{n} w_i x_i + b$$\n"
        "> $$y = f(z)$$\n\n"
        "### Mathematical Symbols & Definitions\n\n"
        "| Symbol | Name | Role & Meaning |\n"
        "| :--- | :--- | :--- |\n"
        "| $x_i$ | Input Feature | The input data signal fed into the neuron. |\n"
        "| $w_i$ | Learnable Weight | Controls the strength and contribution of the input feature toward the output. |\n"
        "| $b$ | Learnable Bias | An independent scalar that shifts the activation threshold, even when all inputs are 0. |\n"
        "| $z$ | Pre-Activation | The linear weighted sum before the activation function is applied. |\n"
        "| $f(\\cdot)$ | Activation Function | Introduces non-linearity, allowing the network to learn complex non-linear patterns. |\n"
        "| $y$ | Neuron Output | The final transformed signal propagated to downstream layers. |\n\n"
        "### Core Activation Functions Compared\n\n"
        "| Function | Formula | Output Range | Typical Role & Critical Caution |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **ReLU** | $f(x) = \\max(0, x)$ | $[0, \\infty)$ | **Standard in hidden layers**: Computationally fast and prevents vanishing gradients for positive inputs. Negative inputs yield 0. |\n"
        "| **Sigmoid** | $\\sigma(x) = \\frac{1}{1 + e^{-x}}$ | $(0, 1)$ | **Used in binary classification outputs**: Squeezes numbers into $(0, 1)$. *Caution*: Can saturate at extremes, causing vanishing gradients. |\n"
        "| **Softmax** | $\\text{Softmax}(z_i) = \\frac{e^{z_i}}{\\sum e^{z_j}}$ | $(0, 1)$, $\\sum = 1$ | **Used in multiclass outputs**: Normalizes logits into a distribution summing to 1. *Caution*: Softmax outputs require calibration evaluation before being treated as true probabilities. |\n\n"
        "### 🔄 How a Neural Network Learns: The 4-Stage Training Loop\n"
        "Training does NOT occur by guessing weights randomly. It follows a mathematically principled 4-stage optimization cycle:\n"
        "1. **Forward Propagation**: Inputs pass through layers to produce output predictions $\\hat{y}$.\n"
        "2. **Loss Calculation**: A loss function (e.g., CrossEntropyLoss or Mean Squared Error) quantifies the discrepancy between predictions and actual ground-truth labels.\n"
        "3. **Backpropagation**: The multivariable calculus **chain rule** computes partial derivatives (gradients $\\frac{\\partial \\mathcal{L}}{\\partial w}$, $\\frac{\\partial \\mathcal{L}}{\\partial b}$) indicating how each parameter contributed to the error.\n"
        "4. **Optimization**: An optimizer (such as Stochastic Gradient Descent or Adam) updates parameters in the opposite direction of the gradient ($w \\leftarrow w - \\eta \\nabla_w \\mathcal{L}$).\n"
        "This loop repeats across batches and epochs while tracking validation metrics to avoid overfitting."
    )

    # Stage C & G: Worked Numerical Example & PyTorch Coding Lab
    code_snippet = (
        "import torch\n"
        "import torch.nn as nn\n\n"
        "# Section 5.7: Small Modular Classifier Architecture for 28x28 Images\n"
        "class NeuralNetwork(nn.Module):\n"
        "    def __init__(self):\n"
        "        super().__init__()\n"
        "        self.network = nn.Sequential(\n"
        "            # 784 inputs correspond to 28x28 flattened grayscale pixels\n"
        "            nn.Linear(784, 128),\n"
        "            # Non-linear activation function\n"
        "            nn.ReLU(),\n"
        "            # Output layer: 10 logits corresponding to digit classes 0 to 9\n"
        "            nn.Linear(128, 10)\n"
        "        )\n\n"
        "    def forward(self, x: torch.Tensor) -> torch.Tensor:\n"
        "        return self.network(x)\n\n"
        "# Instantiate model and verify tensor dimensions with a synthetic batch\n"
        "model = NeuralNetwork()\n"
        "# Batch of 1 sample with 784 features\n"
        "sample = torch.randn(1, 784)\n"
        "logits = model(sample)\n\n"
        "print('Logits shape:', logits.shape)  # torch.Size([1, 10])\n"
        "assert logits.shape == (1, 10), f'Unexpected shape: {logits.shape}'\n\n"
        "# Verification of one artificial neuron manual calculation:\n"
        "# Given: x1 = 2, x2 = 3, w1 = 0.5, w2 = 0.8, b = 0.2\n"
        "import math\n"
        "z_calc = (2 * 0.5) + (3 * 0.8) + 0.2  # 1.0 + 2.4 + 0.2 = 3.6\n"
        "sigmoid_calc = 1.0 / (1.0 + math.exp(-z_calc))  # ~0.9734\n"
        "assert round(z_calc, 2) == 3.60\n"
        "assert round(sigmoid_calc, 3) == 0.973"
    )

    code_content = (
        "## 🛠️ Step-by-Step Applied Walkthrough & Coding Lab\n\n"
        "### 1. Hand-Worked Numerical Example of a Single Neuron (Section 5.3)\n"
        "Suppose a single neuron receives two input signals:\n"
        "- Inputs: $x_1 = 2.0, \\quad x_2 = 3.0$\n"
        "- Learnable Weights: $w_1 = 0.5, \\quad w_2 = 0.8$\n"
        "- Learnable Bias: $b = 0.2$\n"
        "- Activation: Sigmoid $\\sigma(z) = \\frac{1}{1 + e^{-z}}$\n\n"
        "**Step 1: Compute the weighted products**\n"
        "- Contribution of $x_1$: $w_1 x_1 = 0.5 \\times 2.0 = 1.0$\n"
        "- Contribution of $x_2$: $w_2 x_2 = 0.8 \\times 3.0 = 2.4$\n\n"
        "**Step 2: Add the bias to obtain $z$**\n"
        "$$z = 1.0 + 2.4 + 0.2 = 3.60$$\n\n"
        "**Step 3: Apply the Sigmoid activation**\n"
        "$$y = \\sigma(3.60) = \\frac{1}{1 + e^{-3.60}} \\approx \\frac{1}{1 + 0.027324} \\approx 0.973$$\n\n"
        "> [!IMPORTANT]\n"
        "> **Calibration Note**: The output of this single neuron is $\\approx 0.973$. It indicates high positive activation, but it is **not** automatically a calibrated 97.3% predictive model confidence.\n\n"
        "### 2. State & Operation Trace Table\n\n"
        "| Operation | Formula | Substituted Values | Intermediate Result |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| Weighted Input 1 | $w_1 x_1$ | $0.5 \\times 2.0$ | $1.0$ |\n"
        "| Weighted Input 2 | $w_2 x_2$ | $0.8 \\times 3.0$ | $2.4$ |\n"
        "| Bias Addition | $w_1 x_1 + w_2 x_2 + b$ | $1.0 + 2.4 + 0.2$ | $z = 3.60$ |\n"
        "| Sigmoid Activation | $\\frac{1}{1 + e^{-z}}$ | $\\frac{1}{1 + e^{-3.60}}$ | **$y \\approx 0.973$** |\n\n"
        "### 3. PyTorch Model Implementation (Section 5.7)\n"
        "The executable PyTorch model below defines the classifier architecture for $28 \\times 28$ handwritten digits with tensor shape verification:\n\n"
        f"```python\n{code_snippet}\n```\n\n"
        "### 🔍 Tensor Dimensions & Architecture Walkthrough\n"
        "- **Input Dimensions**: `(1, 784)` represents 1 sample image of $28 \\times 28$ pixels flattened into a 1D vector.\n"
        "- **Hidden Layer**: `nn.Linear(784, 128)` projects from 784 dimensions to 128 hidden features.\n"
        "- **Non-Linearity**: `nn.ReLU()` applies element-wise $\\max(0, x)$, preserving positive activations while zeroing negatives.\n"
        "- **Output Layer**: `nn.Linear(128, 10)` maps to 10 raw unnormalized prediction scores (logits).\n"
        "> [!NOTE]\n"
        "> In PyTorch, do **not** apply `nn.Softmax` before `nn.CrossEntropyLoss`. `CrossEntropyLoss` automatically combines LogSoftmax and Negative Log-Likelihood loss for numerical stability."
    )

    # Stage F: Visual Framework (Mermaid Diagrams)
    vis_content = (
        "## 📊 Visual Framework: Artificial Neuron & Network Architecture\n\n"
        "### 1. Internal Mechanics of a Single Neuron (Section 5.6)\n\n"
        "```mermaid\n"
        "flowchart LR\n"
        '    X1["Input x1 = 2.0"] -- "w1 = 0.5" --> Sum["Summation: Σ (wi * xi) + b"]\n'
        '    X2["Input x2 = 3.0"] -- "w2 = 0.8" --> Sum\n'
        '    B["Bias b = 0.2"] --> Sum\n'
        '    Sum -- "z = 3.60" --> Act["Activation: f(z) = Sigmoid"]\n'
        '    Act -- "y ≈ 0.973" --> Out["Neuron Output y"]\n'
        "```\n\n"
        "### 2. Multi-Layer Feedforward Network Flow\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        '    subgraph Input_Layer ["Input Layer (784 features)"]\n'
        '        In1["Pixel 1"]\n'
        '        In2["Pixel 2"]\n'
        '        In784["Pixel 784"]\n'
        '    end\n'
        '    subgraph Hidden_Layer ["Hidden Layer (128 Neurons + ReLU)"]\n'
        '        H1["Neuron 1"]\n'
        '        H2["Neuron 2"]\n'
        '        H128["Neuron 128"]\n'
        '    end\n'
        '    subgraph Output_Layer ["Output Layer (10 Logits)"]\n'
        '        O0["Digit 0"]\n'
        '        O1["Digit 1"]\n'
        '        O9["Digit 9"]\n'
        '    end\n'
        '    Input_Layer -->|"Linear(784, 128)"| Hidden_Layer\n'
        '    Hidden_Layer -->|"Linear(128, 10)"| Output_Layer\n'
        "```\n\n"
        "### 🔄 Key Structural Insights\n"
        "- **Information Direction**: Feedforward networks have no backward cycles during inference.\n"
        "- **Parameter Count**: The first linear layer has $784 \\times 128 + 128 = 100,480$ learnable parameters."
    )

    # Stage H & I: Assessment Blueprint, Guided Challenge & Remediation of Misconceptions
    task_content = (
        "## 🎯 Guided Practice Challenge & Targeted Remediation\n\n"
        "### 📋 Independent Guided Practice Task\n"
        "**Task 1**: A single neuron has inputs $x_1 = 1.0, x_2 = -1.0$, weights $w_1 = 2.0, w_2 = 1.5$, and bias $b = -0.5$. "
        "Calculate the pre-activation $z$ and the sigmoid activation $\\sigma(z)$.\n\n"
        "> [!TIP]\n"
        "> **Step-by-Step Hint**:\n"
        "> 1. Calculate $w_1 x_1 = 2.0 \\times 1.0 = 2.0$.\n"
        "> 2. Calculate $w_2 x_2 = 1.5 \\times (-1.0) = -1.5$.\n"
        "> 3. Sum with bias: $z = 2.0 + (-1.5) + (-0.5) = 0.0$.\n"
        "> 4. Sigmoid output: $\\sigma(0.0) = \\frac{1}{1 + e^0} = \\frac{1}{1 + 1} = 0.50$!\n\n"
        "**Task 2 (Tensor Dimensions)**: If your PyTorch input batch contains 32 images (`torch.Size([32, 784])`), "
        "what are the tensor shapes after the first linear layer and the final output layer?\n"
        "- *After Linear(784, 128)*: `torch.Size([32, 128])`\n"
        "- *After Linear(128, 10)*: `torch.Size([32, 10])`\n\n"
        "### 💡 High-Yield University Exam Takeaways\n"
        "1. **Why Activation Functions are Mandatory**: Without non-linear activation functions, stacked linear layers collapse into a single linear transformation ($W_2 W_1 x = W_{net} x$), making deep networks no more expressive than simple linear regression.\n"
        "2. **The Chain Rule in Backpropagation**: Gradients flow backward via $\\frac{\\partial \\mathcal{L}}{\\partial w_i} = \\frac{\\partial \\mathcal{L}}{\\partial y} \\cdot \\frac{\\partial y}{\\partial z} \\cdot \\frac{\\partial z}{\\partial w_i}$.\n"
        "3. **Generalization vs Training Loss**: Low training loss does not guarantee good model performance; always evaluate on held-out validation data to detect overfitting.\n\n"
        "### ⚠️ 5 Critical Exam Misconceptions (Section 5.9 Remediation)\n"
        "| Misconception | Why It Is Flawed | Scientifically Correct Principle |\n"
        "| :--- | :--- | :--- |\n"
        "| **1. 'Weights are fixed constants'** | Weights are NOT static settings. | Weights are learnable parameters continuously updated by the optimizer via gradient descent. |\n"
        "| **2. 'Bias is just another input'** | Bias has no associated sensor or input signal. | Bias is an independent learnable threshold that shifts the linear sum even when all inputs are 0 ($z = b$ when $x = 0$). |\n"
        "| **3. 'Sigmoid output = calibrated probability'** | Sigmoid produces a scalar in $(0, 1)$, but may be uncalibrated. | Sigmoid squashes activations into $(0, 1)$, but calibration techniques (e.g. Platt scaling) are required before interpreting it as true confidence. |\n"
        "| **4. 'Backprop updates the weights'** | Backpropagation does NOT update parameters. | Backpropagation only **calculates gradients** using the chain rule. The **optimizer** (SGD, Adam) updates the weights. |\n"
        "| **5. 'Layers can have arbitrary sizes without shape matching'** | Matrix dimensions must match for multiplication. | The output features of layer $L$ must exactly equal the input features of layer $L+1$ (`Linear(784, 128)` must connect to `Linear(128, 10)`). |"
    )

    blocks = [
        LessonBlock(type=LessonBlockType.OBJECTIVE, title=f"Curiosity Trigger & Outcomes: {clean_topic}", content=obj_content),
        LessonBlock(type=LessonBlockType.EXPLANATION, title="Conceptual Masterclass: Artificial Neurons & Deep Networks", content=expl_content),
        LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title="Worked Example & PyTorch Coding Lab: Single Neuron to Digit Classifier", content=code_content, code=code_snippet, language="python"),
        LessonBlock(type=LessonBlockType.VISUAL_SPEC, title="Visual Framework: Neuron & Network Architecture", content=vis_content),
        LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=f"Guided Practice Challenge & Exam Takeaways: {clean_topic}", content=task_content),
    ]

    return GeneratedLesson(
        context_id=context_id,
        topic=clean_topic,
        pedagogy_decision=_make_pedagogy(),
        blocks=blocks,
        prerequisites=["Python Basics", "Algebraic Equations", "Vectors"],
        assessment_intent=AssessmentIntent(
            target_concepts=["Artificial Neuron", "Weighted Sum", "Activation Functions", "PyTorch Classifier", "Backpropagation"],
            assessment_mode="formative",
            difficulty="beginner",
            question_count=5,
            evaluation_criteria=["Neuron Mathematics", "Activation Characteristics", "Tensor Dimensionality", "Training Dynamics"],
        ),
        next_action=NextLearningAction(
            action_type="practice",
            target_topic="Convolutional Neural Networks (CNN)",
            rationale="Extend feedforward networks to spatial 2D image processing with convolutional filters.",
            urgency="normal",
        ),
    )
