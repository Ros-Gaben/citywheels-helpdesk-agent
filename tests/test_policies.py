import pytest

from citywheels.policies import get_keywords
from citywheels.policies import load_policy_sections, search_policies


def test_load_policy_sections():
    sections = load_policy_sections()
    titles = [section["title"] for section in sections]
    assert "Cancelling a booking" in titles
    assert "When are you open?" in titles
    assert "Late return" in titles
    assert "Prices" in titles

    for section in sections:
        assert section["source"].endswith(".md")
        assert section["text"] != ""



@pytest.mark.parametrize("text, expected_title", 
    [
        ("Can I cancel my booking?", "Cancelling a booking"),
        ("What are your opening hours?", "When are you open?"),
        ("What happens if there is a storm?", "Bad weather"),
        ("Do I have to wear a helmet?", "Do I have to wear a helmet?"),
        ("How much is the late return fee?", "Late return"),
        ("Do you sell bikes?", "Do you sell bikes?"),
        ("Do prices include VAT?", "Prices"),
    ],
)
def test_search_find_correct_section_first(text, expected_title):
    result = search_policies(text)
    assert result["found"] == True
    assert result["results"][0]["title"] == expected_title

def test_search_question_age_limits_among_results():
    result = search_policies("Can my 14 year old rent an e-bike?")
    titles = [section["title"] for section in result["results"]]
    assert "Are there age limits?" in titles

def test_search_returns_at_most_top_results():
    result = search_policies("bike", top=2)
    assert len(result["results"]) <= 2

@pytest.mark.parametrize("text", ["What is the capital of Australia?", "", "   ", None])
def test_search_nothing_found(text):
    result = search_policies(text)
    assert result["found"] == False
    assert result["results"] == []


def test_get_keywords_keeps_negation():
    assert "no" in get_keywords("no bikes")

def test_prices_intro_vat_isnt_lost():
    sections = load_policy_sections()
    prices_texts = [section["text"] for section in sections if section["title"] == "Prices"]
    assert "VAT" in prices_texts[0]
    assert "EUR" in prices_texts[0]


def test_search_policies_finds_location_question():
    result = search_policies("Where are you?")

    assert result["found"] is True
    assert any(section["source"] == "faq.md" for section in result["results"])