# CTINexus extraction-only benchmark

This isolated benchmark compares the existing production CyberCase extraction runner (E1) with `fastino/gliner2-base-v1` (E2) on the existing CTINexus committed test split. It calls no downstream analysis model and does not modify application, RAG, MITRE, or SEvenLLM code.

The reused CTINexus infrastructure is under `backend/experiments/ctinexus/`. It supplies the fixed test loader, NFKC/casefold/whitespace normalization, exact entity matching, directed endpoint matching, and directed full-triplet matching. The test source is the external checkout at `F:\ctinexus\ctinexus\data\test`; it currently contains 11 English narratives.

E1 invokes `backend.app.services.extraction.extraction_runner.run_baseline_extraction` with the current validated `CaseState` contract and maps only entities and relationships into CTINexus’s common graph. E2 reuses the representation experiment’s GLiNER2 model loader and source-grounding helper. Its schema uses the fixed CTINexus entity-type vocabulary and a generic `subject`, `relation`, `object` span structure. Relation values are not supplied from test gold; they must be extracted as source spans.

Run from the repository root with the project environment and the production key supplied by Doppler:

```powershell
$env:SSLKEYLOGFILE = ''
doppler run -- env_mitre\Scripts\python.exe -m experiments.ctinexus_extraction_benchmark --dataset-dir "F:\ctinexus\ctinexus\data\test" --output-dir "F:\Cybercase Framework\tmp\ctinexus_extraction_only"
```

The runner resumes exact-condition records from `E1_production_predictions.jsonl` and `E2_gliner2_predictions.jsonl`, flushing every record. It writes the dataset manifest, exact run config, per-case evaluations, JSON summary, and Markdown report under the output directory.
