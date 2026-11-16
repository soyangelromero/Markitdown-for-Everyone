# Show HN draft

**Title (choose one):**

- `Show HN: An open-source CLI that OCRs scanned PDFs into Markdown with a free API key`
- `Show HN: Markitdown-for-Everyone – scanned PDFs to Markdown, no GPU required`

**Body:**

I built a small CLI around Microsoft's MarkItDown because I wanted something that works for
non-technical users and for scanned documents without a local GPU or a paid OCR service.

What it does:

- Converts PDFs, images, DOCX/PPTX/XLSX, HTML, CSV, JSON, EPUB and ZIP to Markdown.
- Uses the `markitdown-ocr` plugin so scanned PDFs are OCR'd page by page through a
  vision-capable model.
- Uses Pollinations (OpenAI-compatible API) as the backend. Key creation is free; in my tests
  a one-page scanned PDF cost about 0.0003 pollen (two small model calls).
- Bilingual UI (English/Spanish), an interactive menu, and `--yes` / `--non-interactive`
  flags for scripts.
- MIT licensed, Python 3.10+, no GPU, no Docker, nothing uploaded to a third-party UI.

Demo: https://github.com/soyangelromero/Markitdown-for-Everyone/blob/main/docs/demo.gif

Install:

```bash
uvx markitdown-for-everyone
# or
pipx install markitdown-for-everyone
```

Repo: https://github.com/soyangelromero/Markitdown-for-Everyone

It is not affiliated with Microsoft; it is an independent wrapper around MarkItDown. I would
love feedback on two things: (1) which formats/models matter most to you, and (2) whether
the interactive menu is useful or just noise for a CLI.

**First comment (post immediately after submitting):**

The part I was missing from other tools was zero setup: one command, one free key, OCR
enabled by default. The trade-off is that OCR quality depends on the selected vision model;
the README documents which models are free and which need paid pollen.
