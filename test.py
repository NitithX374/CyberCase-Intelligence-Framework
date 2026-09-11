from datasets import load_dataset

ds = load_dataset("typhoon-ai/ThaiOCRBench")

print(ds)
print(ds["test"].features)
print(len(ds["test"]))

full_ocr = ds["test"].filter(
    lambda x: x["Task"] == "Full-page OCR"
)

print("Full-page OCR:", len(full_ocr))

for i in range(3):
    x = full_ocr[i]
    print("=" * 80)
    print("ID:", x["Id"])
    print("Category:", x["category"])
    print("Question:", x["question"])
    print("GT answer:")
    print(x["answer"])
    display(x["image"])