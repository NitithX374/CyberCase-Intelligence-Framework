from __future__ import annotations

import pytest

from app.trace.quote_binding import tolerated_in
from app.trace.quotes import (
    find_aligned_quote,
    find_format_only_quote,
    find_relaxed_quote,
    format_form,
    locate_quote,
)

PAID = "The accountant paid {} baht to the vendor on Monday."


def located(source: str, quote: str) -> str | None:
    spans = find_aligned_quote(source, quote)
    return None if spans is None else " | ".join(source[start:end] for start, end in spans)


def tier(source: str, quote: str) -> str | None:
    found = locate_quote(source, quote)
    return None if found is None else found.tier


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        (PAID.format("-5,000"), "paid 5,000 baht"),
        (PAID.format("5,000"), "paid -5,000 baht"),
        (PAID.format("−5,000"), "paid 5,000 baht"),
        (PAID.format("5,000"), "paid −5,000 baht"),
        (PAID.format("–5,000"), "paid 5,000 baht"),
        ("The balance changed by (-5) points overall.", "changed by (5) points overall"),
        ("The balance changed by (5) points overall.", "changed by (-5) points overall"),
    ],
)
def test_a_minus_sign_is_never_dropped_and_never_added(source, quote):
    assert located(source, quote) is None


@pytest.mark.parametrize(
    ("source", "quote", "stored"),
    [
        (PAID.format("-5,000"), "paid −5,000 baht", "paid -5,000 baht"),
        (PAID.format("−5,000"), "paid -5,000 baht", "paid −5,000 baht"),
        ("The intrusion lasted 5-10 days in total.", "lasted 5–10 days", "lasted 5-10 days"),
        ("The intrusion lasted 5–10 days in total.", "lasted 5-10 days", "lasted 5–10 days"),
    ],
)
def test_the_style_of_a_dash_still_folds_when_it_is_a_sign_or_between_digits(source, quote, stored):
    assert located(source, quote) == stored


@pytest.mark.parametrize(
    ("source", "quote", "shown"),
    [
        (
            "We must re-sign the lease today.",
            "must resign the lease today",
            [("resign", "re-sign")],
        ),
        (
            "We must resign the lease today.",
            "must re-sign the lease today",
            [("re-sign", "resign")],
        ),
        (
            "Send the e-mail to the whole department.",
            "Send the email to the whole department",
            [("email", "e-mail")],
        ),
        (
            "Send the email to the whole department.",
            "Send the e-mail to the whole department",
            [("e-mail", "email")],
        ),
        (
            "A well-known actor joined the board today.",
            "A wellknown actor joined the board today",
            [("wellknown", "well-known")],
        ),
    ],
)
def test_a_hyphen_between_letters_is_still_dropped_and_shown(source, quote, shown):
    assert tier(source, quote) == "format"
    assert [(d.written, d.source) for d in tolerated_in(source, quote)] == shown


@pytest.mark.parametrize(
    ("source", "quote", "stored"),
    [
        (
            "Send the e-mail to the whole department.",
            "Send the e–mail to the whole department",
            "Send the e-mail to the whole department",
        ),
        (
            "Send the e—mail to the whole department.",
            "Send the e-mail to the whole department",
            "Send the e—mail to the whole department",
        ),
        (
            "We must re-sign the lease today, they said.",
            "We must re-sign the lease today they said",
            "We must re-sign the lease today, they said",
        ),
    ],
)
def test_the_style_of_a_hyphen_between_letters_still_folds(source, quote, stored):
    assert located(source, quote) == stored


THERAPIST = "Our therapist said so after the meeting."
THE_RAPIST = "Our the rapist said so after the meeting."


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        (THERAPIST, THE_RAPIST.rstrip(".")),
        (THE_RAPIST, THERAPIST.rstrip(".")),
        ("Our **therapist** said so after the meeting.", THE_RAPIST.rstrip(".")),
        ("Our **the rapist** said so after the meeting.", THERAPIST.rstrip(".")),
        ("Our therapist, said so after the meeting.", "Our the rapist said so after the meeting"),
    ],
)
def test_a_word_boundary_between_latin_letters_is_never_dropped_and_never_added(source, quote):
    assert located(source, quote) is None
    assert find_relaxed_quote(source, quote) is None
    assert find_format_only_quote(source, quote) is None


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        ("Room 4 02 was entered with a key.", "Room 402 was entered with a key"),
        ("Room 402 was entered with a key.", "Room 4 02 was entered with a key"),
        ("Room 4A was entered with a key today.", "Room 4 A was entered with a key today"),
        ("The ID is AB 12 on the form today.", "The ID is AB12 on the form today"),
    ],
)
def test_a_boundary_between_a_letter_and_a_digit_is_kept_too(source, quote):
    assert located(source, quote) is None


@pytest.mark.parametrize(
    "source",
    [
        "Our the rapist said so after the meeting.",
        "Our the  rapist said so after the meeting.",
        "Our the\trapist said so after the meeting.",
        "Our the\nrapist said so after the meeting.",
        "Our the\n\n  rapist said so after the meeting.",
        "Our **the** **rapist** said so after the meeting.",
        "Our the**rapist** said so after the meeting.",
        "Our **the rapist** said so after the meeting.",
    ],
)
def test_any_amount_and_kind_of_space_still_counts_as_the_boundary(source):
    assert located(source, "Our the rapist said so after the meeting") is not None


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        ("Our the rapist said so, after the meeting.", "Our the rapist said so after the meeting"),
        ("Our the rapist said so after the meeting.", "Our the rapist, said so after the meeting"),
        ("Our (the rapist) said so after the meeting.", "Our the rapist said so after the meeting"),
        ("Our the - rapist said so after the meeting.", "Our the rapist said so after the meeting"),
    ],
)
def test_a_boundary_survives_punctuation_between_the_words(source, quote):
    assert located(source, quote) is not None


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        (
            "ผู้เสียหายโอนเงินไปยังบัญชีของคนร้าย จากนั้นติดต่อไม่ได้อีก",
            "ผู้เสียหายโอนเงินไปยังบัญชีของคนร้ายจากนั้นติดต่อไม่ได้อีก",
        ),
        (
            "ผู้เสียหายโอนเงินไปยังบัญชีของคนร้ายจากนั้นติดต่อไม่ได้อีก",
            "ผู้เสียหายโอนเงินไปยังบัญชี ของคนร้าย จากนั้นติดต่อไม่ได้อีก",
        ),
        ("The suspect, นายสมชาย, left at noon today.", "The suspect นายสมชาย left at noon today"),
    ],
)
def test_whitespace_next_to_thai_script_may_still_be_dropped(source, quote):
    assert located(source, quote) is not None


@pytest.mark.parametrize(
    ("source", "quote", "shown"),
    [
        (
            "Apple pays one million baht each month.",
            "apple pays one million baht each month",
            [("apple", "Apple")],
        ),
        (
            "apple pays one million baht each month.",
            "Apple pays one million baht each month",
            [("Apple", "apple")],
        ),
        (
            "They said that Apple pays one million baht.",
            "They said that apple pays one million baht",
            [("apple", "Apple")],
        ),
        (
            "They said that apple pays one million baht.",
            "They said that Apple pays one million baht",
            [("Apple", "apple")],
        ),
        (
            "Apple pays one million baht each month.",
            "Apple PAYS one million baht each month",
            [("PAYS", "pays")],
        ),
        (
            "SPORTS Direct failed to tell its workers about it.",
            "Sports Direct failed to tell its workers about it",
            [("Sports", "SPORTS")],
        ),
    ],
)
def test_letter_case_still_folds_everywhere_and_is_shown(source, quote, shown):
    assert tier(source, quote) == "format"
    assert [(d.written, d.source) for d in tolerated_in(source, quote)] == shown


@pytest.mark.parametrize(
    ("source", "quote", "stored"),
    [
        (PAID.format("1500000"), "paid 1,500,000 baht", "paid 1500000 baht"),
        (PAID.format("1,500,000"), "paid 1500000 baht", "paid 1,500,000 baht"),
        (PAID.format("5000"), "paid 5,000 baht", "paid 5000 baht"),
        (PAID.format("12,345"), "paid 12345 baht", "paid 12,345 baht"),
    ],
)
def test_a_thousands_comma_is_dropped(source, quote, stored):
    assert tier(source, quote) == "format"
    assert located(source, quote) == stored


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        (PAID.format("15"), "paid 1.5 baht"),
        (PAID.format("1.5"), "paid 15 baht"),
        (PAID.format("1234"), "paid 12,34 baht"),
        (PAID.format("123456"), "paid 12,3456 baht"),
        (PAID.format("1234"), "paid 1,2345 baht"),
        (PAID.format("5000"), "paid $5,000 baht"),
        (PAID.format("10:30"), "paid 1030 baht"),
        (PAID.format("1500000"), "paid 1,500,001 baht"),
    ],
)
def test_only_a_comma_before_exactly_three_digits_is_a_thousands_separator(source, quote):
    assert located(source, quote) is None


def test_a_comma_between_digits_that_is_not_a_group_of_three_is_kept_in_the_form():
    assert format_form("12,34").text == "12,34"
    assert format_form("12,3456").text == "12,3456"
    assert format_form("1,234").text == "1234"
    assert format_form("1,234,567").text == "1234567"
    assert format_form("1,234,5678").text == "1234,5678"


THAI_SENTENCE = "ผู้เสียหายโอนเงิน {} บาทไปยังบัญชีของคนร้าย"


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        (THAI_SENTENCE.format("๘๐๐๐"), THAI_SENTENCE.format("8000")),
        (THAI_SENTENCE.format("8000"), THAI_SENTENCE.format("๘๐๐๐")),
        (THAI_SENTENCE.format("๑,๕๐๐,๐๐๐"), THAI_SENTENCE.format("1500000")),
        (THAI_SENTENCE.format("๑๒๓"), THAI_SENTENCE.format("123")),
    ],
)
def test_thai_digits_fold_to_arabic_digits_by_value(source, quote):
    assert tier(source, quote) == "format"


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        (THAI_SENTENCE.format("๘๐๐๐"), THAI_SENTENCE.format("8001")),
        (THAI_SENTENCE.format("๘๐๐๐"), THAI_SENTENCE.format("800")),
        (THAI_SENTENCE.format("8000"), THAI_SENTENCE.format("๘๐๐๑")),
    ],
)
def test_thai_digits_of_another_value_are_refused(source, quote):
    assert located(source, quote) is None


def test_a_thai_digit_is_recorded_as_a_tolerated_difference():
    source = THAI_SENTENCE.format("๘๐๐๐")
    quote = THAI_SENTENCE.format("8000")

    assert [(d.written, d.source) for d in tolerated_in(source, quote)] == [("8000", "๘๐๐๐")]


def test_a_thousands_comma_is_recorded_as_a_tolerated_difference():
    source = PAID.format("1500000")

    shown = tolerated_in(source, "paid 1,500,000 baht")

    assert [(d.written, d.source) for d in shown] == [("1,500,000", "1500000")]


REPEATED = "Then the money was sent. Later the money was sent!"


def test_a_format_form_that_repeats_with_the_same_source_text_is_accepted_at_its_first_place():
    found = locate_quote(REPEATED, '"the money was sent."')

    assert found is not None
    assert found.tier == "format"
    assert found.spans == [(5, 23)]
    assert REPEATED[5:23] == "the money was sent"


def test_a_format_form_that_repeats_with_different_source_texts_is_refused():
    source = "Then the money was sent. Later the money, was sent!"

    assert located(source, '"the money was sent."') is None


def test_a_format_form_that_repeats_with_texts_that_differ_in_case_is_refused():
    source = "Then the money was sent. Later the Money was sent!"

    assert located(source, '"the money was sent."') is None


def test_an_exact_quote_found_twice_is_still_refused_before_the_format_tier_is_tried():
    source = "The money was sent. The money was sent."

    assert locate_quote(source, "The money was sent.") is None


def test_a_short_form_is_still_refused_whatever_its_boundaries():
    source = "The money was sent to an account abroad."

    assert located(source, '"was sent"') is None
    assert find_format_only_quote(source, '"was sent"') is None


def test_the_earlier_tiers_are_untouched_by_the_boundary_rules():
    assert tier("Our therapist said so after the meeting.", "Our therapist said so") == "exact"
    assert tier("The ﬁnal report was signed on Monday.", "The final report was signed") == "folded"
    assert (
        tier(
            "First came the alarm. Then the logs were wiped. Last the backups failed.",
            "First came the alarm ... Last the backups failed",
        )
        == "ellipsis"
    )
