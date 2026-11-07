# agent-teacher

Convierte un tema en una **guía HTML de estudio** que se puede leer, practicar, repasar y recordar. No es un resumen bonito: es una estructura diseñada con la evidencia sobre aprendizaje humano.

- Menú lateral con cuatro grupos: **Concepto · Historia · Práctica · Transferencia**, y un vocabulario fijo de trece secciones (`{problema}`, `{dominio}`, `{concepto}`, `{llegar}`, `{errores}`, `{aplicacion}`, `{metodos}`, `{miradas}`, `{escenarios}`, `{campos}`, `{cierre}`, `{practica}`, `{historia}`).
- Cada sección se **pliega** con un clic, para repasar sin recorrer toda la guía.
- Escalera **«cómo llegar al concepto»**: seis pasos que derivan la idea de los datos, en vez de anunciarla.
- Fórmulas con **LaTeX** (KaTeX), figuras incrustadas y tablas.
- Práctica de **recuperación activa** con respuestas ocultas.
- **Plan de repaso espaciado** y tareas de transferencia.
- Estética *papercraft* en terracota, con animaciones discretas.
- Un solo archivo de salida: sin servidor, sin build, sin carpetas que se pierdan.

## Instalación

Requiere Python 3.10+ y, solo para recompilar el CSS, [Sass](https://sass-lang.com/):

```bash
npm i -g sass
```

El CSS compilado (`estilos/teacher.css`) ya está en el repositorio, así que la herramienta funciona sin Sass.

## Uso

```bash
python teacher.py leccion.md \
  --salida Guia_Tema.html \
  --titulo "De la potencia a la energía" \
  --subtitulo "Por qué 120 vatios no son 120 vatios-hora" \
  --materia "Cálculo Integral" \
  --acento "#b4552f" \
  --abrir
```

## Formato del Markdown

```md
# Título
> Idea central en una frase.

::: objetivo
Qué podrá hacer el estudiante al terminar.
:::

## El problema {problema}
## El concepto {concepto}
## Historia del concepto {historia}
## Cómo llegar al concepto {llegar}
## Qué llevarte de este tema {cierre}

Q: Pregunta de recuperación.
R: Respuesta oculta.
```

`python teacher.py --catalogo` lista todos los componentes con su sintaxis, un ejemplo y el error típico.

## Contrato

Una guía que no lo cumple **no se genera**. El motor mide el documento y dice qué falta:

```bash
python teacher.py leccion.md --validar
```

```
[  ok  ] 11 secciones
[  ok  ] historia: 4 párrafos, sin viñetas
[ error] llegar (línea 48): 3 pasos, mínimo 4 — observa, compara, cuantifica, nombra
[ error] línea 17: hay una tabla con cifras y ningún ::: desglose
```

Obligatorios hoy: `objetivo`, `prerequisito`, `dominio`, `historia`, `llegar`, `plan`, `transferencia`, `fuentes`; más cuatro preguntas Q/R. El `dominio` exige un `::: glosario` con mínimo 4 términos desplegables, las `{miradas}` exigen `::: pestanas` con mínimo 3 enfoques, y `{fuentes}` exige 3 referencias con año. Si una tabla trae cifras, exige `::: desglose`. Los umbrales viven en [`componentes/contrato.json`](componentes/contrato.json), que es la misma fuente que lee el validador.

La razón de fondo: «sé claro y profundo» no es verificable; «la historia tiene al menos tres párrafos y cero viñetas» sí. Un agente nuevo no tiene que leer un manual: ejecuta, ve lo que falta y corrige.

## Sistema de diseño

```
estilos/_tokens.scss    colores, tipografía y espacio (fuente de verdad)
estilos/teacher.scss    componentes
estilos/teacher.css     compilado que consume teacher.py
```

```bash
sass estilos/teacher.scss estilos/teacher.css --style=expanded
```

Reglas tipográficas sustentadas en evidencia: cuerpo de 19,5 px, interlineado 1,6, columna de ~70 caracteres, sin justificar (WCAG 1.4.8) y contraste AA.

## Por qué está diseñado así

| Decisión | Respaldo |
|---|---|
| Recuperación activa en vez de releer | Roediger & Karpicke (2006): a una semana, testeo supera a repaso en ~21 % |
| Plan de repaso espaciado | Cepeda et al. (2006): intervalo óptimo ≈ 10-20 % del tiempo de retención |
| Derivar el concepto antes de nombrarlo | Efecto de generación y autoexplicación (d ≈ 0,54-0,56) |
| Dificultad calibrada | Bjork: las dificultades deseables mejoran la retención aunque empeoren la fluidez percibida |
| Una idea por sección | Carga cognitiva (Sweller) |
| Cuerpo 19,5 px e interlineado 1,6 | Rello, Pielot & Marcos (2016): mejor comprensión desde 18 pt |

Los papers están en [`papers/`](papers/), con un resumen de qué sostiene cada uno y su entrada BibTeX. La decisión de no migrar a TypeScript está en [`docs/decision-motor.md`](docs/decision-motor.md).

## Licencia

MIT. El motor de fórmulas es [KaTeX](https://katex.org/), cargado por CDN.
