#!/usr/bin/env bash
# PaddleOCR segfaults on some pages (exit 139, no traceback). The worker names
# the page it is about to read in a sentinel file; when it dies, that page is
# recorded as crashed so the next pass moves past it instead of dying again.
#
# No pipeline around the worker: `| grep || true` resets PIPESTATUS and the
# crash is then invisible.
cd "$(dirname "$0")"
PY=../../../env_mitre/Scripts/python.exe
mkdir -p logs
for attempt in $(seq 1 240); do
  before=$(wc -l < predictions/paddle.jsonl 2>/dev/null || echo 0)
  if [ "$before" -ge 197 ]; then echo "done: $before rows"; break; fi
  PYTHONIOENCODING=utf-8 $PY run_engine.py --engine paddle > "logs/paddle_pass_$attempt.log" 2>&1
  status=$?
  after=$(wc -l < predictions/paddle.jsonl 2>/dev/null || echo 0)
  echo "pass $attempt: exit=$status rows $before -> $after"
  if [ "$status" -ne 0 ]; then
    PYTHONIOENCODING=utf-8 $PY run_engine.py --engine paddle --mark-crashed
  fi
  if [ "$after" -le "$before" ] && [ "$status" -eq 0 ]; then
    echo "clean exit with no new rows, stopping at $after"; break
  fi
done
