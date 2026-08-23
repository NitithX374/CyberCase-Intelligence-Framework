from __future__ import annotations

import unittest

from experiments.representation_analysis.b3 import build_augmented_context


class B3ContextTests(unittest.TestCase):
    def test_raw_and_events_are_preserved_verbatim(self):
        raw = "APT29 targeted mail.example.com."
        events = "EVENT 1\nActor: APT29\nTarget: mail.example.com"
        context = build_augmented_context(raw, events)
        self.assertIn(raw, context)
        self.assertIn(events, context)
        self.assertLess(context.index(raw), context.index(events))

    def test_empty_extraction_is_explicit(self):
        self.assertIn("(no atomic events extracted)", build_augmented_context("raw", ""))


if __name__ == "__main__":
    unittest.main()
