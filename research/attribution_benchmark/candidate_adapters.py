import torch
from transformers import AutoModelForSequenceClassification, AutoModelForSeq2SeqLM

from candidate_models import ATTRIBUTION_INSTRUCTION


MAX_LENGTH = 512


def prepare_inputs(tokenizer, spec, rows):
    inputs = []
    lengths = []
    special = tokenizer.num_special_tokens_to_add(pair=spec.kind != "sequence_label_likelihood")
    for index, row in enumerate(rows):
        premise = "\n\n".join(row["references"])
        premise_ids = tokenizer.encode(premise, add_special_tokens=False, verbose=False)
        claim_ids = tokenizer.encode(row["claim"], add_special_tokens=False, verbose=False)
        prefix_tokens = 0
        if spec.kind == "sequence_label_likelihood":
            prefix = ATTRIBUTION_INSTRUCTION + "\n\n Claim: " + row["claim"] + " \n Reference: "
            prefix_ids = tokenizer.encode(prefix, add_special_tokens=False, verbose=False)
            prefix_tokens = len(prefix_ids) - len(claim_ids)
            budget = MAX_LENGTH - special - len(prefix_ids)
        else:
            budget = MAX_LENGTH - special - len(claim_ids)
        if budget < 1:
            raise ValueError(f"Complete claim/prompt cannot fit at {row['id']}: budget={budget}")
        visible = min(len(premise_ids), budget)
        if spec.kind == "sequence_label_likelihood":
            if special != 1 or tokenizer.eos_token_id is None:
                raise ValueError("AttrScore requires the pinned T5 single-EOS input format")
            input_ids = prefix_ids + premise_ids[:visible] + [tokenizer.eos_token_id]
            encoded = {"input_ids": input_ids, "attention_mask": [1] * len(input_ids)}
        else:
            encoded = tokenizer(premise, row["claim"], truncation="only_first", max_length=MAX_LENGTH,
                                return_attention_mask=True, verbose=False)
        expected_length = special + len(claim_ids) + prefix_tokens + visible
        if len(encoded["input_ids"]) != expected_length or expected_length > MAX_LENGTH:
            raise ValueError(f"Input length accounting disagrees at {spec.key}:{index}")
        inputs.append(dict(encoded))
        lengths.append({
            "premise_tokens": len(premise_ids), "claim_tokens": len(claim_ids), "prompt_tokens": prefix_tokens,
            "pair_tokens": len(premise_ids) + len(claim_ids) + prefix_tokens + special,
            "visible_premise_tokens": visible, "removed_premise_tokens": len(premise_ids) - visible,
            "truncated": visible < len(premise_ids), "input_tokens": expected_length,
        })
    return inputs, lengths


class ClassificationAdapter:
    def __init__(self, spec, dtype, device):
        self.model = AutoModelForSequenceClassification.from_pretrained(
            spec.model, revision=spec.revision, local_files_only=True, dtype=dtype
        ).to(device).eval()
        expected = ("0", "1") if spec.kind == "support_classifier" else spec.labels
        actual = tuple(self.model.config.id2label[index].lower() for index in range(len(expected)))
        if actual != expected:
            raise ValueError(f"Checkpoint class order disagrees: {actual} != {expected}")
        self.signature = {"class_score_kind": "native_classification_logits"}

    def predict(self, encoded):
        logits = self.model(**encoded).logits.float()
        return logits, [{} for _ in range(logits.shape[0])]


class SequenceLabelAdapter:
    def __init__(self, spec, tokenizer, dtype, device):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            spec.model, revision=spec.revision, local_files_only=True, dtype=dtype
        ).to(device).eval()
        self.label_ids = [tokenizer.encode(label, add_special_tokens=True) for label in spec.labels]
        if any(ids[-1] != tokenizer.eos_token_id for ids in self.label_ids):
            raise ValueError("Each label must include its EOS token")
        self.signature = {
            "class_score_kind": "sum_autoregressive_label_token_log_probabilities_including_EOS",
            "probability_kind": "softmax_over_three_complete_label_sequence_log_likelihoods",
            "label_token_ids": self.label_ids, "instruction": ATTRIBUTION_INSTRUCTION,
            "scoring_note": "Constrained whole-label likelihood, without length normalization; not greedy generation",
        }

    def predict(self, encoded):
        encoder = self.model.get_encoder()(
            input_ids=encoded["input_ids"], attention_mask=encoded["attention_mask"], return_dict=True
        )
        columns = []
        token_scores = []
        for label_ids in self.label_ids:
            labels = torch.tensor(label_ids, device=self.model.device).unsqueeze(0).expand(encoded["input_ids"].shape[0], -1)
            outputs = self.model(encoder_outputs=encoder, attention_mask=encoded["attention_mask"], labels=labels,
                                 use_cache=False, return_dict=True)
            selected = outputs.logits.float().log_softmax(dim=-1).gather(-1, labels.unsqueeze(-1)).squeeze(-1)
            columns.append(selected.sum(dim=-1))
            token_scores.append(selected.cpu().tolist())
        scores = torch.stack(columns, dim=-1)
        details = [{"label_token_log_probabilities": [values[index] for values in token_scores]}
                   for index in range(scores.shape[0])]
        return scores, details


def load_adapter(spec, tokenizer, dtype, device):
    if spec.kind == "sequence_label_likelihood":
        return SequenceLabelAdapter(spec, tokenizer, dtype, device)
    if spec.kind in {"nli", "support_classifier"}:
        return ClassificationAdapter(spec, dtype, device)
    raise ValueError(f"Unsupported adapter: {spec.kind}")
