# Awesome-list PR drafts

PyPI is published (`markitdown-for-everyone`), so these entries can be submitted now; they have a
stable install command (`pipx install markitdown-for-everyone`). Always follow each list's contribution rules and sort
alphabetically where required.

## Candidate lists

| List | Section | Entry |
|---|---|---|
| [awesome-markdown](https://github.com/BubuAnime/awesome-markdown) | Tools | `[markitdown-for-everyone](https://github.com/soyangelromero/Markitdown-for-Everyone) - CLI that converts PDFs, scans and Office documents to Markdown using MarkItDown and Pollinations; includes OCR and a bilingual UI.` |
| [awesome-pdf](https://github.com/awesomelistsio/awesome-pdf) | Converters | `markitdown-for-everyone` — OCR + Markdown conversion for scanned PDFs. |
| [awesome-python-cli](https://github.com/awesome-python-cli/awesome-python-cli) | Document processing | `markitdown-for-everyone` — PDF/image/Office → Markdown CLI with Pollinations. |
| [awesome-ai-tools](https://github.com/ikaijua/awesome-ai-tools) | Document | `markitdown-for-everyone` — local CLI for scanned PDF OCR to Markdown. |
| [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | Open-source apps | only if it fits their app criteria. |

## Suggested PR description

```text
Add markitdown-for-everyone to <section>

markitdown-for-everyone is an MIT-licensed Python CLI that converts PDFs,
images and Office documents to Markdown using Microsoft's MarkItDown and a
free Pollinations API key. It enables the markitdown-ocr plugin for scanned
PDFs, has a bilingual EN/ES interface and works without a GPU or Docker.

Repository: https://github.com/soyangelromero/Markitdown-for-Everyone
Demo: https://github.com/soyangelromero/Markitdown-for-Everyone/blob/main/docs/demo.gif
License: MIT
```

## MarkItDown plugin route

A separate distribution, `markitdown-pollinations`, could register an
`markitdown.plugin` entry point so users of `markitdown --use-plugins` can select
Pollinations as their LLM client. That gives visibility inside the upstream ecosystem
without competing with it. Track it as a future task; do not claim it exists until published.
