from __future__ import annotations

import unittest

from experiments.representation_analysis.diagnostics import possible_unsupported_surface_values, retention_diagnostics
from experiments.representation_analysis.gliner_adapter import GlinerEventExtractor
from experiments.representation_analysis.serializers import serialize_events


class FakeGliner:
    def extract_json(self, source, schema, **kwargs):
        return {"cyber_event": [{"actor": {"text": "APT29", "start": 0, "end": 5, "confidence": 0.9}, "action": {"text": "invented", "confidence": 0.8}, "target": "mail server"}]}


class ContractTests(unittest.TestCase):
    def test_gliner_keeps_only_exact_source_spans(self):
        result = GlinerEventExtractor("fake", "cpu", model=FakeGliner()).extract("APT29 targeted the mail server")
        self.assertTrue(result["extraction_success"])
        self.assertEqual(result["events"][0]["actor"]["text"], "APT29")
        self.assertEqual(result["events"][0]["target"]["text"], "mail server")
        self.assertNotIn("action", result["events"][0])
        self.assertEqual(serialize_events(result["events"]), "EVENT 1\nActor: APT29\nTarget: mail server")

    def test_retention_and_case_state_diagnostics(self):
        source = "Host 10.0.0.1 used CVE-2024-1234."
        diagnostics = retention_diagnostics(source, "CVE-2024-1234")
        self.assertGreaterEqual(diagnostics["missing"], 1)
        values = possible_unsupported_surface_values(source, {"facts": [{"statement": "invented claim"}]})
        self.assertEqual(values, ["invented claim"])


if __name__ == "__main__":
    unittest.main()
