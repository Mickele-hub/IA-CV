"""
Tests pour app.services.pdf_extractor et app.services.text_cleaner.
 
Lancer : pytest tests/test_pdf.py -v
"""
 
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.text_cleaner import (
    clean_text,
    collapse_letter_spaced_words,
    clean_repeated_words,
)
 
 
# --------------------------------------------------------
# extract_text_from_pdf
# --------------------------------------------------------
 
def test_extract_text_from_pdf_returns_non_empty_text(harper_russo_pdf_path):
    with open(harper_russo_pdf_path, "rb") as file:
        text = extract_text_from_pdf(file)
 
    assert text
    assert len(text) > 100
 
 
def test_extract_text_from_pdf_contains_candidate_name(harper_russo_pdf_path):
    with open(harper_russo_pdf_path, "rb") as file:
        text = extract_text_from_pdf(file)
 
    # Le nom peut être dédoublé ou séparé sur deux lignes selon
    # la mise en page brute — on vérifie juste la présence des
    # deux mots quelque part dans le texte extrait.
    assert "Harper" in text
    assert "Russo" in text
 
 
# --------------------------------------------------------
# collapse_letter_spaced_words (titres écrits lettre par lettre)
# --------------------------------------------------------
 
def test_collapse_letter_spaced_words_joins_spaced_title():
    raw = "C O N T A C T :\nHarper Russo"
    result = collapse_letter_spaced_words(raw)
 
    assert "CONTACT :" in result
    assert "C O N T A C T" not in result
 
 
def test_collapse_letter_spaced_words_does_not_alter_normal_text():
    raw = "I am a qualified professional with five years of experience."
    result = collapse_letter_spaced_words(raw)
 
    assert result == raw
 
 
def test_collapse_letter_spaced_words_no_false_single_letter_tokens():
    raw = (
        "C O N T A C T :\n"
        "S K I L L S :\n"
        "R E F E R E N C E S :\n"
        "Web Design, Python, communication skills"
    )
    result = collapse_letter_spaced_words(raw)
    tokens = result.replace(",", " ").replace(":", " ").split()
 
    # Ce test couvre spécifiquement le bug rencontré : des
    # lettres isolées ('C', 'R') étaient faussement détectées
    # comme compétences par skill_extractor.
    assert "C" not in tokens
    assert "R" not in tokens
 
 
# --------------------------------------------------------
# clean_repeated_words (mots dupliqués façon 'AndréaAndréaAndréa')
# --------------------------------------------------------
 
def test_clean_repeated_words_collapses_duplicated_name():
    raw = "AndréaAndréaAndréa SanchezSanchezSanchez"
    result = clean_repeated_words(raw)
 
    assert result == "Andréa Sanchez"
 
 
def test_clean_repeated_words_does_not_alter_short_words():
    raw = "Andréa Sanchez is a great communicator"
    result = clean_repeated_words(raw)
 
    assert result == raw
 
 
# --------------------------------------------------------
# clean_text (pipeline complet de nettoyage)
# --------------------------------------------------------
 
def test_clean_text_handles_empty_input():
    assert clean_text("") == ""
    assert clean_text(None) == ""
 
 
def test_clean_text_normalizes_whitespace():
    raw = "Hello    world\n\n\n\nGoodbye"
    result = clean_text(raw)
 
    assert "    " not in result
    assert "\n\n\n" not in result
 