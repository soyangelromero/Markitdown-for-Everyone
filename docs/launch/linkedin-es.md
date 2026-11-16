# LinkedIn (español)

**Título del post:**

De PDFs escaneados a Markdown en un comando (open source, OCR incluido)

**Cuerpo:**

Durante los últimos días estuve puliendo una herramienta que empecé hace unos meses:
**Markitdown-for-Everyone**, un CLI open source (MIT) que convierte PDFs, imágenes,
documentos de Office y otros formatos a Markdown.

Lo que la hace distinta para mi caso de uso:

- **OCR de PDFs escaneados** con el plugin `markitdown-ocr`, sin GPU ni Docker.
- **Clave gratuita de Pollinations** como backend (compatible con OpenAI). En mis pruebas,
  una página escaneada costó ~0,0003 pollen.
- **Interfaz bilingüe** español/inglés, con menú interactivo y flags para automatizar.
- Catálogo de modelos en vivo que indica cuáles son gratis y cuáles requieren pollen de pago.
- Todo local: los archivos no se suben a una web de terceros.

Demo (GIF) y código:
https://github.com/soyangelromero/Markitdown-for-Everyone

No está afiliado a Microsoft; es un proyecto independiente sobre MarkItDown.

Si trabajas con documentos escaneados, archivos de oficina o automatización de datos, me
gustaría saber qué formato o flujo te falta. Los issues y las estrellas ayudan a que más gente
lo encuentre, pero sobre todo me interesa el feedback de uso real.

#OpenSource #Python #OCR #Markdown #Automatización #IA #Documentos
