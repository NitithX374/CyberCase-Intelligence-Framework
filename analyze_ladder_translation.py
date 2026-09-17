#!/usr/bin/env python3
"""
Root entrypoint redirecting to experiments/ladder_translation_quality/analyze_ladder_translation.py
"""
import sys
from pathlib import Path

exp_dir = Path(__file__).parent / "experiments" / "ladder_translation_quality"
sys.path.insert(0, str(exp_dir))

from analyze_ladder_translation import main

if __name__ == "__main__":
    main()
