"""El contrato tiene que discriminar: el ejemplo pasa, una guía floja no.

python test_contrato.py
"""

import pathlib
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parent
MOTOR = RAIZ / "teacher.py"

FLOJA = """# Guía floja

> Una idea.

## Introducción {inventada}

Es importante destacar que la integral es muy importante en el mundo actual.

## Historia {historia}

- 1854: Riemann.
- 1823: Cauchy.

## Tabla {practica}

| n | resultado |
| --- | --- |
| 1 | 200 |
| 4 | 208,75 |
| 20 | 212,35 |

TODO: completar.
"""


def validar(archivo: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MOTOR), str(archivo), "--validar"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


buena = validar(RAIZ / "ejemplo.md")
assert buena.returncode == 0, buena.stdout
assert "Contrato cumplido" in buena.stdout

with tempfile.TemporaryDirectory() as tmp:
    floja = pathlib.Path(tmp) / "floja.md"
    floja.write_text(FLOJA, encoding="utf-8")
    mala = validar(floja)

assert mala.returncode == 1, mala.stdout
for falta in (
    "objetivo",
    "llegar",
    "plan",
    "historia",
    "desglose",
    "TODO",
    "inventada",
):
    assert falta in mala.stdout, f"no reportó «{falta}»"

print("ok: el contrato distingue una guía completa de una floja")
