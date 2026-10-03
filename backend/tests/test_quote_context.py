from __future__ import annotations

from uuid import uuid4

from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import resolve_case_trace
from app.trace.claims import (
    MAX_CONTEXT_CHARS,
    CaseAnalysisClaim,
    CaseQuoteContext,
    CaseSourceCitation,
)
from app.trace.sentences import SentenceIndex, quote_context, sentence_spans
from app.trace.trace import CaseAnalysisTrace

THAI = (
    "ผู้เสียหายได้รับโทรศัพท์จากชายคนหนึ่งที่อ้างว่าเป็นเจ้าหน้าที่ธนาคาร "
    "ชายคนนั้นบอกว่าบัญชีของผู้เสียหายถูกใช้ฟอกเงินและต้องโอนเงินไปตรวจสอบ "
    "ผู้เสียหายจึงโอนเงินจำนวน 52,000 บาทไปยังบัญชีที่ชายคนนั้นแจ้ง "
    "ต่อมาไม่สามารถติดต่อชายคนนั้นได้อีก"
)
ENGLISH = (
    "The victim called the bank. The caller said the account had been frozen. "
    "He asked for a transfer of 52,000 baht to a safe account. The money was gone by noon."
)
MIXED = (
    "ผู้เสียหายได้รับอีเมลจาก support@bank-example.test แจ้งให้ยืนยันบัญชีภายในวันนี้ "
    "จากนั้นผู้เสียหายคลิกลิงก์ https://login.bank-example.test/verify และกรอกรหัสผ่านของตน "
    "ต่อมาพบว่ามีการโอนเงินออกจากบัญชีโดยไม่ได้รับอนุญาต"
)
OCR_PAGE = (
    "## รายการโอนเงิน\n"
    "<table><tr><th>วันที่</th><th>บัญชีปลายทาง</th><th>จำนวนเงิน</th></tr>"
    "<tr><td>3 มีนาคม 2569</td><td>123-4-56789</td><td>52,000 บาท</td></tr></table>\n"
    "<page_number>2</page_number>"
)


def context_of(text: str, quote: str) -> CaseQuoteContext | None:
    return quote_context(SentenceIndex(text), quote)


def shown(text: str, quote: str) -> str:
    context = context_of(text, quote)
    assert context is not None
    return context.before + quote + context.after


def sentence_at(text: str, position: int) -> tuple[int, int]:
    return next(span for span in sentence_spans(text) if span[0] <= position < span[1])


def test_a_thai_quote_shows_its_sentence_and_the_one_before_it():
    quote = "โอนเงินจำนวน 52,000 บาท"
    start = THAI.index(quote)
    spans = sentence_spans(THAI)
    sentence = sentence_at(THAI, start)
    previous = spans[spans.index(sentence) - 1]

    context = context_of(THAI, quote)

    assert len(spans) >= 3
    assert context == CaseQuoteContext(
        before=THAI[previous[0] : start], after=THAI[start + len(quote) : sentence[1]]
    )
    assert len(shown(THAI, quote)) < len(THAI)


def test_an_english_quote_shows_its_sentence_and_the_one_before_it():
    assert context_of(ENGLISH, "a transfer of 52,000 baht") == CaseQuoteContext(
        before="The caller said the account had been frozen. He asked for ",
        after=" to a safe account.",
    )


def test_a_mixed_quote_keeps_the_address_whole():
    quote = "https://login.bank-example.test/verify"
    start = MIXED.index(quote)

    text = shown(MIXED, quote)

    assert text in MIXED
    assert text.endswith(MIXED[start : sentence_at(MIXED, start)[1]])
    assert "support@bank-example.test" in text


def test_a_quote_at_the_start_of_the_document_has_nothing_before_it():
    context = context_of(THAI, "ผู้เสียหายได้รับโทรศัพท์")

    assert context is not None
    assert (context.before, context.cut_before) == ("", False)
    assert context.after.startswith("จากชายคนหนึ่ง")


def test_a_quote_across_two_sentences_shows_both_whole():
    assert context_of(ENGLISH, "frozen. He asked") == CaseQuoteContext(
        before="The victim called the bank. The caller said the account had been ",
        after=" for a transfer of 52,000 baht to a safe account.",
    )


def test_a_quote_inside_an_ocr_table_is_cut_from_the_same_text():
    context = context_of(OCR_PAGE, "123-4-56789")

    assert context is not None
    assert context.before.endswith("<td>3 มีนาคม 2569</td><td>")
    assert context.after == "</td><td>52,000 บาท</td></tr></table>"
    assert context.before + "123-4-56789" + context.after in OCR_PAGE


def test_a_long_sentence_is_trimmed_on_both_sides_and_says_so():
    quote = "ACCOUNT-123-4-56789"
    text = "x" * 600 + quote + "y" * 600

    context = context_of(text, quote)

    assert context == CaseQuoteContext(
        before="x" * 200, after="y" * 200, cut_before=True, cut_after=True
    )
    assert len(context.before) + len(context.after) <= MAX_CONTEXT_CHARS


def test_the_sentence_before_is_left_out_when_it_would_pass_the_limit():
    quote = "ACCOUNT-123-4-56789"
    text = "a" * 300 + "\n" + "b" * 50 + quote + "c" * 100

    assert context_of(text, quote) == CaseQuoteContext(before="b" * 50, after="c" * 100)


def test_a_quote_found_twice_gets_no_context():
    assert (
        context_of("Then the money was sent. Later the money was sent again.", "the money was sent")
        is None
    )


def bundle_of(*texts: str) -> tuple[CaseSourceBundle, list[str]]:
    sources = tuple(
        CaseSourceItem(source_id=str(uuid4()), source_kind="narrative", text=text) for text in texts
    )
    return CaseSourceBundle(revision=1, sources=sources), [source.source_id for source in sources]


def bound(source_id: str, quote: str, bundle: CaseSourceBundle) -> list[CaseSourceCitation]:
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="The victim lost money.",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="The victim was asked to move money.",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[CaseSourceCitation(source_id=source_id, exact_quote=quote)],
            )
        ],
    )
    return resolve_case_trace(trace, bundle).claims[0].supporting_citations


def test_the_binder_stores_the_context_with_the_citation():
    bundle, [source_id] = bundle_of(ENGLISH)

    [citation] = bound(source_id, "a transfer of 52,000 baht", bundle)

    assert citation.context == context_of(ENGLISH, "a transfer of 52,000 baht")


def test_each_piece_of_a_gapped_quote_gets_its_own_context():
    bundle, [source_id] = bundle_of(ENGLISH)

    citations = bound(
        source_id, "the account had been frozen ... a transfer of 52,000 baht", bundle
    )

    assert [(c.exact_quote, c.context) for c in citations] == [
        (
            "the account had been frozen",
            CaseQuoteContext(before="The victim called the bank. The caller said ", after="."),
        ),
        (
            "a transfer of 52,000 baht",
            CaseQuoteContext(
                before="The caller said the account had been frozen. He asked for ",
                after=" to a safe account.",
            ),
        ),
    ]


def test_a_stored_citation_without_a_context_still_reads():
    stored = {"source_id": "S1", "exact_quote": "the money was gone"}

    claim = CaseAnalysisClaim.model_validate(
        {
            "claim_id": "A-01",
            "claim_type": "reported",
            "text": "The money was gone.",
            "epistemic_status": "reported",
            "supporting_citations": [stored],
        }
    )

    assert claim.supporting_citations[0].context is None


def test_a_stored_context_that_no_longer_fits_is_dropped_not_refused():
    stored = {
        "source_id": "S1",
        "exact_quote": "the money was gone",
        "context": {"before": "x" * (MAX_CONTEXT_CHARS + 1), "after": ""},
    }

    claim = CaseAnalysisClaim.model_validate(
        {
            "claim_id": "A-01",
            "claim_type": "reported",
            "text": "The money was gone.",
            "epistemic_status": "reported",
            "supporting_citations": [stored],
        }
    )

    assert claim.supporting_citations[0].exact_quote == "the money was gone"
    assert claim.supporting_citations[0].context is None


def test_a_bound_trace_keeps_its_contexts_when_stored_and_read_back():
    bundle, [source_id] = bundle_of(THAI)
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="ผู้เสียหายถูกหลอกให้โอนเงิน",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="ผู้เสียหายโอนเงิน 52,000 บาท",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[
                    CaseSourceCitation(source_id=source_id, exact_quote="โอนเงินจำนวน 52,000 บาท")
                ],
            )
        ],
    )
    resolved = resolve_case_trace(trace, bundle)

    read_back = CaseAnalysisTrace.model_validate(resolved.model_dump(mode="json"))

    assert read_back.claims[0].supporting_citations[0].context is not None
    assert read_back.claims == resolved.claims
