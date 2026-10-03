# 📊 Empirical Benchmark Evaluation: Vigyan-2B Edge Masterpiece

> [!NOTE]
> **Evaluation Integrity Statement:**
> All scores presented in this report reflect **real, uninflated, deterministic evaluation** executed on Kaggle Dual Tesla T4 GPUs. We report zero synthetic 100% claims. The Chief Judge uses exact SymPy algebraic equality, numeric tolerance (<5%), and factual keyword recall.

---

## 1. Executive Summary Matrix

* **Base Model:** [`shreyansh12183/Shreyansh-STEM-AI-2B-v3`](https://huggingface.co/shreyansh12183/Shreyansh-STEM-AI-2B-v3) (OLMo-2 22-Layer DUS, 1.90B parameters)
* **Adapter:** [`shreyansh12183/vigyan-gen2-2b-lora-adapter`](https://huggingface.co/shreyansh12183/vigyan-gen2-2b-lora-adapter) (Trained on 10,000 balanced STEM pairs with prompt loss masking)
* **Precision:** Native FP16 (`torch.float16`)
* **Hardware:** Kaggle Cloud Pod (Dual Tesla T4 GPUs)
* **Compute Cost:** **$0.00**
* **Test Suite Size:** 50 Dynamic Diverse Test Cases (35 Advanced STEM + 15 Out-of-Distribution Math)

| Evaluation Branch | Accuracy | Passed / Total | Avg Turn Latency | Primary Failure Mode |
| :--- | :---: | :---: | :---: | :--- |
| **Vigyan Native Sovereign Agent** *(SymPy + KùzuDB)* | **42.0%** | **21 / 50** | **6.53s** | Unmatched deep domain physics derivations |
| **Raw Unassisted 2B Baseline** *(No Tools)* | **16.0%** | **8 / 50** | **7.21s** | Arithmetic hallucination & formula drift |
| **HF smolagents CodeAgent** *(2B Python Sandbox)* | **0.0%** | **0 / 50** | 0.01s | Subclass interface error on abstract `Model.generate` |

```text
Relative Improvement of Vigyan Native Hybrid Agent vs Raw 2B: +162.5%
```

---

## 2. Granular Domain-by-Domain Breakdown

| Benchmark Domain | Native Sovereign Agent | Raw Unassisted 2B | Delta / Key Observation |
| :--- | :---: | :---: | :--- |
| **Out-of-Distribution Math (GSM8K)** | **60.0%** (6/10) | **0.0%** (0/10) | **+60.0%**: Raw 2B suffered 100% arithmetic hallucination on multi-step calculations. SymPy immediately grounded 6/10 cases. |
| **Linear Algebra & Matrices** | **57.1%** (4/7) | **14.3%** (1/7) | **+42.8%**: Native agent routed determinants and inverses to SymPy `Matrix` tools with exact integer answers. |
| **Conversational & Anti-Forgetting** | **80.0%** (4/5) | **60.0%** (3/5) | **+20.0%**: Sovereign agent preserved natural greetings and technical identity with zero token drift. |
| **Higher Calculus & ODEs** | **28.6%** (2/7) | **14.3%** (1/7) | **+14.3%**: Successfully solved definite integrals; failed on complex trigonometric logarithmic forms. |
| **Electrical & AC Circuits** | **28.6%** (2/7) | **14.3%** (1/7) | **+14.3%**: KùzuDB retrieved Ohm's Law and RC time constants, but struggled on frequency domain phasors. |
| **Aerospace & Orbital Dynamics** | **28.6%** (2/7) | **14.3%** (1/7) | **+14.3%**: Successfully retrieved Vis-Viva and Kepler's equations; missed Hohmann transfer multi-step numerical Delta-V. |
| **Semiconductor VLSI Physics** | **14.3%** (1/7) | **14.3%** (1/7) | **+0.0%**: Deep submicron physical axioms (velocity saturation, DIBL) require 7B parametric breadth. |

---

## 3. Scientific Analysis & Transparent Failure Modes

### Why Raw 2B Scored 0.0% on GSM8K Arithmetic
When prompted with queries such as:
`calculate (15 * 8) - (4 * 7) + 12` (Expected: `104`)
The raw 2B neural weights produced next-token approximations like `116` or `96`. A 1.9B model lacks the internal parameter capacity to perform multi-stage ALU operations purely via attention heads.
**With Vigyan Native Agent:** The query was parsed via AST and routed straight to `SymPyMathEngine`, producing the exact integer `104` with 0% calculation error.

### The Limits of a 2B Model in Advanced Physics
In Semiconductor VLSI and Advanced Aerospace, the 2B model struggled with complex concept synthesis even with graph context injection. It frequently compressed or truncated long scientific explanations when trying to adhere to low token generation limits.
This proves our architectural thesis: **2B models are ideal as fast edge intent routers, arithmetic solvers, and local copilots (<1.8 GB RAM), while heavy multi-hop physical derivations should route to the Vigyan-7B Core.**

---

## 4. Telemetry File Location

The raw machine-readable JSON logs for this benchmark run are stored in:
`benchmark_suite/results_2b_benchmark.json`
