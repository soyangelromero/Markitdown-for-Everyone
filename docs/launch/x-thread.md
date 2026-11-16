# X/Twitter thread drafts

## English

1/ I built a small open-source CLI that turns **scanned PDFs and images into Markdown** using
MarkItDown + a free Pollinations API key. OCR included, no GPU, no Docker, MIT.

Demo: https://github.com/soyangelromero/Markitdown-for-Everyone/blob/main/docs/demo.gif

2/ Why another converter? Zero setup: one command, one free key. Scanned pages are OCR'd page
by page through a vision model. In my tests a 1-page scan cost ~0.0003 pollen.

3/ It also has a bilingual EN/ES menu, non-interactive flags for scripts, a live model catalog
(free vs paid) and clear 401/402/429 messages.

4/ Install today:

```bash
uvx markitdown-for-everyone
```

Repo: https://github.com/soyangelromero/Markitdown-for-Everyone

Feedback on OCR quality and formats is very welcome.

## Español

1/ Hice un CLI open source que convierte **PDFs escaneados e imágenes a Markdown** con
MarkItDown + una clave gratuita de Pollinations. OCR incluido, sin GPU, sin Docker, MIT.

Demo: https://github.com/soyangelromero/Markitdown-for-Everyone/blob/main/docs/demo.gif

2/ ¿Por qué otra herramienta? Configuración cero: un comando y una clave gratuita. Las páginas
escaneadas se procesan con OCR página a página. En mis pruebas, una página costó ~0,0003 pollen.

3/ Además: menú bilingüe ES/EN, flags para automatizar, catálogo de modelos (gratis/pago) y
mensajes claros de error (401/402/429).

4/ Instalación:

```bash
uvx markitdown-for-everyone
```

Repo: https://github.com/soyangelromero/Markitdown-for-Everyone

Se agradece feedback sobre la calidad del OCR y los formatos que faltan.
