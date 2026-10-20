from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateModel:
    key: str
    model: str
    revision: str
    kind: str
    labels: tuple[str, ...]
    supported_index: int
    language: str


MODELS = {
    "mdeberta": CandidateModel(
        "mdeberta", "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
        "b5113eb38ab63efdd7f280f8c144ea8b13f978ce", "nli",
        ("entailment", "neutral", "contradiction"), 0, "multilingual including Thai",
    ),
    "deberta_small": CandidateModel(
        "deberta_small", "cross-encoder/nli-deberta-v3-small",
        "fa2804872c3b4bd748f38c0185cc85775361e735", "nli",
        ("contradiction", "entailment", "neutral"), 1, "English",
    ),
    "minilm": CandidateModel(
        "minilm", "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli",
        "0a71e92a985b6e1ad1828cf67ce9c459639c1dca", "nli",
        ("entailment", "neutral", "contradiction"), 0, "multilingual including Thai",
    ),
    "minicheck": CandidateModel(
        "minicheck", "lytang/MiniCheck-DeBERTa-v3-Large",
        "2f2d01a54fa022a7ffadb76260e1ea8bc88c82bb", "support_classifier",
        ("unsupported", "supported"), 1, "English",
    ),
    "xlmr": CandidateModel(
        "xlmr", "joeddav/xlm-roberta-large-xnli",
        "b227ee8435ceadfa86dc1368a34254e2838bf242", "nli",
        ("contradiction", "neutral", "entailment"), 2, "multilingual including Thai",
    ),
    "attrscore": CandidateModel(
        "attrscore", "osunlp/attrscore-flan-t5-large",
        "282eb2ab5d537f5badf5fa33008d96abff34607b", "sequence_label_likelihood",
        ("Attributable", "Contradictory", "Extrapolatory"), 0, "English",
    ),
}


ATTRIBUTION_INSTRUCTION = (
    "As an Attribution Validator, your task is to verify whether a given reference can support the given claim. "
    "A claim can be either a plain sentence or a question followed by its answer. "
    "Specifically, your response should clearly indicate the relationship: Attributable, Contradictory or Extrapolatory.\n"
    "A contradictory error occurs when you can infer that the answer contradicts the fact presented in the context, "
    "while an extrapolatory error means that you cannot infer the correctness of the answer based on the information "
    "provided in the context."
)


def metric_rows(rows, supported_label):
    return [
        {**row, "p_entailment": row["p_supported"],
         "nli_argmax": "entailment" if row["class_argmax"] == supported_label else "neutral"}
        for row in rows
    ]
