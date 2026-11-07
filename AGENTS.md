# AGENTS.md — teacher

Motor de guías de estudio en HTML con estética *papercraft* y pedagogía basada en ciencia del aprendizaje. Las reglas del workspace siguen aplicando.

## Lo único que hay que saber

```bash
python teacher.py --catalogo                  # qué componentes existen y qué exige cada uno
python teacher.py leccion.md --validar        # ¿cumple el contrato?
python teacher.py leccion.md --salida Guia_Tema.html \
    --titulo "..." --materia "Curso" --abrir
```

**El motor no genera una guía que incumpla el contrato.** Lista lo que falta y sale con código 1. Las reglas viven en `componentes/contrato.json`, no en este archivo: si hay que cambiar una, se cambia ahí y el validador la aplica.

`--forzar` existe solo para casos deliberados (una guía corta a propósito). No es la salida por defecto.

## Archivos

| Archivo | Para qué |
| --- | --- |
| `teacher.py` | Motor y validador. |
| `componentes/contrato.json` | Componentes, obligaciones, mínimos y frases prohibidas. **Fuente de verdad.** |
| `ejemplo.md` | Lección modelo: es la referencia de cómo se ve una guía que pasa el contrato. |
| `papers/` | Evidencia que sostiene las decisiones pedagógicas. |
| `estilos/` | Sistema de diseño en SCSS. |
| `prueba/` | Capturas de verificación visual. |

## Trabajo

1. **Copiar la estructura del ejemplo, no inventarla.** `ejemplo.md` pasa el validador; una guía nueva debería parecerse.
2. **Usar el vocabulario de vistas.** `{problema}`, `{historia}`, `{llegar}`… salen de `contrato.json`; un sufijo inventado es un error. `--catalogo` los lista.
3. **Validar antes de entregar.** `--validar` y corregir los errores. Los avisos se leen; si se ignoran, se sabe por qué.
3. **Verificación visual obligatoria.** Abrir el HTML y revisar portada, fórmulas, tablas, desgloses y figuras. Si algo se ve mal, se corrige y se regenera.
4. **Un tema por guía.** Dos ideas centrales son dos guías.
5. **Las guías se guardan en la carpeta del curso**, nunca aquí.
6. **No se toca el CSS desde el Markdown.** El diseño se cambia en `estilos/` y se compila con `sass estilos/teacher.scss estilos/teacher.css --style=expanded`.

## Estilos que no se tocan (tienen respaldo)

- Cuerpo 18-20 px; interlineado 1,5-1,6; línea de 45-75 caracteres.
- Nunca texto justificado (WCAG 1.4.8).
- Contraste AA: tinta `#241d18` sobre papel `#f7f0e6`.

## Límites conocidos

- KaTeX se carga por CDN: sin internet las fórmulas muestran el LaTeX crudo.
- Las tablas necesitan la línea separadora `|---|`.
- No hay numeración automática de figuras ni referencias cruzadas.
- El validador mide forma, no verdad: una guía puede pasar y estar conceptualmente mal. Eso lo revisa una persona.
