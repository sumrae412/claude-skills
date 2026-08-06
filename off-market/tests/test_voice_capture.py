"""Tests for voice sample summarizer."""

from scripts.voice_capture import summarize_samples


def test_summarize_samples_basic_stats():
    samples = ["The quick brown fox jumps over the lazy dog.", "Quick foxes jump."]
    s = summarize_samples(samples)
    assert s["sample_count"] == 2
    assert s["total_words"] > 0
    assert s["avg_sentence_length_words"] > 0


def test_summarize_samples_top_content_words_excludes_stopwords():
    samples = ["The cat sat on the mat. The cat was happy. The cat slept."]
    s = summarize_samples(samples)
    top_words = [w for w, _ in s["top_content_words"]]
    assert "the" not in top_words
    assert "cat" in top_words  # most frequent content word


def test_summarize_samples_openers_and_closers():
    samples = ["Hello there, this is my first sample paragraph. It has things to say."]
    s = summarize_samples(samples)
    assert len(s["sample_openers"]) == 1
    assert s["sample_openers"][0].lower().startswith("hello")


def test_summarize_samples_empty_input():
    s = summarize_samples([])
    assert s["sample_count"] == 0
    assert s["total_words"] == 0


def test_summarize_samples_multi_sentence_average():
    samples = ["A. " * 5]  # 5 sentences of one word each
    s = summarize_samples(samples)
    assert s["avg_sentence_length_words"] == 1.0


def test_summarize_samples_long_paragraph_truncates_opener_to_6_words():
    samples = ["one two three four five six seven eight nine ten."]
    s = summarize_samples(samples)
    assert len(s["sample_openers"][0].split()) == 6
