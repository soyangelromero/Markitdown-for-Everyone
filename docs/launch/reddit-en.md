# Reddit drafts (English)

Review each subreddit's self-promotion rules first. Adapt tone; do not post the same text
everywhere on the same day.

## r/LocalLLaMA

**Title:** CLI that turns scanned PDFs into Markdown using a free Pollinations key (OCR on top of MarkItDown)

**Body:**

I wrote a small open-source CLI for a use case I kept hitting: scanned PDFs and images that
need to become Markdown, without running a local model or paying an OCR subscription.

It wraps MarkItDown and uses the `markitdown-ocr` plugin with a vision model through
Pollinations (OpenAI-compatible, free key). Everything runs locally; only the image/page that
needs OCR is sent to the model. A one-page scan cost roughly 0.0003 pollen in my tests.

Other bits: bilingual EN/ES UI, interactive menu, `--yes`/`--non-interactive`, live model
catalog that marks free vs paid models, MIT license, Python 3.10+.

Demo GIF: <https://github.com/soyangelromero/Markitdown-for-Everyone/blob/main/docs/demo.gif>

```bash
uvx --from git+https://github.com/soyangelromero/Markitdown-for-Everyone.git markitdown-for-everyone
```

Repo: <https://github.com/soyangelromero/Markitdown-for-Everyone>

Not affiliated with Microsoft. Feedback welcome, especially on OCR quality/model choices.

## r/Python

**Title:** I built a bilingual CLI to convert scanned PDFs to Markdown with a free API key

**Body:**

`markitdown-for-everyone` is a small Python CLI (Python 3.10+) that converts documents to
Markdown using Microsoft's MarkItDown, with the `markitdown-ocr` plugin for scanned PDFs and a
free Pollinations API key as the LLM backend.

It includes an interactive menu for people who do not live in a terminal, and non-interactive
flags (`--yes`, `--quiet`) for automation. The interface is English/Spanish with localized
OCR prompts. MIT licensed.

Repo and demo: <https://github.com/soyangelromero/Markitdown-for-Everyone>

Install (PyPI pending):

```bash
pipx install git+https://github.com/soyangelromero/Markitdown-for-Everyone.git
```

I would appreciate feedback on the CLI design and on packaging.

## r/opensource

**Title:** Open-source CLI: scanned PDF → Markdown with OCR and a free API key (MIT)

**Body:**

I released a small MIT-licensed tool that wraps MarkItDown to make scanned PDFs and images
usable without a paid OCR service. It uses Pollinations for the vision/OCR calls, ships a
bilingual (EN/ES) menu, and works on Windows/macOS/Linux. CI, tests and a changelog are in the
repo.

<https://github.com/soyangelromero/Markitdown-for-Everyone>

Feedback and issues are welcome. If there is a format or workflow you need, tell me and I will
prioritize it.
