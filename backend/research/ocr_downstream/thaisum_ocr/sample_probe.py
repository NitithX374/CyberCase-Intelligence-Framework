import re, unicodedata
from collections import Counter
import numpy as np, pandas as pd
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords

df = pd.read_csv("F:/ThaiSum/thaisum.csv", encoding="utf-8")
crime = df["type"].fillna("").str.contains("อาชญากรรม") | df["tags"].fillna("").str.contains("อาชญากรรม")
summ = df["summary"].fillna("").str.strip() != ""
blen = df["body"].fillna("").str.len()
el = df[crime & summ & (blen >= 1500) & (blen <= 5000)]
print("crime", int(crime.sum()), "eligible", len(el), "dedup", el["url"].nunique())
import unicodedata
from facts import candidates, category, PROVINCES, ZERO_WIDTH
el = el.sort_values("url").reset_index()
rng = np.random.default_rng(2026)
pick = sorted(rng.choice(len(el), 100, replace=False))
clean = lambda t: ZERO_WIDTH.sub("", unicodedata.normalize("NFC", t))
per = Counter(); zero = 0; anycat = Counter()
for i in pick:
    row = el.iloc[i]
    cands = candidates(clean(row["body"]), clean(row["summary"]))
    cats = Counter(category(c) for c in cands)
    zero += not cands
    for k in ("number", "place", "other"):
        anycat[k] += cats[k] > 0
    per.update(cats)
print("provinces", len(PROVINCES), "articles with no candidate", zero, "articles having a candidate per category", dict(anycat), "candidates total", dict(per))
