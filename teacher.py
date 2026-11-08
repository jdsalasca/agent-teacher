"""teacher.py — convierte una explicación en Markdown a una guía HTML autocontenida.

Diseñado para aprender, no para lucirse: cada guía sale con gancho inicial, idea
central, ejemplos resueltos, errores típicos, práctica de recuperación y una tarea
de transferencia. El estilo visual es "papercraft": papel, cinta y sombras suaves.

Uso:
    python teacher.py leccion.md --salida guia.html \
        --titulo "Sumas de Riemann" --materia "Cálculo Integral" \
        --subtitulo "De la potencia a la energía" --acento "#b4532a" --abrir

Formato del Markdown de entrada:
    # Título
    > Idea central (una sola frase)

    ## Sección
    Texto con **negrita**, *cursiva* y `código`.

    ### Subsección
    - lista
    - otra

    ```python
    print("bloque de código")
    ```

    ::: ejemplo
    Un ejemplo trabajado.
    :::

    ::: error
    El error que hay que evitar.
    :::

    ::: nota
    Un recordatorio.
    :::

    Q: ¿Pregunta de recuperación?
    R: Respuesta que se revela al hacer clic.

    - [x] tarea hecha
    - [ ] tarea pendiente

Requisitos: Python 3.10+. Sin dependencias externas.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import webbrowser
from pathlib import Path

CSS = """
:root {
  --papel: #f7f1e3;
  --hoja: #fffdf7;
  --tinta: #23201c;
  --suave: #6b6357;
  --linea: #e3d9c6;
  --acento: %ACCENTO%;
  --sombra: rgba(60, 45, 20, .18);
  --nota: #fff4c2;
  --error: #ffe3dd;
  --ejemplo: #e3f0f7;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--tinta);
  background-color: var(--papel);
  background-image:
    radial-gradient(circle at 20% 10%, rgba(255,255,255,.55), transparent 40%),
    repeating-linear-gradient(0deg, rgba(0,0,0,.022) 0 1px, transparent 1px 26px),
    repeating-linear-gradient(90deg, rgba(0,0,0,.018) 0 1px, transparent 1px 26px);
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.72;
  font-size: 17.5px;
}
.envoltura { max-width: 860px; margin: 0 auto; padding: 34px 20px 90px; }

.hero { text-align: center; margin-bottom: 26px; position: relative; }
.hero svg { width: 82px; height: 82px; margin-bottom: 6px; }
.kicker {
  font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
  font-size: 11.5px; letter-spacing: .18em; text-transform: uppercase;
  color: var(--suave); margin: 0 0 6px;
}
.hero h1 {
  font-size: clamp(26px, 4.4vw, 40px); line-height: 1.15; margin: 0 0 10px;
  letter-spacing: -.01em;
}
.hero .sub { color: var(--suave); font-style: italic; margin: 0; font-size: 17px; }
.hero .fecha {
  margin-top: 10px; font-size: 12px; color: var(--suave);
  font-family: ui-monospace, Consolas, monospace;
}

.idea {
  background: var(--hoja); border-left: 5px solid var(--acento);
  padding: 16px 20px; border-radius: 10px; margin: 0 0 26px;
  box-shadow: 0 8px 20px -14px var(--sombra);
  font-size: 18.5px;
}

.indice {
  display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
  margin: 0 0 30px;
}
.indice a {
  font-family: ui-sans-serif, system-ui, sans-serif; font-size: 12.5px;
  color: var(--tinta); text-decoration: none; background: var(--hoja);
  border: 1px solid var(--linea); border-radius: 999px; padding: 5px 12px;
  box-shadow: 0 4px 10px -8px var(--sombra);
}
.indice a:hover { border-color: var(--acento); color: var(--acento); }

.tarjeta {
  position: relative; background: var(--hoja);
  border: 1px solid var(--linea); border-radius: 14px;
  padding: 26px 26px 20px; margin: 0 0 30px;
  box-shadow: 0 1px 0 #fff inset, 0 18px 30px -22px var(--sombra);
}
.tarjeta:nth-of-type(odd) { transform: rotate(-.18deg); }
.tarjeta:nth-of-type(even) { transform: rotate(.14deg); }
.tarjeta::before {
  content: ""; position: absolute; top: -9px; left: 50%; transform: translateX(-50%) rotate(-1.5deg);
  width: 92px; height: 20px; background: rgba(226, 205, 150, .55);
  border-left: 1px dashed rgba(120, 100, 60, .35);
  border-right: 1px dashed rgba(120, 100, 60, .35);
}
.tarjeta h2 {
  font-size: 23px; margin: 6px 0 12px; line-height: 1.25;
  padding-bottom: 8px; border-bottom: 2px dotted var(--linea);
}
.tarjeta h2 .num {
  font-family: ui-monospace, Consolas, monospace; font-size: 13px;
  color: #fff; background: var(--acento); border-radius: 6px;
  padding: 2px 8px; margin-right: 10px; vertical-align: 3px;
}
.tarjeta h3 { font-size: 18px; margin: 20px 0 6px; }
p { margin: 0 0 12px; }
ul, ol { margin: 0 0 14px; padding-left: 24px; }
li { margin-bottom: 5px; }
code {
  font-family: ui-monospace, "Cascadia Code", Consolas, monospace; font-size: .88em;
  background: #f1ead9; padding: 1px 5px; border-radius: 5px;
}
pre {
  background: #2b2620; color: #f4eee1; padding: 16px 18px; border-radius: 10px;
  overflow-x: auto; font-size: 14px; line-height: 1.55;
  box-shadow: inset 0 2px 10px rgba(0,0,0,.35);
}
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
blockquote {
  margin: 0 0 14px; padding: 10px 16px; border-left: 4px solid var(--acento);
  background: #fbf6e9; color: #3a352c; font-style: italic; border-radius: 0 8px 8px 0;
}
.bloque { border-radius: 10px; padding: 14px 18px; margin: 16px 0; border: 1px solid var(--linea); }
.bloque .etiqueta {
  display: block; font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase;
  margin-bottom: 4px; color: #6b5a2e;
}
.bloque.ejemplo { background: var(--ejemplo); }
.bloque.error { background: var(--error); }
.bloque.nota { background: var(--nota); }
.bloque.tip { background: #e9f5ea; }
.bloque.tip .etiqueta { color: #2f5b34; }
.bloque.error .etiqueta { color: #8a2f22; }

table {
  width: 100%; border-collapse: collapse; margin: 14px 0 18px;
  font-size: 15.5px; background: #fffdf7;
}
th, td { border-bottom: 1px solid var(--linea); padding: 7px 10px; text-align: left; }
th {
  font-family: ui-sans-serif, system-ui, sans-serif; font-size: 12px;
  letter-spacing: .06em; text-transform: uppercase; color: var(--suave);
  border-bottom: 2px solid var(--acento);
}
td:not(:first-child), th:not(:first-child) { text-align: right; font-variant-numeric: tabular-nums; }

.formula {
  margin: 14px 0; padding: 14px 18px; text-align: center;
  background: #fbf6e9; border: 1px dashed #d9cdb4; border-radius: 10px;
  font-size: 19px; letter-spacing: .01em;
}
.math {
  font-family: "Cambria Math", Cambria, Georgia, serif;
  font-style: italic; padding: 0 2px; white-space: nowrap;
}

/* --- animaciones papercraft --- */
.progreso {
  position: fixed; top: 0; left: 0; height: 3px; width: 0;
  background: var(--acento); z-index: 99; transition: width .12s linear;
}
.revelar { opacity: 0; transform: translateY(14px) rotate(-.2deg); transition: opacity .55s ease, transform .55s ease; }
.revelar.visible { opacity: 1; transform: none; }

.pasos { list-style: none; padding: 0; margin: 16px 0 20px; counter-reset: paso; }
.pasos li {
  position: relative; margin: 0 0 12px; padding: 14px 16px 14px 58px;
  background: #fffdf7; border: 1px solid var(--linea); border-radius: 12px;
  box-shadow: 0 10px 18px -16px var(--sombra);
  opacity: 0; transform: translateX(-10px);
  transition: opacity .5s ease, transform .5s ease;
}
.pasos.visible li { opacity: 1; transform: none; }
.pasos.visible li:nth-child(1) { transition-delay: .05s; }
.pasos.visible li:nth-child(2) { transition-delay: .2s; }
.pasos.visible li:nth-child(3) { transition-delay: .35s; }
.pasos.visible li:nth-child(4) { transition-delay: .5s; }
.pasos.visible li:nth-child(5) { transition-delay: .65s; }
.pasos.visible li:nth-child(6) { transition-delay: .8s; }
.pasos li::before {
  counter-increment: paso; content: counter(paso);
  position: absolute; left: 14px; top: 12px;
  width: 30px; height: 30px; border-radius: 8px;
  background: var(--acento); color: #fffdf7;
  display: grid; place-items: center;
  font-family: ui-monospace, Consolas, monospace; font-size: 14px;
  transform: rotate(-3deg);
}

.enfoques { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; margin: 16px 0 20px; }
.enfoques article {
  background: #fffdf7; border: 1px solid var(--linea); border-radius: 12px;
  padding: 14px 16px; box-shadow: 0 12px 20px -18px var(--sombra);
  transition: transform .18s ease, box-shadow .18s ease;
}
.enfoques article:hover { transform: translateY(-3px) rotate(-.4deg); box-shadow: 0 18px 26px -18px var(--sombra); }
.enfoques article h4 { margin: 0 0 6px; font-size: 15.5px; }
.enfoques article p { margin: 0; font-size: 15px; color: #3a352c; }

@media (prefers-reduced-motion: reduce) {
  .revelar, .pasos li { opacity: 1 !important; transform: none !important; transition: none !important; }
  .progreso { display: none; }
}

/* ===== v2: paleta terracota y tipografía más fina ===== */
:root {
  --papel: #f7f0e6;
  --hoja: #fffdf8;
  --tinta: #241d18;
  --suave: #7b6a5b;
  --linea: #e9dccb;
  --acento: %ACCENTO%;
  --acento-claro: #d98a63;
  --dorado: #c2a25a;
  --sombra: rgba(72, 45, 25, .16);
}
body {
  background-color: var(--papel);
  background-image:
    radial-gradient(1200px 600px at 15% -10%, rgba(255,255,255,.75), transparent 60%),
    radial-gradient(800px 400px at 100% 0%, rgba(217,138,99,.10), transparent 60%),
    repeating-linear-gradient(0deg, rgba(90,60,30,.022) 0 1px, transparent 1px 28px);
  font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif;
  font-size: 18px;
  line-height: 1.75;
}
.hero h1 {
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  font-weight: 600; letter-spacing: -.015em;
}
.hero { margin-bottom: 20px; }
.hero::after {
  content: ""; display: block; width: 120px; height: 2px; margin: 16px auto 0;
  background: linear-gradient(90deg, transparent, var(--dorado), transparent);
}
.kicker { color: var(--acento); letter-spacing: .22em; }
.idea {
  border-left: 4px solid var(--acento);
  background: linear-gradient(180deg, #fffdf8, #fdf7ee);
  font-size: 19.5px; font-style: italic;
}
.tarjeta {
  border-radius: 16px;
  box-shadow: 0 1px 0 #fff inset, 0 22px 38px -26px var(--sombra), 0 2px 6px -4px var(--sombra);
  padding: 30px 32px 24px;
}
.tarjeta h2 {
  font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  font-size: 24px; border-bottom: 1px solid var(--linea);
}
.tarjeta h2 .num {
  background: linear-gradient(180deg, var(--acento), #8f3f22);
  box-shadow: 0 4px 10px -6px rgba(120,50,20,.7);
}
.tarjeta h3 { font-size: 19px; color: #3a2c22; }
blockquote { border-left-color: var(--dorado); background: #fcf7ec; }

/* objetivo y prerequisito */
.objetivo {
  background: linear-gradient(135deg, #8f3f22, var(--acento));
  color: #fff8f0; border: none; border-radius: 14px;
  padding: 18px 22px; margin: 0 0 22px;
  box-shadow: 0 18px 30px -22px rgba(120,50,20,.85);
}
.objetivo .etiqueta { color: #ffd9c2; }
.objetivo p { margin: 0; font-size: 17.5px; }
.prerequisito {
  background: #fdfaf3; border: 1px dashed var(--dorado); border-radius: 12px;
  padding: 16px 20px; margin: 0 0 22px;
}
.prerequisito .etiqueta { color: #8a6d1f; }
.analogia {
  background: #f2f6f4; border: 1px solid #cfe0d6; border-left: 4px solid #4f7f68;
  border-radius: 0 12px 12px 0; padding: 16px 20px; margin: 16px 0;
}
.analogia .etiqueta { color: #2f5b47; }

/* plan de repaso espaciado */
.plan { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 14px 0 8px; }
.plan .dia {
  background: #fffdf8; border: 1px solid var(--linea); border-radius: 12px;
  padding: 12px 14px; text-align: center;
  box-shadow: 0 10px 16px -16px var(--sombra);
}
.plan .dia strong { display: block; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--acento); margin-bottom: 4px; }
.plan .dia span { font-size: 14.5px; color: #3a352c; }

.transferencia { background: #fbf7ef; border: 1px solid var(--linea); border-radius: 12px; padding: 16px 20px; margin: 16px 0; }
.transferencia .etiqueta { color: #7a5a2b; }

figure { margin: 18px 0 20px; text-align: center; }
figure img { max-width: 100%; border-radius: 10px; box-shadow: 0 14px 26px -22px var(--sombra); }
figcaption {
  margin-top: 8px; font-size: 13.5px; color: var(--suave); font-style: italic;
}

/* impresión: flashcards */
@media print {
  .flashcards { page-break-before: always; }
  .flashcard { border: 1px dashed #999; border-radius: 8px; padding: 10px; margin: 6px 0; break-inside: avoid; }
}

details.pregunta {
  background: #f8f3e6; border: 1px solid var(--linea); border-radius: 10px;
  padding: 10px 14px; margin: 8px 0 12px;
}
details.pregunta summary {
  cursor: pointer; font-weight: bold; list-style: none; outline: none;
}
details.pregunta summary::-webkit-details-marker { display: none; }
details.pregunta summary::before { content: "▸ "; color: var(--acento); }
details.pregunta[open] summary::before { content: "▾ "; }
details.pregunta .respuesta {
  margin: 10px 0 2px; padding-top: 10px; border-top: 1px dashed var(--linea);
}

.checklist { list-style: none; padding-left: 0; }
.checklist li { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px; }
.checklist input { margin-top: 6px; accent-color: var(--acento); }

.pie {
  text-align: center; color: var(--suave); font-size: 12.5px; margin-top: 34px;
  font-family: ui-sans-serif, system-ui, sans-serif;
}
.pie a { color: var(--acento); }

@media print {
  body { background: #fff; font-size: 12pt; }
  .tarjeta { box-shadow: none; transform: none; page-break-inside: avoid; }
  .indice { display: none; }
  details.pregunta { break-inside: avoid; }
  details.pregunta .respuesta { display: block; }
}
@media (max-width: 560px) {
  .envoltura { padding: 22px 14px 60px; }
  .tarjeta { padding: 20px 18px 14px; }
}
"""

LOGO = """<svg viewBox="0 0 120 120" role="img" aria-label="teacher">
  <defs>
    <linearGradient id="tapa" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#f0d9a8"/><stop offset="1" stop-color="#dcc084"/>
    </linearGradient>
  </defs>
  <g transform="rotate(-4 60 60)">
    <rect x="16" y="30" width="52" height="62" rx="6" fill="#fffdf7" stroke="#c8b892" stroke-width="2"/>
    <rect x="52" y="30" width="52" height="62" rx="6" fill="url(#tapa)" stroke="#c8b892" stroke-width="2"/>
    <path d="M22 42h40M22 52h40M22 62h28" stroke="#d8cbb0" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M60 30v62" stroke="#b9a678" stroke-width="2"/>
    <circle cx="92" cy="26" r="12" fill="#%ACCENTO_HEX%" opacity=".92"/>
    <path d="M86 26l4 4 8-9" stroke="#fffdf7" stroke-width="3" fill="none"
          stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>"""


def inline(texto: str) -> str:
    """Convierte negritas, cursivas, código, $math$ y ==término== en línea."""
    t = html.escape(texto)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\$([^$]+)\$", r'<span class="math">$\1$</span>', t)

    def _marca(m):
        clave = slug(m.group(1))
        ficha = FICHAS.get(clave)
        boton = (
            f'<button type="button" class="term" data-ficha="{clave}" '
            f'aria-expanded="false" title="Ver la definición">{m.group(1)}</button>'
        )
        if not ficha:
            return boton
        corto = next((l.strip() for l in ficha["lineas"] if l.strip()), "")
        respaldo = (
            f'<span class="ficha-inline"><strong>{html.escape(ficha["nombre"])}</strong> '
            f"<span>{html.escape(corto)}</span></span>"
        )
        return f'<span class="term-wrap">{boton}{respaldo}</span>'

    t = re.sub(r"==([^=]+)==", _marca, t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    return t


def es_tabla(lineas: list[str], i: int) -> bool:
    """True si en la línea i empieza una tabla markdown con separador."""
    if i + 1 >= len(lineas):
        return False
    a, b = lineas[i].strip(), lineas[i + 1].strip()
    return (
        a.startswith("|")
        and b.startswith("|")
        and re.fullmatch(r"\|[\s:|-]+\|?", b) is not None
    )


def _celda_numerica(celda: str) -> bool:
    """Cierto si la celda es una cifra con unidades, no una frase."""
    v = celda.strip()
    if not re.search(r"\d", v):
        return False
    v = re.sub(r"[${}\\]", "", v)
    v = re.sub(r"(?<=[\d.,])\s*[A-Za-z%·/]+$", "", v).strip()
    return bool(v) and re.fullmatch(r"[\d\s.,+\-−/()]+", v) is not None


def render_tabla(filas: list[str]) -> str:
    def celdas(linea: str) -> list[str]:
        return [c.strip() for c in linea.strip().strip("|").split("|")]

    cabecera = celdas(filas[0])
    cuerpo = [celdas(f) for f in filas[2:]]
    numericas = []
    for c in range(len(cabecera)):
        valores = [f[c] for f in cuerpo if c < len(f) and f[c].strip()]
        numericas.append(bool(valores) and all(_celda_numerica(v) for v in valores))

    def clase(c: int) -> str:
        return ' class="num"' if c < len(numericas) and numericas[c] else ""

    html_tabla = ["<table>", "<thead><tr>"]
    html_tabla += [f"<th{clase(i)}>{inline(c)}</th>" for i, c in enumerate(cabecera)]
    html_tabla.append("</tr></thead><tbody>")
    for fila in cuerpo:
        html_tabla.append(
            "<tr>"
            + "".join(f"<td{clase(i)}>{inline(c)}</td>" for i, c in enumerate(fila))
            + "</tr>"
        )
    html_tabla.append("</tbody></table>")
    return "".join(html_tabla)


def slug(texto: str) -> str:
    s = re.sub(r"<[^>]+>", "", texto)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s]+", "-", s)[:60] or "seccion"


FICHAS: dict[str, dict] = {}


def extraer_fichas(md: str) -> dict[str, dict]:
    """Recoge términos y autores de los bloques ::: glosario y ::: autores."""
    fichas: dict[str, dict] = {}
    tipo = None
    actual = None
    for l in md.splitlines():
        d = l.strip()
        if d.startswith(":::") and d[3:].strip().lower() in ("glosario", "autores"):
            tipo = d[3:].strip().lower()
            continue
        if tipo and d == ":::":
            tipo = None
            actual = None
            continue
        if tipo and d.startswith("## "):
            actual = {"nombre": d[3:].strip(), "tipo": tipo, "lineas": []}
            fichas[slug(actual["nombre"])] = actual
        elif tipo and actual is not None:
            actual["lineas"].append(l)
    return fichas


def plantilla_fichas(fichas: dict[str, dict]) -> str:
    """Contenido de las tarjetas que el popup clona al pulsar un término."""
    if not fichas:
        return ""
    partes = []
    for clave, f in fichas.items():
        cuerpo = [l for l in f["lineas"] if l.strip()]
        corto = cuerpo[0].strip() if cuerpo else ""
        resto = cuerpo[1:]
        partes.append(
            f'<div class="ficha-datos" data-ficha="{clave}">'
            f'<p class="ficha-nombre">{inline(f["nombre"])}</p>'
            f'<p class="ficha-corto">{inline(corto)}</p>'
            f'<div class="ficha-mas">{render_fragmento(resto)}</div>'
            "</div>"
        )
    return f'<template id="fichas">{"".join(partes)}</template>'


def figura_html(caption: str, src: str) -> str:
    """Figura incrustada en base64 para que la guía siga siendo un solo archivo."""
    destino = src
    archivo = (BASE_DIR / src) if BASE_DIR else None
    if archivo and archivo.exists():
        import base64

        mime = {
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }.get(archivo.suffix.lower(), "application/octet-stream")
        datos = base64.b64encode(archivo.read_bytes()).decode()
        destino = f"data:{mime};base64,{datos}"
    return (
        f'<figure><img src="{destino}" alt="{html.escape(caption)}">'
        f"<figcaption>{inline(caption)}</figcaption></figure>"
    )


def render_fragmento(lineas: list[str]) -> str:
    """Markdown mínimo para el interior de pestañas, glosario y ejercicios."""
    piezas: list[str] = []
    parrafo: list[str] = []
    lista: str | None = None

    def cerrar_parrafo():
        nonlocal parrafo
        if parrafo:
            piezas.append("<p>" + inline(" ".join(parrafo).strip()) + "</p>")
            parrafo = []

    def cerrar_lista():
        nonlocal lista
        if lista:
            piezas.append(f"</{lista}>")
            lista = None

    i = 0
    while i < len(lineas):
        d = lineas[i].strip()
        if not d:
            cerrar_parrafo()
            cerrar_lista()
            i += 1
            continue
        m_img = re.match(r"!\[(.*?)\]\((.+?)\)", d)
        if m_img:
            cerrar_parrafo()
            cerrar_lista()
            piezas.append(figura_html(m_img.group(1), m_img.group(2)))
            i += 1
            continue
        if d.startswith("$$"):
            cerrar_parrafo()
            cerrar_lista()
            expr = html.escape(d.strip("$").strip())
            piezas.append(f'<div class="formula">$${expr}$$</div>')
            i += 1
            continue
        if d.startswith(("- ", "* ")):
            cerrar_parrafo()
            if lista != "ul":
                cerrar_lista()
                piezas.append("<ul>")
                lista = "ul"
            piezas.append("<li>" + inline(d[2:]) + "</li>")
            i += 1
            continue
        if re.match(r"^\d+\.\s", d):
            cerrar_parrafo()
            if lista != "ol":
                cerrar_lista()
                piezas.append("<ol>")
                lista = "ol"
            piezas.append("<li>" + inline(re.sub(r"^\d+\.\s", "", d)) + "</li>")
            i += 1
            continue
        if d.startswith("### "):
            cerrar_parrafo()
            cerrar_lista()
            piezas.append("<h4>" + inline(d[4:]) + "</h4>")
            i += 1
            continue
        if d.startswith("> "):
            cerrar_parrafo()
            cerrar_lista()
            piezas.append("<blockquote>" + inline(d[2:]) + "</blockquote>")
            i += 1
            continue
        parrafo.append(d)
        i += 1

    cerrar_parrafo()
    cerrar_lista()
    return "".join(piezas)


_TAB = [0]
TABS_CSS: list[str] = []


def render_bloque(tipo: str, lineas: list[str]) -> str:
    cuerpo_crudo = "\n".join(lineas).strip()

    if tipo in ("glosario", "autores"):
        entradas = []
        actual = None
        for l in cuerpo_crudo.splitlines():
            if l.strip().startswith("## "):
                actual = {"nombre": l.strip()[3:].strip(), "lineas": []}
                entradas.append(actual)
            elif actual is not None:
                actual["lineas"].append(l)
        piezas = []
        for e in entradas:
            cuerpo = [l for l in e["lineas"] if l.strip()]
            corto = cuerpo[0].strip() if cuerpo else ""
            resto = cuerpo[1:]
            ident = "ficha-" + slug(e["nombre"])
            nombre = inline(e["nombre"])
            if resto:
                piezas.append(
                    f'<details class="termino" id="{ident}">'
                    f"<summary><strong>{nombre}</strong>"
                    f'<span class="def">{inline(corto)}</span></summary>'
                    f'<div class="termino-mas">{render_fragmento(resto)}</div>'
                    "</details>"
                )
            else:
                piezas.append(
                    f'<div class="termino" id="{ident}"><strong>{nombre}</strong>'
                    f'<span class="def">{inline(corto)}</span></div>'
                )
        return f'<div class="glosario">{"".join(piezas)}</div>'

    if tipo == "pestanas":
        paneles = []
        actual = None
        for l in cuerpo_crudo.splitlines():
            if l.strip().startswith("## "):
                actual = {"titulo": l.strip()[3:].strip(), "lineas": []}
                paneles.append(actual)
            elif actual is not None:
                actual["lineas"].append(l)
        if not paneles:
            return f'<div class="bloque nota"><p>{inline(cuerpo_crudo)}</p></div>'
        _TAB[0] += 1
        base = f"pest-{_TAB[0]}"
        controles, cuerpos = [], []
        for idx, p in enumerate(paneles):
            pid = f"{base}-{idx}"
            marcado = " checked" if idx == 0 else ""
            controles.append(
                f'<input type="radio" name="{base}" id="{pid}"{marcado}>'
                f'<label for="{pid}">{inline(p["titulo"])}</label>'
            )
            cuerpos.append(
                f'<div class="panel" data-tab="{pid}">{render_fragmento(p["lineas"])}</div>'
            )
            TABS_CSS.append(
                f".pestanas:has(#{pid}:checked) [data-tab='{pid}']{{display:block}}"
            )
        return f'<div class="pestanas">{"".join(controles)}{"".join(cuerpos)}</div>'

    if tipo == "secuencia":
        marcos = []
        for l in cuerpo_crudo.splitlines():
            m = re.match(r"!\[(.*?)\]\((.+?)\)", l.strip())
            if m:
                marcos.append(f"<li>{figura_html(m.group(1), m.group(2))}</li>")
        return f'<ol class="secuencia">{"".join(marcos)}</ol>'

    if tipo == "ejercicio":
        partes = {}
        actual = None
        for l in cuerpo_crudo.splitlines():
            if l.strip().startswith("## "):
                actual = l.strip()[3:].strip().lower()
                partes[actual] = []
            elif actual is not None:
                partes[actual].append(l)
        enunciado = render_fragmento(partes.get("enunciado", []))
        solucion = render_fragmento(partes.get("solución", partes.get("solucion", [])))
        bloque = (
            '<div class="ejercicio"><div class="enunciado">'
            '<span class="etiqueta">Ejercicio</span>'
            f"{enunciado}</div>"
        )
        if solucion:
            bloque += (
                '<details class="solucion"><summary>Ver la solución paso a paso</summary>'
                f"<div>{solucion}</div></details>"
            )
        return bloque + "</div>"

    if tipo == "errores":
        casos = []
        actual = None
        for l in cuerpo_crudo.splitlines():
            if l.strip().startswith("## "):
                actual = {"titulo": l.strip()[3:].strip(), "lineas": []}
                casos.append(actual)
            elif actual is not None:
                actual["lineas"].append(l)
        tarjetas = []
        for c in casos:
            tarjetas.append(
                f'<article class="caso-error"><h3>{inline(c["titulo"])}</h3>'
                f"{render_fragmento(c['lineas'])}</article>"
            )
        return f'<div class="errores">{"".join(tarjetas)}</div>'

    if tipo == "linea":
        entradas = []
        actual = None
        for l in cuerpo_crudo.splitlines():
            if l.strip().startswith("## "):
                titulo = l.strip()[3:].strip()
                for guion in ("—", "–", " - "):
                    if guion in titulo:
                        ano, nombre = titulo.split(guion, 1)
                        break
                else:
                    ano, nombre = "", titulo
                actual = {"ano": ano.strip(), "nombre": nombre.strip(), "lineas": []}
                entradas.append(actual)
            elif actual is not None:
                actual["lineas"].append(l)
        items = []
        for e in entradas:
            items.append(
                f'<li><span class="ano">{inline(e["ano"])}</span>'
                f'<div class="hito"><strong>{inline(e["nombre"])}</strong>'
                f"{render_fragmento(e['lineas'])}</div></li>"
            )
        return f'<ol class="linea">{"".join(items)}</ol>'

    if tipo == "pasos":
        items = [l for l in cuerpo_crudo.splitlines() if l.strip()]
        pasos = "".join(
            "<li>" + inline(re.sub(r"^\s*(?:\d+\.|[-*])\s*", "", l)) + "</li>"
            for l in items
        )
        return f'<ol class="pasos">{pasos}</ol>'

    if tipo == "enfoques":
        tarjetas = []
        for l in cuerpo_crudo.splitlines():
            if not l.strip():
                continue
            limpio = re.sub(r"^\s*[-*]\s*", "", l)
            m = re.match(r"\*\*(.+?)\*\*\s*[—:-]?\s*(.*)", limpio)
            titulo, texto = (m.group(1), m.group(2)) if m else (limpio, "")
            tarjetas.append(
                f"<article><h4>{inline(titulo)}</h4><p>{inline(texto)}</p></article>"
            )
        return f'<div class="enfoques">{"".join(tarjetas)}</div>'

    if tipo == "desglose":
        casos = []
        actual = None
        for l in cuerpo_crudo.splitlines():
            if not l.strip():
                continue
            if l.startswith("## "):
                actual = {"titulo": l[3:].strip(), "pasos": []}
                casos.append(actual)
            elif actual is not None:
                actual["pasos"].append(re.sub(r"^\s*[-*]\s*", "", l))
        if not casos:
            return f'<div class="bloque nota"><p>{inline(cuerpo_crudo)}</p></div>'
        html_casos = []
        for c in casos:
            pasos = "".join(f"<li>{inline(p)}</li>" for p in c["pasos"])
            html_casos.append(
                f"<details><summary>{inline(c['titulo'])}</summary><ol>{pasos}</ol></details>"
            )
        return f'<div class="desglose">{"".join(html_casos)}</div>'

    if tipo == "llegar":
        escalones = []
        for idx, l in enumerate(
            [x for x in cuerpo_crudo.splitlines() if x.strip()], start=1
        ):
            limpio = re.sub(r"^\s*[-*]\s*", "", l)
            if ":" in limpio:
                etapa, texto = limpio.split(":", 1)
            else:
                etapa, texto = f"Paso {idx}", limpio
            escalones.append(
                '<div class="escalon">'
                f'<span class="marca-paso">{idx}</span>'
                f'<span class="etapa">{inline(etapa.strip())}</span>'
                f"<p>{inline(texto.strip())}</p></div>"
            )
        if len(escalones) < 4:
            print(
                f"aviso: el bloque 'llegar' tiene {len(escalones)} pasos; "
                "se recomiendan al menos 4 (observa, compara, cuantifica, nombra)",
                file=sys.stderr,
            )
        return f'<div class="llegar">{"".join(escalones)}</div>'

    if tipo == "objetivo":
        return (
            '<div class="objetivo"><span class="etiqueta">Al terminar podrás</span>'
            f"<p>{inline(cuerpo_crudo)}</p></div>"
        )

    if tipo == "prerequisito":
        return (
            '<div class="prerequisito"><span class="etiqueta">Antes de empezar</span>'
            f"<p>{inline(cuerpo_crudo)}</p></div>"
        )

    if tipo == "analogia":
        return (
            '<div class="analogia"><span class="etiqueta">La analogía</span>'
            f"<p>{inline(cuerpo_crudo)}</p></div>"
        )

    if tipo == "transferencia":
        items = [l for l in cuerpo_crudo.splitlines() if l.strip()]
        lista = "".join(
            "<li>" + inline(re.sub(r"^\s*[-*]\s*", "", l)) + "</li>" for l in items
        )
        return (
            '<div class="transferencia"><span class="etiqueta">Llévatelo a otro contexto</span>'
            f"<ul>{lista}</ul></div>"
        )

    if tipo == "plan":
        dias = []
        for l in cuerpo_crudo.splitlines():
            if not l.strip():
                continue
            limpio = re.sub(r"^\s*[-*]\s*", "", l)
            m = re.match(r"(.+?)\s*[—:-]\s*(.+)", limpio)
            cuando, que = (m.group(1), m.group(2)) if m else (limpio, "")
            dias.append(
                f'<div class="dia"><strong>{inline(cuando)}</strong><span>{inline(que)}</span></div>'
            )
        return f'<div class="plan">{"".join(dias)}</div>'

    etiquetas = {
        "ejemplo": "Ejemplo resuelto",
        "error": "Error típico",
        "nota": "Para recordar",
        "tip": "Truco",
    }
    etiqueta = etiquetas.get(tipo, tipo.capitalize())
    cuerpo = "\n".join(lineas).strip()
    # listas y párrafos dentro del bloque
    piezas = []
    buffer: list[str] = []
    for linea in cuerpo.splitlines():
        if linea.startswith("- "):
            piezas.append(
                "<ul>"
                + "".join(
                    f"<li>{inline(l[2:])}</li>"
                    for l in cuerpo.splitlines()
                    if l.startswith("- ")
                )
                + "</ul>"
            )
            buffer = []
            break
        buffer.append(linea)
    else:
        piezas.append("".join(f"<p>{inline(l)}</p>" for l in buffer if l.strip()))
    return (
        f'<div class="bloque {tipo}"><span class="etiqueta">{etiqueta}</span>'
        + "".join(piezas)
        + "</div>"
    )


BASE_DIR: Path | None = None


def convertir(
    md: str, vistas: dict[str, dict] | None = None
) -> tuple[str, str, str, list[tuple[str, str, str]]]:
    """Devuelve (titulo, idea, cuerpo_html, secciones[(slug, titulo, vista)])."""
    vistas = vistas or {}
    FICHAS.clear()
    FICHAS.update(extraer_fichas(md))
    lineas = md.splitlines()
    titulo = ""
    idea = ""
    secciones: list[tuple[str, str, str]] = []
    cuerpo: list[str] = []
    abierta = False

    i = 0
    en_texto: list[str] | None = None
    bloque_tipo: str | None = None
    bloque_lineas: list[str] = []
    en_codigo = False
    codigo: list[str] = []
    lista_abierta: str | None = None
    parrafo: list[str] = []
    pregunta = None

    def cerrar_parrafo():
        nonlocal parrafo
        if parrafo:
            cuerpo.append("<p>" + inline(" ".join(parrafo).strip()) + "</p>")
            parrafo = []

    def cerrar_lista():
        nonlocal lista_abierta
        if lista_abierta:
            cuerpo.append(f"</{lista_abierta}>")
            lista_abierta = None

    while i < len(lineas):
        cruda = lineas[i]
        linea = cruda.rstrip()
        desnuda = linea.strip()

        if en_codigo:
            if desnuda.startswith("```"):
                cuerpo.append(
                    "<pre><code>" + html.escape("\n".join(codigo)) + "</code></pre>"
                )
                codigo = []
                en_codigo = False
            else:
                codigo.append(cruda)
            i += 1
            continue

        if desnuda.startswith("```"):
            cerrar_parrafo()
            cerrar_lista()
            en_codigo = True
            i += 1
            continue

        if bloque_tipo:
            if desnuda == ":::":
                cuerpo.append(render_bloque(bloque_tipo, bloque_lineas))
                bloque_tipo, bloque_lineas = None, []
            else:
                bloque_lineas.append(linea)
            i += 1
            continue

        if desnuda.startswith(":::") and len(desnuda) > 3:
            cerrar_parrafo()
            cerrar_lista()
            bloque_tipo = desnuda[3:].strip().lower()
            i += 1
            continue

        if desnuda.startswith("Q:"):
            cerrar_parrafo()
            cerrar_lista()
            pregunta = desnuda[2:].strip()
            i += 1
            continue

        if desnuda.startswith("R:") and pregunta is not None:
            respuesta = desnuda[2:].strip()
            cuerpo.append(
                f'<details class="pregunta"><summary>{inline(pregunta)}</summary>'
                f'<div class="respuesta">{inline(respuesta)}</div></details>'
            )
            pregunta = None
            i += 1
            continue

        m_img = re.match(r"!\[(.*?)\]\((.+?)\)", desnuda)
        if m_img:
            cerrar_parrafo()
            cerrar_lista()
            cuerpo.append(figura_html(m_img.group(1), m_img.group(2)))
            i += 1
            continue

        if es_tabla(lineas, i):
            cerrar_parrafo()
            cerrar_lista()
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas.append(lineas[i])
                i += 1
            cuerpo.append(render_tabla(filas))
            continue

        if desnuda.startswith("$$"):
            cerrar_parrafo()
            cerrar_lista()
            expr = html.escape(desnuda.strip("$").strip())
            cuerpo.append(f'<div class="formula">$${expr}$$</div>')
            i += 1
            continue

        if desnuda.startswith("# "):
            if not titulo:
                titulo = desnuda[2:].strip()
            i += 1
            continue

        if desnuda.startswith("## "):
            cerrar_parrafo()
            cerrar_lista()
            bruto = desnuda[3:].strip()
            m_vista = re.search(r"\{(\w+)\}\s*$", bruto)
            vista = m_vista.group(1).lower() if m_vista else "concepto"
            texto = re.sub(r"\s*\{\w+\}\s*$", "", bruto).strip()
            info = vistas.get(vista, {})
            estandar = info.get("titulo", "")
            if not texto:
                texto = estandar or "Sección"
            num = len(secciones) + 1
            if abierta:
                cuerpo.append("</div></section>")
            cuerpo.append(f'<section class="tarjeta revelar" id="{slug(texto)}">')
            if estandar and estandar != texto:
                cuerpo.append(f'<p class="vista">{inline(estandar)}</p>')
            cuerpo.append(
                f'<h2><span class="num">{num:02d}</span>{inline(texto)}'
                '<button class="plegar" type="button" aria-expanded="true" '
                'aria-label="Plegar sección" title="Plegar sección">&#8211;</button></h2>'
                '<div class="cuerpo">'
            )
            secciones.append((slug(texto), texto, vista))
            abierta = True
            i += 1
            continue

        if desnuda.startswith("### "):
            cerrar_parrafo()
            cerrar_lista()
            cuerpo.append("<h3>" + inline(desnuda[4:].strip()) + "</h3>")
            i += 1
            continue

        if desnuda.startswith("> ") and not cuerpo:
            idea = desnuda[2:].strip()
            i += 1
            continue

        if desnuda.startswith("> "):
            cerrar_parrafo()
            cerrar_lista()
            cuerpo.append(
                "<blockquote>" + inline(desnuda[2:].strip()) + "</blockquote>"
            )
            i += 1
            continue

        if desnuda.startswith("- [ ]") or desnuda.startswith("- [x]"):
            cerrar_parrafo()
            if lista_abierta != 'ul class="checklist"':
                cerrar_lista()
                cuerpo.append('<ul class="checklist">')
                lista_abierta = 'ul class="checklist"'
            hecho = "checked" if desnuda.startswith("- [x]") else ""
            cuerpo.append(
                f'<li><input type="checkbox" {hecho}><span>{inline(desnuda[5:].strip())}</span></li>'
            )
            i += 1
            continue

        if desnuda.startswith("- "):
            cerrar_parrafo()
            if lista_abierta != "ul":
                cerrar_lista()
                cuerpo.append("<ul>")
                lista_abierta = "ul"
            cuerpo.append("<li>" + inline(desnuda[2:].strip()) + "</li>")
            i += 1
            continue

        if re.match(r"^\d+\.\s", desnuda):
            cerrar_parrafo()
            if lista_abierta != "ol":
                cerrar_lista()
                cuerpo.append("<ol>")
                lista_abierta = "ol"
            cuerpo.append("<li>" + inline(re.sub(r"^\d+\.\s", "", desnuda)) + "</li>")
            i += 1
            continue

        if not desnuda:
            cerrar_parrafo()
            cerrar_lista()
            i += 1
            continue

        parrafo.append(desnuda)
        i += 1

    cerrar_parrafo()
    cerrar_lista()
    if en_codigo and codigo:
        cuerpo.append("<pre><code>" + html.escape("\n".join(codigo)) + "</code></pre>")
    if bloque_tipo:
        cuerpo.append(render_bloque(bloque_tipo, bloque_lineas))
    if abierta:
        cuerpo.append("</div></section>")

    return titulo, idea, "\n".join(cuerpo), secciones


KATEX = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}], throwOnError: false});"></script>"""

SCRIPT = """<script>
(function () {
  document.documentElement.classList.add("js");

  var obs = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) {
      if (e.isIntersecting) e.target.classList.add("visible");
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".revelar, .pasos").forEach(function (el) { obs.observe(el); });

  var barra = document.querySelector(".progreso");
  if (barra) {
    addEventListener("scroll", function () {
      var h = document.documentElement;
      var avance = h.scrollTop / (h.scrollHeight - h.clientHeight || 1);
      barra.style.width = (avance * 100).toFixed(1) + "%";
    }, { passive: true });
  }

  var enlaces = Array.prototype.slice.call(document.querySelectorAll(".lateral a"));
  var destinos = enlaces.map(function (a) { return document.querySelector(a.getAttribute("href")); });
  if (destinos.length) {
    var espia = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (!e.isIntersecting) return;
        enlaces.forEach(function (a) {
          a.classList.toggle("activo", a.getAttribute("href") === "#" + e.target.id);
        });
      });
    }, { rootMargin: "-15% 0px -70% 0px" });
    destinos.forEach(function (s) { if (s) espia.observe(s); });
  }

  document.querySelectorAll(".plegar").forEach(function (b) {
    b.addEventListener("click", function () {
      var tarjeta = b.closest(".tarjeta");
      var plegada = tarjeta.classList.toggle("plegada");
      b.setAttribute("aria-expanded", String(!plegada));
      b.setAttribute("aria-label", plegada ? "Desplegar sección" : "Plegar sección");
      b.textContent = plegada ? "+" : "–";
    });
  });

  var plantillaFichas = document.getElementById("fichas");
  var fichaAbierta = null;
  var termAbierto = null;

  function cerrarFicha() {
    if (fichaAbierta) { fichaAbierta.remove(); fichaAbierta = null; }
    if (termAbierto) { termAbierto.setAttribute("aria-expanded", "false"); termAbierto = null; }
  }

  document.querySelectorAll(".term").forEach(function (enlace) {
    enlace.addEventListener("click", function (ev) {
      if (!plantillaFichas) return;
      var datos = plantillaFichas.content.querySelector(
        '[data-ficha="' + enlace.dataset.ficha + '"]'
      );
      if (!datos) return;
      ev.preventDefault();
      ev.stopPropagation();
      cerrarFicha();
      var caja = document.createElement("div");
      caja.className = "ficha-flotante";
      caja.appendChild(datos.cloneNode(true));
      document.body.appendChild(caja);
      var r = enlace.getBoundingClientRect();
      var ancho = Math.min(360, document.documentElement.clientWidth - 16);
      caja.style.width = ancho + "px";
      var izq = Math.min(r.left + window.scrollX, document.documentElement.clientWidth - ancho - 12);
      caja.style.left = Math.max(8, izq) + "px";
      caja.style.top = r.bottom + window.scrollY + 8 + "px";
      var cerrar = document.createElement("button");
      cerrar.type = "button";
      cerrar.className = "ficha-cerrar";
      cerrar.setAttribute("aria-label", "Cerrar");
      cerrar.textContent = "×";
      cerrar.addEventListener("click", cerrarFicha);
      caja.appendChild(cerrar);
      if (window.renderMathInElement) {
        window.renderMathInElement(caja, {
          delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false }
          ],
          throwOnError: false
        });
      }
      fichaAbierta = caja;
      termAbierto = enlace;
      enlace.setAttribute("aria-expanded", "true");
    });
  });

  document.addEventListener("click", function (e) {
    if (fichaAbierta && !fichaAbierta.contains(e.target)) cerrarFicha();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") cerrarFicha();
  });
})();
</script>"""


CSS_PATH = Path(__file__).resolve().parent / "estilos" / "teacher.css"


def cargar_css(acento: str) -> str:
    """Lee el CSS compilado del sistema de diseño; si falta, usa un mínimo legible."""
    if CSS_PATH.exists():
        css = CSS_PATH.read_text(encoding="utf-8")
        if acento.lower() != "#b4552f":
            css = css.replace("#b4552f", acento)
        return css
    return (
        "body{font-family:Georgia,serif;max-width:700px;margin:2rem auto;padding:0 1rem;"
        "font-size:19px;line-height:1.6;color:#241d18}"
    )


def construir(
    md: str,
    titulo: str,
    subtitulo: str,
    materia: str,
    acento: str,
    contrato: dict,
) -> str:
    TABS_CSS.clear()
    titulo_md, idea, cuerpo, secciones = convertir(md, contrato.get("vistas", {}))
    titulo = titulo or titulo_md or "Guía de estudio"
    hoy = dt.date.today().strftime("%d/%m/%Y")
    acento_hex = acento.lstrip("#")

    mapa = contrato.get("vistas", {})
    grupos = {
        "concepto": "Concepto",
        "historia": "Historia",
        "practica": "Práctica",
        "transferencia": "Transferencia",
    }
    nav: list[str] = []
    for grupo, etiqueta in grupos.items():
        propias = [
            (s, t)
            for s, t, v in secciones
            if mapa.get(v, {}).get("grupo", "concepto") == grupo
        ]
        if not propias:
            continue
        nav.append(f'<p class="grupo">{etiqueta}</p>')
        for s, t in propias:
            numero = next(i + 1 for i, (ss, _, _) in enumerate(secciones) if ss == s)
            nav.append(
                f'<a href="#{s}"><span class="nav-num">{numero:02d}</span>{html.escape(t)}</a>'
            )
    indice = "".join(nav)

    idea_html = f'<div class="idea">{inline(idea)}</div>' if idea else ""
    css = cargar_css(acento) + "".join(TABS_CSS)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)}</title>
{KATEX}
<style>{css}</style>
</head>
<body>
<div class="progreso"></div>
<div class="layout">
  <aside class="lateral">
    <div class="marca">{LOGO.replace("%ACCENTO_HEX%", acento_hex)}<span>teacher</span></div>
    <nav>
      {indice}
    </nav>
  </aside>

  <main class="contenido">
    <header class="hero">
      <p class="kicker">{html.escape(materia) if materia else "guía de estudio"}</p>
      <h1>{html.escape(titulo)}</h1>
      {f'<p class="sub">{html.escape(subtitulo)}</p>' if subtitulo else ""}
      <p class="fecha">{hoy}</p>
    </header>

    {idea_html}

    {cuerpo.lstrip()}

    <p class="pie">
      Guía generada con teacher · práctica de recuperación activa: responde antes de abrir cada respuesta.
    </p>
  </main>
</div>
{plantilla_fichas(FICHAS)}
{SCRIPT}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Contrato de componentes: una guía cumple o no se genera.
# Las reglas viven en componentes/contrato.json, no en un manual que nadie lee.
# ---------------------------------------------------------------------------

CONTRATO_PATH = Path(__file__).resolve().parent / "componentes" / "contrato.json"


def cargar_contrato() -> dict:
    return json.loads(CONTRATO_PATH.read_text(encoding="utf-8"))


def analizar(md: str) -> dict:
    """Mide el documento: secciones, bloques, preguntas, tablas y viñetas."""
    lineas = md.splitlines()
    doc: dict = {"secciones": [], "bloques": [], "tablas": [], "preguntas": 0}
    sec = None
    bloque = None
    estado = {"parrafo": False}

    def cerrar_parrafo():
        if estado["parrafo"] and sec is not None:
            sec["parrafos"] += 1
        estado["parrafo"] = False

    i = 0
    while i < len(lineas):
        cruda = lineas[i]
        d = cruda.strip()

        if bloque is not None:
            if d == ":::":
                doc["bloques"].append(bloque)
                bloque = None
            else:
                bloque["lineas"].append(cruda)
            i += 1
            continue

        if d.startswith(":::") and len(d) > 3:
            cerrar_parrafo()
            bloque = {"tipo": d[3:].strip().lower(), "lineas": [], "linea": i + 1}
            i += 1
            continue

        if d.startswith("```"):
            cerrar_parrafo()
            i += 1
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                i += 1
            i += 1
            continue

        if d.startswith("## "):
            cerrar_parrafo()
            m = re.search(r"\{(\w+)\}\s*$", d)
            vista = m.group(1).lower() if m else "concepto"
            titulo = re.sub(r"\s*\{\w+\}\s*$", "", d[3:]).strip()
            sec = {
                "titulo": titulo,
                "vista": vista,
                "parrafos": 0,
                "vinietas": 0,
                "linea": i + 1,
            }
            doc["secciones"].append(sec)
            i += 1
            continue

        if d.startswith("|"):
            cerrar_parrafo()
            inicio = i + 1
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas.append(lineas[i])
                i += 1
            doc["tablas"].append({"linea": inicio, "filas": filas})
            continue

        if d.startswith("Q:"):
            cerrar_parrafo()
            doc["preguntas"] += 1
            i += 1
            continue

        if d.startswith("R:") or d.startswith("![") or d.startswith("# "):
            cerrar_parrafo()
            i += 1
            continue

        if re.match(r"^([-*]|\d+\.)\s", d):
            cerrar_parrafo()
            if sec is not None:
                sec["vinietas"] += 1
            i += 1
            continue

        if not d:
            cerrar_parrafo()
            i += 1
            continue

        if not d.startswith("###"):
            estado["parrafo"] = True
        i += 1

    cerrar_parrafo()
    return doc


def _tabla_numerica(filas: list[str]) -> bool:
    """Cierto si al menos dos filas de datos traen cifras."""
    con_cifras = 0
    for f in filas[1:]:
        if re.match(r"^\|[\s:|-]+\|?$", f.strip()):
            continue
        celdas = [c.strip() for c in f.strip().strip("|").split("|")]
        if any(re.search(r"\d", c) for c in celdas):
            con_cifras += 1
    return con_cifras >= 2


def _secciones_md(md: str) -> list[tuple[str, str]]:
    """Secciones de nivel 2 sin cortar los bloques ::: que viven dentro."""
    secciones: list[tuple[str, list[str]]] = []
    actual = None
    dentro = False
    for l in md.splitlines():
        d = l.strip()
        if d.startswith(":::") and len(d) > 3:
            dentro = True
        elif d == ":::" and dentro:
            dentro = False
        if not dentro and d.startswith("## "):
            if actual is not None:
                secciones.append((actual[0], "\n".join(actual[1])))
            actual = (d[3:].strip(), [])
            continue
        if actual is not None:
            actual[1].append(l)
    if actual is not None:
        secciones.append((actual[0], "\n".join(actual[1])))
    return secciones


def validar(md: str, contrato: dict) -> list[tuple[str, str]]:
    """Devuelve el informe como pares (nivel, mensaje)."""
    doc = analizar(md)
    m = contrato["minimos"]
    salida: list[tuple[str, str]] = []

    def bloques(tipo: str) -> list[dict]:
        return [b for b in doc["bloques"] if b["tipo"] == tipo]

    def vistas(nombre: str) -> list[dict]:
        return [s for s in doc["secciones"] if s["vista"] == nombre]

    # --- estructura ---
    total = len(doc["secciones"])
    if total < m["secciones"]:
        salida.append(
            (
                "error",
                f"{total} secciones; faltan ideas por desarrollar (mínimo {m['secciones']})",
            )
        )
    elif total > m["secciones_max"]:
        salida.append(
            (
                "aviso",
                f"{total} secciones; por encima de {m['secciones_max']} se pierde el hilo",
            )
        )
    else:
        salida.append(("ok", f"{total} secciones"))

    for nombre in contrato["obligatorios"]:
        forma = contrato["componentes"].get(nombre, {}).get("forma", "bloque")
        hay = vistas(nombre) if forma == "vista" else bloques(nombre)
        if not hay:
            salida.append(
                (
                    "error",
                    f"falta «{nombre}» — {contrato['componentes'][nombre]['para']}",
                )
            )
        else:
            salida.append(("ok", f"{nombre} presente"))

    conocidas = set(contrato.get("vistas", {})) | {"concepto"}
    for s in doc["secciones"]:
        if s["vista"] not in conocidas:
            salida.append(
                (
                    "error",
                    f"«{s['titulo']}» (línea {s['linea']}): vista «{s['vista']}» no existe; "
                    f"usa una de: {', '.join(sorted(conocidas))}",
                )
            )

    # --- fichas: términos y autores desplegables, marcas ==ficha== ---
    terminos = set()
    for b in bloques("glosario") + bloques("autores"):
        entradas = []
        actual = None
        for l in b["lineas"]:
            if l.strip().startswith("## "):
                actual = {"nombre": l.strip()[3:].strip(), "lineas": []}
                entradas.append(actual)
            elif actual is not None:
                actual["lineas"].append(l)
        for e in entradas:
            terminos.add(slug(e["nombre"]))
            cuerpo = [l for l in e["lineas"] if l.strip()]
            if len(cuerpo) < 3:
                salida.append(
                    (
                        "error",
                        f"«{e['nombre']}»: {len(cuerpo)} línea(s) de detalle; "
                        "cada ficha necesita al menos dos párrafos",
                    )
                )
    if vistas("dominio") and len(terminos) < 4:
        salida.append(
            (
                "error",
                f"dominio: {len(terminos)} fichas, mínimo 4 — usa ::: glosario o ::: autores",
            )
        )
    for encontrado in re.finditer(r"==([^=]+)==", md):
        if slug(encontrado.group(1)) not in terminos:
            salida.append(
                (
                    "error",
                    f"«{encontrado.group(1)}» está marcado pero no tiene ficha en el glosario",
                )
            )
            break

    # --- ejercicios: solución desarrollada ---
    for b in bloques("ejercicio"):
        solucion = []
        dentro = False
        for l in b["lineas"]:
            if l.strip().startswith("## "):
                dentro = l.strip()[3:].strip().lower().startswith("soluci")
                continue
            if dentro and l.strip():
                solucion.append(l)
        if len(solucion) < 6:
            salida.append(
                (
                    "error",
                    f"ejercicio (línea {b['linea']}): solución de {len(solucion)} líneas, "
                    "mínimo 6 — desarróllala paso a paso",
                )
            )

    # --- respuestas: que expliquen, no que contesten ---
    for n, l in enumerate(md.splitlines(), start=1):
        if l.strip().startswith("R:"):
            texto = l.strip()[2:].strip()
            if len(texto) < 100:
                salida.append(
                    (
                        "error",
                        f"línea {n}: respuesta de {len(texto)} caracteres; desarrolla el porqué",
                    )
                )

    # --- fórmulas: delimitadores balanceados ---
    for n, l in enumerate(md.splitlines(), start=1):
        if l.count("$$") % 2:
            salida.append(
                (
                    "error",
                    f"línea {n}: «$$» sin cerrar; cada fórmula va completa en una línea",
                )
            )
            break
        if l.replace("$$", "").count("$") % 2:
            salida.append(("error", f"línea {n}: «$» sin cerrar"))
            break

    # --- miradas: al menos tres enfoques en pestañas ---
    if vistas("miradas"):
        paneles = max(
            (
                sum(1 for l in b["lineas"] if l.strip().startswith("## "))
                for b in bloques("pestanas")
            ),
            default=0,
        )
        if paneles < 3:
            salida.append(
                (
                    "error",
                    f"miradas: usa ::: pestanas con al menos 3 enfoques (hay {paneles})",
                )
            )
        else:
            salida.append(("ok", f"miradas: {paneles} enfoques en pestañas"))

    # --- fuentes: al menos tres referencias con año ---
    for encabezado, parte in _secciones_md(md):
        if "{fuentes}" in encabezado:
            refs = re.findall(r"\((?:1[5-9]\d{2}|20\d{2})\)", parte)
            if len(refs) < 3:
                salida.append(
                    ("error", f"fuentes: {len(refs)} referencias con año, mínimo 3")
                )
            else:
                salida.append(("ok", f"fuentes: {len(refs)} referencias con año"))

    # --- línea de tiempo: al menos cuatro hitos con año y desarrollo ---
    for b in bloques("linea"):
        hitos: list[tuple[str, list[str]]] = []
        actual = None
        for l in b["lineas"]:
            if l.strip().startswith("## "):
                actual = (l.strip()[3:].strip(), [])
                hitos.append(actual)
            elif actual is not None:
                actual[1].append(l)
        con_ano = [h for h, _ in hitos if re.search(r"\d{4}", h)]
        flojos = [h for h, ls in hitos if len([l for l in ls if l.strip()]) < 2]
        if len(con_ano) < 4:
            salida.append(
                (
                    "error",
                    f"línea de tiempo (línea {b['linea']}): {len(con_ano)} hitos con año, mínimo 4",
                )
            )
        elif flojos:
            salida.append(
                (
                    "error",
                    f"línea de tiempo: {len(flojos)} hito(s) con una sola frase; "
                    f"desarrolla al menos dos párrafos ({', '.join(flojos[:3])})",
                )
            )
        else:
            salida.append(
                ("ok", f"línea de tiempo: {len(con_ano)} hitos desarrollados")
            )

    # --- cada enfoque lleva su diagrama ---
    for encabezado, parte in _secciones_md(md):
        if (
            "{miradas}" in encabezado
            or "{metodos}" in encabezado
            or "{campos}" in encabezado
        ):
            if "::: pestanas" not in parte:
                continue
            cuerpo_p = parte.split("::: pestanas", 1)[1]
            paneles = re.split(r"^## ", cuerpo_p, flags=re.M)[1:]
            sin_img = [p.splitlines()[0].strip() for p in paneles if "![" not in p]
            if sin_img:
                salida.append(
                    (
                        "error",
                        f"{encabezado}: cada enfoque necesita un diagrama; faltan "
                        f"{', '.join(sin_img)}",
                    )
                )
            elif paneles:
                salida.append(
                    (
                        "ok",
                        f"{encabezado.split('{')[0].strip()}: {len(paneles)} enfoques con diagrama",
                    )
                )
        if "{practica}" in encabezado and "![" not in parte:
            salida.append(
                (
                    "error",
                    "práctica: falta al menos una imagen que acompañe los ejercicios",
                )
            )

    # --- errores: casos con imagen y desarrollo ---
    if vistas("errores"):
        casos: list[tuple[str, list[str]]] = []
        for b in bloques("errores"):
            actual = None
            for l in b["lineas"]:
                if l.strip().startswith("## "):
                    actual = (l.strip()[3:].strip(), [])
                    casos.append(actual)
                elif actual is not None:
                    actual[1].append(l)
        if len(casos) < 6:
            salida.append(("error", f"errores: {len(casos)} casos, mínimo 6"))
        for titulo, lineas in casos:
            if "![" not in "\n".join(lineas):
                salida.append(
                    ("error", f"error «{titulo}»: le falta el diagrama del caso")
                )
                break
            if len([l for l in lineas if l.strip()]) < 7:
                salida.append(
                    ("error", f"error «{titulo}»: menos de 7 líneas de desarrollo")
                )
                break
        else:
            if casos:
                salida.append(
                    ("ok", f"errores: {len(casos)} casos con imagen y desarrollo")
                )

    # --- historia: relato, no cronología ---
    for s in vistas("historia"):
        if s["vinietas"]:
            salida.append(
                (
                    "error",
                    f"historia (línea {s['linea']}): {s['vinietas']} viñetas; cuéntala como relato",
                )
            )
        if s["parrafos"] < m["parrafos_historia"]:
            salida.append(
                (
                    "error",
                    f"historia (línea {s['linea']}): {s['parrafos']} párrafos, "
                    f"mínimo {m['parrafos_historia']} — quién, qué problema tenía, qué cambió",
                )
            )
        elif not s["vinietas"]:
            salida.append(("ok", f"historia: {s['parrafos']} párrafos, sin viñetas"))

    # --- llegar: derivar antes de nombrar ---
    for b in bloques("llegar"):
        pasos = len([l for l in b["lineas"] if l.strip()])
        if pasos < m["pasos_llegar"]:
            salida.append(
                (
                    "error",
                    f"llegar (línea {b['linea']}): {pasos} pasos, mínimo {m['pasos_llegar']} "
                    "— observa, compara, cuantifica, nombra, verifica, decide",
                )
            )
        else:
            salida.append(("ok", f"llegar: {pasos} pasos"))

    # --- desglose: cada caso con su aritmética ---
    for b in bloques("desglose"):
        casos, actual = [], None
        for l in b["lineas"]:
            if l.strip().startswith("## "):
                actual = []
                casos.append(actual)
            elif actual is not None and l.strip():
                actual.append(l)
        if not casos:
            salida.append(
                (
                    "error",
                    f"desglose (línea {b['linea']}): sin casos «## ...»; cada cifra va aparte",
                )
            )
            continue
        flojos = [c for c in casos if len(c) < m["pasos_desglose"]]
        if flojos:
            salida.append(
                (
                    "error",
                    f"desglose (línea {b['linea']}): {len(flojos)} caso(s) con menos de "
                    f"{m['pasos_desglose']} operaciones; el lector no reconstruye el número",
                )
            )
        else:
            salida.append(
                ("ok", f"desglose: {len(casos)} caso(s) con la cuenta completa")
            )

    # --- práctica ---
    if doc["preguntas"] < m["preguntas"]:
        salida.append(
            (
                "error",
                f"{doc['preguntas']} preguntas Q/R, mínimo {m['preguntas']} para que se recuerde",
            )
        )
    else:
        salida.append(("ok", f"{doc['preguntas']} preguntas de recuperación"))

    # --- cifras sin explicación ---
    for cond in contrato["condiciones"]:
        if cond["si"] == "tabla_numerica":
            con_cifras = [t for t in doc["tablas"] if _tabla_numerica(t["filas"])]
            if con_cifras and not bloques(cond["requiere"]):
                salida.append(
                    ("error", f"línea {con_cifras[0]['linea']}: {cond['mensaje']}")
                )

    # --- voz ---
    lineas = md.splitlines()
    for frase in contrato["frases_prohibidas"]:
        for n, l in enumerate(lineas, start=1):
            if frase in l.lower():
                salida.append(
                    (
                        "aviso",
                        f"línea {n}: «{frase}» no dice nada; escribe la cosa directamente",
                    )
                )
                break

    for marca in contrato["marcadores"]:
        for n, l in enumerate(lineas, start=1):
            golpe = marca in l if marca.isupper() else marca in l.lower()
            if golpe:
                salida.append(("error", f"línea {n}: marcador «{marca}» sin resolver"))
                break

    for frase in contrato.get("prohibido_meta", []):
        patron = re.compile(rf"\b{re.escape(frase)}\b", re.I)
        for n, l in enumerate(lineas, start=1):
            if patron.search(l):
                salida.append(
                    (
                        "error",
                        f"línea {n}: «{frase}» habla de la actividad, no del concepto",
                    )
                )
                break

    # --- densidad ---
    palabras = len(re.findall(r"\w+", md))
    if palabras < m["palabras"]:
        salida.append(
            (
                "aviso",
                f"{palabras} palabras; con menos de {m['palabras']} no alcanza a explicar",
            )
        )

    for s in vistas("concepto"):
        if s["parrafos"] < m["parrafos_concepto"]:
            salida.append(
                (
                    "aviso",
                    f"«{s['titulo']}» (línea {s['linea']}): {s['parrafos']} párrafos; falta prosa",
                )
            )

    return salida


def imprimir_informe(problemas: list[tuple[str, str]]) -> int:
    marcas = {"ok": "  ok  ", "aviso": " aviso", "error": " error"}
    for nivel, texto in problemas:
        print(f"[{marcas[nivel]}] {texto}")
    errores = sum(1 for n, _ in problemas if n == "error")
    avisos = sum(1 for n, _ in problemas if n == "aviso")
    if errores:
        print(
            f"\n{errores} error(es), {avisos} aviso(s). La guía no se genera hasta corregirlos."
        )
    else:
        print(f"\nContrato cumplido{'' if not avisos else f' con {avisos} aviso(s)'}.")
    return errores


def imprimir_catalogo(contrato: dict) -> None:
    m = contrato["minimos"]
    print("# Componentes\n")
    print(
        "Un componente es un bloque con una obligación. Si lo usas, debe cumplir esto:\n"
    )
    for nombre, c in contrato["componentes"].items():
        print(f"## {nombre}\n")
        print(f"`{c['sintaxis']}`\n")
        print(f"{c['para']}\n")
        print(f"- Bien: {c['ejemplo']}")
        print(f"- Mal: {c['error']}\n")
    print("# Mínimos\n")
    for k, v in m.items():
        print(f"- {k}: {v}")
    print(f"\n# Obligatorios\n\n{', '.join(contrato['obligatorios'])}")
    print("\n# Vistas\n")
    for nombre, v in contrato.get("vistas", {}).items():
        print(f"- `{{{nombre}}}` — {v['titulo']} · grupo {v['grupo']}: {v['para']}")


def main(argv: list[str] | None = None) -> int:
    try:  # consolas de Windows en cp1252 revientan con ∫, ≈ o →
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    ap = argparse.ArgumentParser(
        description="Markdown → guía HTML de estudio (papercraft)."
    )
    ap.add_argument("entrada", nargs="?", default="")
    ap.add_argument("--salida", default="")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--subtitulo", default="")
    ap.add_argument("--materia", default="")
    ap.add_argument("--acento", default="#b4532a")
    ap.add_argument("--abrir", action="store_true", help="abre la guía en el navegador")
    ap.add_argument("--validar", action="store_true", help="solo revisa el contrato")
    ap.add_argument("--forzar", action="store_true", help="genera aunque haya errores")
    ap.add_argument("--catalogo", action="store_true", help="lista los componentes")
    args = ap.parse_args(argv)

    contrato = cargar_contrato()

    if args.catalogo:
        imprimir_catalogo(contrato)
        return 0

    if not args.entrada:
        ap.error("falta el archivo de entrada")

    origen = Path(args.entrada)
    if not origen.exists():
        print(f"no existe: {origen}", file=sys.stderr)
        return 2

    global BASE_DIR
    BASE_DIR = origen.resolve().parent

    md = origen.read_text(encoding="utf-8")

    problemas = validar(md, contrato)
    errores = imprimir_informe(problemas)
    if args.validar:
        return 1 if errores else 0
    if errores and not args.forzar:
        return 1
    if not args.salida:
        ap.error("falta --salida")

    salida = construir(
        md, args.titulo, args.subtitulo, args.materia, args.acento, contrato
    )
    destino = Path(args.salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(salida, encoding="utf-8")
    print(f"\nguía: {destino} ({len(salida) // 1024} KB)")
    if args.abrir:
        webbrowser.open(destino.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
