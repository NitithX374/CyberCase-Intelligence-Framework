"""Does asking improve the answer, and what does asking cost?

A harness for one question: when a task is stated incompletely, does explicit
sufficiency assessment plus bounded clarification produce a better final answer
than answering straight away. Four arms differ by one step each, so what is
measured is the step rather than four separate systems.

Nothing here imports the production database. The arms are plain functions over
a benchmark sample, which is what lets the same code run over AskBench and over
a CyberCase case.
"""
