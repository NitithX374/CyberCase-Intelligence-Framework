from __future__ import annotations

import unittest

from experiments.context_refinement.prompting import (
    build_condition_prompt,
    validate_context_only_prompt_change,
)
from experiments.context_refinement.protected_spans import compare_protected_spans


class PromptAndSpanTests(unittest.TestCase):
    def test_prompt_changes_only_context(self) -> None:
        row = {
            "id": 1,
            "category": "Threat Analysis",
            "task": "test-en-gen",
            "instruction": "Analyze the incident.",
            "input": "raw context",
            "output": "gold",
        }
        raw = build_condition_prompt(row, "raw context")
        refined = build_condition_prompt(row, "compressed context")
        validate_context_only_prompt_change(row, "raw context", "compressed context")
        self.assertNotEqual(raw, refined)
        self.assertEqual(raw.replace("raw context", "compressed context"), refined)

    def test_protected_span_diagnostics_are_explicit(self) -> None:
        raw = (
            "Connect to 10.2.3.4 and https://evil.example/path. "
            "Hash aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, CVE-2024-1234, T1059.001, "
            "C:\\Windows\\Temp\\drop.exe. powershell.exe -enc AAAA\n"
            "account=alice at 2026-08-23T12:34:56Z."
        )
        refined = "Connect to 10.2.3.4 and CVE-2024-1234."
        result = compare_protected_spans(raw, refined)
        self.assertGreater(result["total"], 5)
        self.assertGreater(result["preserved"], 1)
        self.assertGreater(result["missing"], 1)
        self.assertIn("ipv4", result["by_type"])
        self.assertIn("cve", result["by_type"])


if __name__ == "__main__":
    unittest.main()

