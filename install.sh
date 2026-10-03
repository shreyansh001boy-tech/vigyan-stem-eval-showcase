#!/usr/bin/env bash
set -e

echo "================================================================="
echo "  Vigyan AI: STEM Benchmark & Evaluation Suite Installer"
echo "================================================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Please install Python 3.10+."
    exit 1
fi

echo "[1/3] Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/3] Installing core neuro-symbolic dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[3/3] Running verification test..."
python3 -c "
from core.sympy_engine import SymPyEngine
from core.kuzu_graph import KuzuSTEMGraph
from core.agent import VigyanAgent

math = SymPyEngine()
print('SymPy Test:', math.evaluate('diff(x**3 * exp(x), x)')['result'])
graph = KuzuSTEMGraph()
print('Kuzu Test :', graph.query_multihop_context(['MOSFET'])[:40], '...')
agent = VigyanAgent()
print('Agent Test:', agent.answer('hii')['response'])
print('✓ Vigyan Evaluation Showcase fully operational!')
"

echo "================================================================="
echo "  Setup Complete! Run benchmark with:"
echo "  source .venv/bin/activate && python3 benchmark_suite/run_benchmark.py"
echo "================================================================="
