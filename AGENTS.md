# AGENTS.md — teacher

Motor de guías de estudio en HTML con estética *papercraft* y pedagogía basada en ciencia del aprendizaje.

Este archivo gobierna la carpeta `tools/teacher`. Las reglas del workspace (`..\..\..\AGENTS.md` y las de cada curso) siguen aplicando.

## Qué hay aquí

| Archivo | Para qué |
| --- | --- |
| `teacher.py` | Motor: convierte un Markdown en una guía HTML autocontenida. |
| `ejemplo.md` | Lección de muestra con todas las capacidades (LaTeX, tablas, pasos, enfoques, Q/R). |
| `ejemplo.html` | Salida generada del ejemplo. Sirve para probar cambios. |
| `prueba/` | Capturas de verificación visual. No se versiona como entregable. |

## Skill asociada

`~/.config/opencode/skills/on-demand/SKILL.md`

**Toda explicación pedagógica pasa por esa skill.** Define cuándo usarla, la estructura obligatoria (7 secciones), los principios de aprendizaje y el checklist de calidad. Este AGENTS.md solo describe el motor; la pedagogía vive en la skill.

## Uso

```bash
python teacher.py leccion.md --salida Guia_Tema.html \
    --titulo "..." --subtitulo "..." --materia "Curso" --acento "#b4532a" --abrir
```

Salida: un solo HTML, sin build y sin dependencias de Python. KaTeX se carga por CDN solo para las fórmulas.

## Convención del Markdown

| Sintaxis | Resultado |
| --- | --- |
| `# Título` | Título del documento |
| `> frase` (primera, antes de secciones) | Idea central destacada |
| `## Sección {vista}` | Tarjeta numerada y entrada en el menú lateral |
| `### Subtítulo` | Subtítulo dentro de la tarjeta |
| `$...$` y `$$...$$` | LaTeX (KaTeX) en línea y centrado |
| `![leyenda](figuras/x.svg)` | Figura incrustada en base64 (sigue siendo un solo archivo) |
| Tablas con `\|---\|` | Tabla con encabezado tenue |
| `::: ejemplo / error / nota / tip` | Bloques de color con etiqueta |
| `::: objetivo / prerequisito / analogia / transferencia` | Bloques pedagógicos con estilo propio |
| `::: pasos` | Escalera animada de conclusiones (`1.`, `2.`…) |
| `::: enfoques` | Rejilla de tarjetas (`- **Título** — texto`) |
| `::: plan` | Tarjetas de repaso espaciado (`- Día 2 — qué hacer`) |
| `Q:` / `R:` | Tarjeta de recuperación que se despliega |
| `- [ ]` / `- [x]` | Checklist de transferencia |
| Cercas ``` | Bloque de código |

### Vistas del menú lateral

El sufijo `{vista}` agrupa la sección en la barra izquierda. Valores válidos:

- `{concepto}` — qué es y por qué (por defecto).
- `{historia}` — de dónde salió la idea.
- `{practica}` — ejemplos, métodos, ejercicios.
- `{transferencia}` — aplicación a otros contextos.

Una guía bien armada tiene al menos una sección de cada tipo; el orden del documento debe respetar el orden de los grupos (concepto → historia → práctica → transferencia) para que la numeración no salte.

## Sistema de estilos (SCSS)

El diseño vive en `estilos/` y se compila a un CSS que el motor incrusta:

```
estilos/_tokens.scss    → colores, tipografía, espacio (fuente de verdad)
estilos/teacher.scss    → componentes
estilos/teacher.css     → compilado que lee teacher.py
```

Para cambiar el diseño:

```bash
sass estilos/teacher.scss estilos/teacher.css --style=expanded
python teacher.py ejemplo.md --salida ejemplo.html
```

Reglas tipográficas que **no se tocan** (están sustentadas en evidencia):

- Cuerpo entre 18 y 20 px; nunca menos de 16.
- Interlineado 1,5 a 1,6; los extremos (0,8 o 1,8) perjudican la comprensión.
- Ancho de línea 45-75 caracteres; el contenedor está en 700 px para lograrlo.
- Texto **nunca justificado** (WCAG 1.4.8): ríos y espacios irregulares.
- Contraste AA como mínimo; tinta `#241d18` sobre papel `#f7f0e6`.


## Reglas de trabajo

1. **No se toca el CSS desde el Markdown.** Si el diseño necesita cambiar, se cambia `teacher.py` y se regenera el ejemplo.
2. **Un tema por guía.** Si el tema tiene dos ideas centrales, son dos guías.
3. **El Markdown es la fuente.** Se guarda junto al HTML para poder corregir sin reescribir.
4. **Verificación visual obligatoria.** Generar, abrir y revisar en el navegador: fórmula centrada, tablas alineadas, tarjetas sin cortes, animaciones sin saltos. Si algo se ve mal, se corrige y se regenera.
5. **Las guías se guardan en la carpeta del curso**, nunca aquí. Esta carpeta solo contiene el motor, el ejemplo y las pruebas.
6. **Sin LaTeX roto.** Si una fórmula no renderiza, se prueba en `ejemplo.md` antes de usarla en una guía real.

## Límites conocidos

- KaTeX necesita internet. Sin conexión, las fórmulas muestran el LaTeX crudo.
- Las tablas requieren la línea separadora; sin ella se renderizan como párrafo.
- Las animaciones usan `IntersectionObserver`: no hay animaciones si el navegador las bloquea por `prefers-reduced-motion`.
- No hay numeración automática de figuras ni referencias cruzadas.

## Cómo probar un cambio

```bash
python teacher.py ejemplo.md --salida ejemplo.html --titulo "Prueba"
```

Abrir `ejemplo.html` y revisar las cuatro zonas: portada, fórmula centrada, tabla, pasos animados y tarjetas de enfoques.
