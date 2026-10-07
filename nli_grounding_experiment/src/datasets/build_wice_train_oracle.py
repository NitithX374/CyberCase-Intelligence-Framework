import json
import random
from copy import deepcopy
from pathlib import Path
import numpy as np

def split_into_chunks(article_sentences: list[str], article_indices: list[int], word_num_in_chunk: int = 256):
    chunks_list: list[list[str]] = []
    sentence_idx_list_of_dict: list[dict] = [{"start": 0}]
    sentence_idx: int = 0
    cur_chunk: list[str] = []
    while True:
        cur_chunk.append(article_sentences[sentence_idx])
        if sentence_idx == len(article_sentences) - 1:
            if len(cur_chunk) > 0:
                chunks_list.append(cur_chunk)
                sentence_idx_list_of_dict[-1]["end"] = sentence_idx
            else:
                sentence_idx_list_of_dict = sentence_idx_list_of_dict[:-1]
            break

        sentence_idx += 1
        cur_chunk_len = sum(len(sent.split()) for sent in cur_chunk)
        if cur_chunk_len >= word_num_in_chunk:
            if len(cur_chunk) == 1:
                sentence_idx_list_of_dict[-1]["end"] = sentence_idx - 1
            else:
                cur_chunk = cur_chunk[:-1]
                sentence_idx_list_of_dict[-1]["end"] = sentence_idx - 2

            chunks_list.append(cur_chunk)
            sentence_idx -= (len(cur_chunk) - 1) // 2
            cur_chunk = []
            sentence_idx_list_of_dict.append({"start": sentence_idx})

    sentence_idx_list = [
        [article_indices[idx] for idx in range(sentence_idx_dict["start"], sentence_idx_dict["end"] + 1, 1)]
        for sentence_idx_dict in sentence_idx_list_of_dict
    ]
    return {"chunks_list": chunks_list, "sentence_idx_list": sentence_idx_list}

def get_chunk_label(article_label: str, supporting_sentences_list: list[list[int]], chunk_idx_list: list[int]) -> str:
    if article_label == "not_supported":
        return "not_supported"

    partially_supported = False
    for supporting_sentences in supporting_sentences_list:
        product_set = set(supporting_sentences).intersection(set(chunk_idx_list))
        if article_label == "supported" and len(product_set) == len(supporting_sentences):
            return "supported"
        if len(product_set) > 0:
            partially_supported = True

    if partially_supported:
        return "partially_supported"
    return "not_supported"

def generate_oracle_chunks(raw_data_list: list[dict], word_num_in_chunk: int = 256) -> list[dict]:
    oracles_output_list: list[dict] = []

    for raw_data in raw_data_list:
        metadata = dict(raw_data["meta"])
        metadata.pop("claim_context", None)
        output_dict = {
            "label": "",
            "claim": raw_data["claim"],
            "evidence": "",
            "meta": metadata,
        }

        if raw_data["label"] == "not_supported":
            chunks = split_into_chunks(
                raw_data["evidence"],
                article_indices=list(range(len(raw_data["evidence"]))),
                word_num_in_chunk=word_num_in_chunk,
            )
            for chunk_id, cnk in enumerate(chunks["chunks_list"]):
                chunks_output_dict = deepcopy(output_dict)
                chunks_output_dict["evidence"] = cnk
                chunk_idx_list = chunks["sentence_idx_list"][chunk_id]
                chunks_output_dict["label"] = "not_supported"
                chunks_output_dict["meta"]["chunk_idx"] = chunk_idx_list
                oracles_output_list.append(chunks_output_dict)
        else:
            num_oracle_chunks_for_this_case = 0
            while num_oracle_chunks_for_this_case <= 3:
                for supporting_sentences in raw_data["supporting_sentences"]:
                    candidate_sentences_added_to_oracle_ = list(
                        set(range(max(supporting_sentences[0] - 15, 0), min(supporting_sentences[-1] + 25, len(raw_data["evidence"])), 1))
                        - set(supporting_sentences)
                    )
                    candidate_sentences_added_to_oracle = random.Random(num_oracle_chunks_for_this_case).sample(
                        candidate_sentences_added_to_oracle_, len(candidate_sentences_added_to_oracle_)
                    )
                    extended_oracle_indices = supporting_sentences + candidate_sentences_added_to_oracle
                    extended_oracle_chunk_list = [raw_data["evidence"][sentence_idx] for sentence_idx in extended_oracle_indices]

                    split_oracle_chunk = split_into_chunks(
                        article_sentences=extended_oracle_chunk_list,
                        article_indices=extended_oracle_indices,
                        word_num_in_chunk=word_num_in_chunk,
                    )

                    original_oracle_evidence = split_oracle_chunk["chunks_list"][0]
                    original_oracle_sentence_idx = split_oracle_chunk["sentence_idx_list"][0]

                    sorted_oracle_evidence = [original_oracle_evidence[idx] for idx in np.argsort(original_oracle_sentence_idx)]
                    sorted_oracle_sentence_idx = sorted(original_oracle_sentence_idx)

                    chunks_output_dict = deepcopy(output_dict)
                    chunks_output_dict["evidence"] = sorted_oracle_evidence
                    chunks_output_dict["meta"]["chunk_idx"] = sorted_oracle_sentence_idx
                    chunks_output_dict["meta"]["oracle_idx"] = supporting_sentences
                    chunks_output_dict["label"] = get_chunk_label(
                        raw_data["label"],
                        supporting_sentences_list=raw_data["supporting_sentences"],
                        chunk_idx_list=chunks_output_dict["meta"]["chunk_idx"],
                    )
                    oracles_output_list.append(chunks_output_dict)
                    num_oracle_chunks_for_this_case += 1

    # Sample up to 3 chunks per claim ID
    oracle_id_to_list: dict[str, list[dict]] = {}
    oracle_id_list: list[str] = []
    for row in oracles_output_list:
        oracle_id_to_list.setdefault(row["meta"]["id"], []).append(row)
        oracle_id_list.append(row["meta"]["id"])

    oracle_id_list = list(dict.fromkeys(oracle_id_list))
    sample_num = 3
    sampled_oracle_list: list[dict] = []
    for oracle_id in oracle_id_list:
        items = oracle_id_to_list[oracle_id]
        if len(items) <= sample_num:
            sampled_oracle_list.extend(items)
        else:
            sampled_oracle_list.extend(random.Random(oracle_id).sample(items, sample_num))

    return sampled_oracle_list

if __name__ == "__main__":
    train_raw_path = Path("nli_grounding_experiment/data/wice/train_raw.jsonl")
    train_out_path = Path("nli_grounding_experiment/data/wice/train.jsonl")

    with open(train_raw_path, "r", encoding="utf-8") as f:
        raw_train = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(raw_train)} raw train examples. Generating oracle chunks...")
    train_oracle = generate_oracle_chunks(raw_train)
    print(f"Generated {len(train_oracle)} train oracle chunks across {len(set(r['meta']['id'] for r in train_oracle))} unique claim IDs.")

    with open(train_out_path, "w", encoding="utf-8") as f:
        for r in train_oracle:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote to {train_out_path} ({train_out_path.stat().st_size} bytes)")
