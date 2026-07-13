from app.services.embedding_service import RulebookIndex

RULES = [
    {"rule_text": "Students may not be charged any fee for seating assignments.", "source_section": "4.2"},
    {"rule_text": "Confiscating food without written parental consent is prohibited.", "source_section": "7.1"},
    {"rule_text": "The examinable syllabus must be published 30 days before the test.", "source_section": "2.5"},
]


def test_best_match_returns_most_relevant_rule():
    index = RulebookIndex()
    index.build(RULES)

    rule, score = index.best_match("Can they charge me money for my seat?")
    assert rule["source_section"] == "4.2"
    assert 0 <= score <= 1


def test_best_match_handles_unrelated_claim_with_low_score():
    index = RulebookIndex()
    index.build(RULES)

    rule, score = index.best_match("What is the capital of France?")
    assert score < 0.5


def test_empty_index_returns_none():
    index = RulebookIndex()
    index.build([])
    assert index.best_match("anything") is None
