from tunis_rag.loader import load_file


def test_markdown_and_text_files_are_read(tmp_path):
    (tmp_path / "a.md").write_text("# Titre\n\nBonjour", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Salut", encoding="utf-8")
    section = load_file(tmp_path / "a.md")[0]
    assert section.source == "a.md" and "Bonjour" in section.text
    assert load_file(tmp_path / "b.txt")[0].text == "Salut"
