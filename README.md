# Semantic Feedback-Enhanced LLM Test Case and Oracle Generation

Replication package for: *A Semantic Feedback-Enhanced LLM Approach for Test
Case and Oracle Generation from Natural Language Requirements.*

A two-agent pipeline: a **generator** produces test cases from NL requirements
(RAG-style baseline, re-implemented from RAGTAG, Arora et al., IEEE RE 2024),
and a **critic** audits them on five dimensions — requirement coverage,
correctness, redundancy, edge-case completeness, oracle consistency — after
which the generator revises its output (feedback loop).

## Key results (35 requirements x 3 runs = 105 paired comparisons, Wilcoxon)

| Metric              | Baseline | +Feedback | p        |
|---------------------|----------|-----------|----------|
| Condition coverage  | 0.856    | 0.923     | < 0.001  |
| Edge-case coverage  | 0.384    | 0.538     | < 0.001  |
| Oracle consistency  | 0.838    | 0.915     | < 0.001  |
| Duplicate pairs     | 0.010    | 0.000     | 0.317 ns |

Ablation (n=35/config): edge-case feedback is the primary driver (edge
coverage 0.494 without it vs. 0.543 with it); coverage feedback is marginal.
Human validation: 95.5% agreement between the automated checklist judge and a
human evaluator (67 verdicts, random sample of 10 requirements).

## Repository structure

    data/raw/requirements_seed.json      35 NL requirements
    data/annotations/conditions.json     per-requirement checklists
    data/annotations/human_answers.json  human validation verdicts
    data/annotations/human_form.md       human validation form (filled)
    outputs/baseline/                    RAG-style baseline (3 runs)
    outputs/feedback/                    feedback-refined (3 runs)
    outputs/eval2/                       checklist scores (210 + 70 records)
    outputs/ablation/                    ablation configurations (2 x 35)
    src/                                 pipeline scripts

## Setup

    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env   # fill in your API key
    export HF_ENDPOINT=https://hf-mirror.com   # only needed in mainland China

Models: generation GLM-4.7-Flash (temperature 0.2), judging GLM-4-Flash
(temperature 0.0). All scripts support resume: re-running skips completed
records.

## Pipeline (execution order)

    python src/baseline.py        # run 3x with RUN_ID = run1/run2/run3
    python src/feedback.py        # feedback refinement, same 3 runs
    python src/extract_conditions.py
    python src/evaluate2.py       # checklist scoring (210 records)
    python src/stats2.py          # main results table (Table 1)
    python src/ablation.py && python src/add_req.py
    python src/score_ablation.py  # ablation scoring (70 records)
    python src/stats_ablation.py  # ablation table (Table 2)
    python src/agreement.py       # human-vs-judge agreement (95.5%)
