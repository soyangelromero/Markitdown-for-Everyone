# Borradores para Reddit / comunidades en español

Revisa las reglas de autopromoción de cada comunidad. Personaliza el texto y no publiques lo
mismo en todas el mismo día.

## r/programacion / r/PythonES / comunidades de Python en Discord

**Título:** CLI open source para convertir PDFs escaneados a Markdown con OCR y una clave gratuita

**Cuerpo:**

Hice una herramienta pequeña para un problema que me encontraba seguido: PDFs escaneados e
imágenes que hay que pasar a Markdown sin montar un modelo local ni pagar un servicio de OCR.

Envuelve MarkItDown de Microsoft, activa el plugin `markitdown-ocr` y usa Pollinations
(compatible con OpenAI, clave gratuita) como backend. Todo corre en local; al modelo solo se
le envía la imagen o página que necesita OCR. En mis pruebas, una página escaneada costó
aproximadamente 0,0003 pollen.

Incluye interfaz bilingüe español/inglés, menú interactivo, flags para scripts
(`--yes`, `--non-interactive`, `--quiet`), catálogo de modelos con etiquetas de gratis/pago,
licencia MIT y Python 3.10+.

Demo: <https://github.com/soyangelromero/Markitdown-for-Everyone/blob/main/docs/demo.gif>

```bash
uvx markitdown-for-everyone
```

Repo: <https://github.com/soyangelromero/Markitdown-for-Everyone>

No está afiliado a Microsoft. Cualquier comentario sobre el diseño del CLI o los formatos que
faltan se agradece.

## Grupos de IA / automatización (WhatsApp, Telegram, Discord, LinkedIn)

Mensaje corto:

> Compartí una herramienta open source (MIT) que convierte PDFs escaneados, imágenes y
> documentos a Markdown con OCR, usando una clave gratuita de Pollinations. Corre en local,
> no necesita GPU ni Docker y tiene menú en español. Demo y repo:
> <https://github.com/soyangelromero/Markitdown-for-Everyone> — cualquier feedback es bienvenido.
