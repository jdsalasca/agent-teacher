# Decisión: motor de generación

**Estado:** aceptada · **Fecha:** 2026-11-07

## Contexto

`teacher` produce guías de estudio estáticas que se abren con doble clic y funcionan sin servidor. La pregunta era si convenía reescribirlo en TypeScript con React y una carpeta de componentes reutilizables, para lograr páginas "más lindas" y reutilizables.

## Opciones

| Opción | Ventaja | Costo |
| --- | --- | --- |
| **Python + plantilla** (actual) | Cero dependencias de ejecución, un archivo de salida, arranque instantáneo, funciona sin internet (salvo KaTeX) | Interactividad limitada; el HTML se arma con cadenas |
| **TypeScript + React + Vite** | Componentes tipados, estado, animaciones complejas, ecosistema | Node, `node_modules`, build, servidor o exportación estática; 300 MB de dependencias para generar un HTML |
| **Astro + islas** | HTML estático con islas interactivas | Build, dependencias, y el contenido seguiría viviendo en Markdown |

## Decisión

Se mantiene **Python**. La razón principal no es el gusto: el producto final es un **documento estático**. React brilla cuando hay estado compartido y re-render, y aquí no hay ninguno: el estudiante lee, despliega respuestas y sigue un plan. Cambiar de motor agregaría una cadena de build sin mejorar lo que ve el usuario.

Lo que sí se adoptó del mundo frontend:

- **Sistema de diseño en SCSS** con tokens y componentes (`estilos/`), compilado con Sass.
- **Componentes reutilizables de facto**: los bloques (`::: ejemplo`, `::: llegar`, `::: desglose`) son componentes semánticos con estilos propios, documentados en `AGENTS.md`.

## Cuándo revisar esta decisión

Se justifica migrar si aparece alguna de estas necesidades:

1. **Persistencia de progreso** por guía (qué preguntas respondió, cuándo toca repasar).
2. **Programador de repaso** que genere la sesión del día a partir de un historial.
3. **Editor visual** para que el estudiante arme sus propias guías.
4. **Métricas** de uso o de aciertos.

En ese escenario el camino razonable no es reescribir todo: se conserva el generador y se añaden **islas interactivas** (Astro o Web Components) que hablen con `localStorage`.

## Consecuencias

- El repositorio no necesita `package.json` para funcionar; solo Sass si se cambia el diseño.
- La interactividad actual es CSS + ~40 líneas de JavaScript sin dependencias.
- Si se migra, el Markdown y el SCSS se conservan: el contenido no depende del motor.
