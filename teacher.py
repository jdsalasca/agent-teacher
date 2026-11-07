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
    """Convierte negritas, cursivas, código y $math$ en línea. Escapa el HTML primero."""
    t = html.escape(texto)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\$([^$]+)\$", r'<span class="math">$\1$</span>', t)
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


def render_tabla(filas: list[str]) -> str:
    def celdas(linea: str) -> list[str]:
        return [c.strip() for c in linea.strip().strip("|").split("|")]

    cabecera = celdas(filas[0])
    cuerpo = [celdas(f) for f in filas[2:]]
    html_tabla = ["<table>", "<thead><tr>"]
    html_tabla += [f"<th>{inline(c)}</th>" for c in cabecera]
    html_tabla.append("</tr></thead><tbody>")
    for fila in cuerpo:
        html_tabla.append(
            "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in fila) + "</tr>"
        )
    html_tabla.append("</tbody></table>")
    return "".join(html_tabla)


def slug(texto: str) -> str:
    s = re.sub(r"<[^>]+>", "", texto)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s]+", "-", s)[:60] or "seccion"


def render_bloque(tipo: str, lineas: list[str]) -> str:
    cuerpo_crudo = "\n".join(lineas).strip()

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


def convertir(md: str) -> tuple[str, str, str, list[tuple[str, str]]]:
    """Devuelve (titulo, idea, cuerpo_html, secciones[(slug, titulo)])."""
    lineas = md.splitlines()
    titulo = ""
    idea = ""
    secciones: list[tuple[str, str]] = []
    cuerpo: list[str] = []

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
            caption, src = m_img.group(1), m_img.group(2)
            destino_img = src
            archivo = (BASE_DIR / src) if BASE_DIR else None
            if archivo and archivo.exists():
                import base64

                mime = {
                    ".svg": "image/svg+xml",
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                }.get(archivo.suffix.lower(), "application/octet-stream")
                datos = base64.b64encode(archivo.read_bytes()).decode()
                destino_img = f"data:{mime};base64,{datos}"
            cuerpo.append(
                f'<figure><img src="{destino_img}" alt="{html.escape(caption)}">'
                f"<figcaption>{inline(caption)}</figcaption></figure>"
            )
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
            expr = desnuda.strip("$").strip()
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
            num = len(secciones) + 1
            cuerpo.append("</section>")
            cuerpo.append(
                f'<section class="tarjeta revelar" id="{slug(texto)}">'
                f'<h2><span class="num">{num:02d}</span>{inline(texto)}</h2>'
            )
            secciones.append((slug(texto), texto, vista))
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
    cuerpo.append("</section>")

    return titulo, idea, "\n".join(cuerpo), secciones


KATEX = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}], throwOnError: false});"></script>"""

SCRIPT = """<script>
(function () {
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


def construir(md: str, titulo: str, subtitulo: str, materia: str, acento: str) -> str:
    titulo_md, idea, cuerpo, secciones = convertir(md)
    titulo = titulo or titulo_md or "Guía de estudio"
    hoy = dt.date.today().strftime("%d/%m/%Y")
    acento_hex = acento.lstrip("#")

    vistas = {
        "concepto": "Concepto",
        "historia": "Historia",
        "practica": "Práctica",
        "transferencia": "Transferencia",
    }
    nav: list[str] = []
    for clave, etiqueta in vistas.items():
        propias = [(s, t) for s, t, v in secciones if v == clave]
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
    css = cargar_css(acento)

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

    {cuerpo.lstrip().removeprefix("</section>")}

    <p class="pie">
      Guía generada con teacher · práctica de recuperación activa: responde antes de abrir cada respuesta.
    </p>
  </main>
</div>
{SCRIPT}
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Markdown → guía HTML de estudio (papercraft)."
    )
    ap.add_argument("entrada")
    ap.add_argument("--salida", required=True)
    ap.add_argument("--titulo", default="")
    ap.add_argument("--subtitulo", default="")
    ap.add_argument("--materia", default="")
    ap.add_argument("--acento", default="#b4532a")
    ap.add_argument("--abrir", action="store_true", help="abre la guía en el navegador")
    args = ap.parse_args(argv)

    origen = Path(args.entrada)
    if not origen.exists():
        print(f"no existe: {origen}", file=sys.stderr)
        return 2

    global BASE_DIR
    BASE_DIR = origen.resolve().parent

    md = origen.read_text(encoding="utf-8")
    salida = construir(md, args.titulo, args.subtitulo, args.materia, args.acento)
    destino = Path(args.salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(salida, encoding="utf-8")
    print(f"guía: {destino} ({len(salida) // 1024} KB)")
    if args.abrir:
        webbrowser.open(destino.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
