# Launch kit

Ready-to-edit drafts for announcing Markitdown-for-Everyone. Nothing here is posted
automatically; review the rules of each community before publishing.

## Positioning (one sentence)

> A free, open-source CLI that turns scanned PDFs, images and Office documents into Markdown
> using a Pollinations API key — OCR included, no GPU, English/Spanish.

## Assets

- PyPI: <https://pypi.org/project/markitdown-for-everyone/>
- Demo GIF: [`docs/demo.gif`](../demo.gif)
- Repository: <https://github.com/soyangelromero/Markitdown-for-Everyone>
- Approximate cost from real tests: **0.0002–0.0003 pollen** for a 1-page scanned document
  (two LLM calls: image description + OCR).
- License: MIT.

## Checklist

- [x] Published to PyPI: <https://pypi.org/project/markitdown-for-everyone/> (install with `uvx markitdown-for-everyone` or `pipx install markitdown-for-everyone`).
- [ ] Create the GitHub release and tag (`v0.4.1` or newer).
- [ ] Record/replace `docs/demo.gif` if the UI changed (`python scripts/generate_demo.py`).
- [ ] Publish in this order: GitHub release → X/LinkedIn (ES) → Reddit (EN/ES) → Show HN →
      awesome lists PRs.
- [ ] Reply to comments the same day; feedback is more valuable than stars.
- [ ] Do not repost the same text in many communities the same day; tailor each one.
- [ ] Do not claim Microsoft affiliation; mention it is built on top of MarkItDown.

## Drafts

| File | Channel |
|---|---|
| [`show-hn.md`](show-hn.md) | Hacker News "Show HN" |
| [`reddit-en.md`](reddit-en.md) | r/LocalLLaMA, r/Python, r/opensource |
| [`reddit-es.md`](reddit-es.md) | Comunidades hispanas de Python/IA |
| [`linkedin-es.md`](linkedin-es.md) | LinkedIn (español) |
| [`x-thread.md`](x-thread.md) | X/Twitter thread (EN + ES) |
| [`awesome-lists.md`](awesome-lists.md) | PRs to curated lists |
