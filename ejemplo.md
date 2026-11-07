# De la potencia a la energía

> La potencia es un punto en el tiempo. La energía es el área debajo de esa curva.

::: objetivo
Explicar por qué 120 vatios no son 120 vatios-hora, estimar la energía de una bomba con sumas de Riemann y decidir cuándo la aproximación ya es suficientemente buena.
:::

::: prerequisito
Saber multiplicar y dividir, leer una tabla y aceptar que una hora tiene 60 minutos. Si puedes calcular cuánto gasta un bombillo de 100 W encendido dos horas, tienes todo lo necesario.
:::

## El problema del agricultor {concepto}

A las seis de la mañana la bomba arranca y el agua empieza a subir por el canal. Dos horas después se apaga. El agricultor mira el medidor y hace la cuenta que hace todo el mundo: «si gasta 120 vatios, y fueron dos horas, entonces fueron 240».

La cuenta está mal, y no por poco: se pasa en casi 27 vatios-hora. El error está en el punto de partida. La bomba no gastó 120 durante todo el tiempo: a las seis de la mañana apenas si llegaba a 100, y solo al final del riego tocó los 120. Multiplicar por el valor más alto es como calcular el precio de un mercado por el artículo más caro del carrito.

Lo que el agricultor necesita no es un número instantáneo, sino la suma de todo lo que fue consumiendo minuto a minuto. Y ahí empieza el problema de verdad: no hay un solo número que multiplicar, porque el consumo cambia en cada instante.

## La función que describe la bomba {concepto}

El ejercicio entrega la potencia como una función del tiempo:

$$f(t) = 100 + 5t^2$$

El 100 es el punto de partida: los vatios que consume apenas se enciende. El término $5t^2$ es lo que se va sumando con el tiempo, y crece cada vez más rápido porque va al cuadrado. En la hora 1 aporta 5 vatios; en la hora 2, aporta 20.

| Tiempo | Cálculo | Potencia |
| ---: | --- | ---: |
| 0 h | $100 + 5(0)^2$ | 100 W |
| 1 h | $100 + 5(1)^2$ | 105 W |
| 2 h | $100 + 5(2)^2$ | 120 W |

::: error
Decir «gastó 120 porque a las 2 horas tenía 120 vatios» es el error más común de todo el tema. El 120 es la rapidez con la que consumía en ese instante; la energía es lo que acumuló durante las dos horas.
:::

## Qué es el ancho de un pedazo {concepto}

Aquí aparece la palabra que más confunde. El **ancho** es simplemente **cuánto tiempo cubre cada pedazo** cuando partimos las dos horas.

$$\Delta t = \frac{2}{n}$$

Si partes las dos horas en 4 pedazos, cada uno mide media hora. Si las partes en 100, cada uno mide 0,02 horas, que son 72 segundos.

| Pedazos ($n$) | Ancho ($\Delta t$) | Equivale a |
| ---: | ---: | ---: |
| 1 | 2 h | las dos horas completas |
| 4 | 0,5 h | 30 minutos |
| 20 | 0,1 h | 6 minutos |
| 100 | 0,02 h | 72 segundos |

El ancho es lo que convierte vatios en vatios-hora. Un vatio solo no dice cuánto se gastó; hay que decir durante cuánto tiempo. Multiplicar la potencia por el ancho es exactamente eso.

## El primer cálculo: un solo pedazo {concepto}

Con un solo pedazo, las dos horas se toman como un bloque. La potencia al inicio es 100 vatios, así que se supone que la bomba gastó eso todo el tiempo.

::: desglose
## n = 1 → 200 W·h
- Ancho: 2 h ÷ 1 = 2 h
- Potencia al inicio del pedazo: f(0) = 100 + 5(0)² = 100 W
- Energía del pedazo: 100 W × 2 h = 200 W·h
- Comparación con el exacto: 213,33 − 200 = 13,33 W·h de error
- Lectura: se queda corto porque la bomba terminó gastando más de 100
:::

Doscientos no es «el resultado»: es la estimación más burda posible, la que se obtiene mirando solo el primer instante. Y sirve para algo: marca el piso. Cualquier estimación decente tiene que quedar por encima.

## Partir el tiempo en pedazos {concepto}

La idea para mejorar es sencilla: si el consumo cambia, no tomemos un solo bloque sino varios. Cada pedazo es un rectángulo: el ancho es el tiempo que cubre y la altura es la potencia al inicio de ese pedazo.

$$L_n = \sum_{i=0}^{n-1} f(t_i)\,\Delta t$$

![Con cuatro pedazos, cada rectángulo toma la altura del inicio del intervalo. El área que falta es el error de la aproximación.](figuras/riemann_n4.svg)

## De dónde salió esta idea {historia}

En 1854, un joven de 28 años llamado Bernhard Riemann tenía que dar una clase para poder enseñar en la Universidad de Gotinga. Podía elegir tres temas; eligió el que menos le convenía, el de las series trigonométricas, porque era el único que no había preparado. Se encerró a resolverlo y de ahí salió, sin buscarlo, su definición de integral.

El problema que tenía enfrente era este: los matemáticos ya sabían integrar funciones continuas —curvas sin saltos—, y Cauchy había dejado la definición como límite de sumas en 1823. Pero Fourier había demostrado que casi cualquier función podía escribirse como suma de senos y cosenos, y esas funciones se rompen, saltan y se disparan al infinito. La definición de Cauchy no alcanzaba.

Riemann hizo un cambio pequeño con consecuencias enormes: en vez de exigir que la función fuera continua, exigió que las sumas convergieran. Si al hacer los pedazos cada vez más pequeños la suma se estabiliza, entonces hay integral. Si no, no la hay. La integral dejó de ser una fórmula y se volvió una prueba de comportamiento.

La idea de sumar pedazos era mucho más vieja: Arquímedes ya calculaba áreas así en el siglo III antes de Cristo, y Leibniz había inventado el símbolo $\int$ en 1675 como una «S» alargada de *summa*, suma. Lo que Riemann agregó fue el criterio para saber cuándo esa suma vale. Por eso la suma lleva su nombre y no el de Leibniz.

::: nota
Durante casi dos siglos la intuición y el símbolo fueron los mismos: sumar pedazos cada vez más finos. Lo que cambió después no fue la idea, sino el rigor con que se decide cuándo la suma sirve.
:::

## Cómo llegar a la idea de convergencia {practica}

La tabla siguiente es el corazón del tema. No hace falta creerla: se puede leer.

| Pedazos | Ancho | Estimación | Error |
| ---: | ---: | ---: | ---: |
| 1 | 2 h | 200,00 | 13,33 |
| 4 | 30 min | 208,75 | 4,58 |
| 20 | 6 min | 212,35 | 0,98 |
| 100 | 72 s | 213,13 | 0,20 |
| exacto | — | 213,33 | 0 |

::: llegar
- Observa: con 1 pedazo faltan 13,33 para el exacto; con 4 faltan 4,58; con 20, 0,98; con 100, 0,20.
- Compara: al pasar de 4 a 20 pedazos el error se divide por 4,7; al pasar de 20 a 100, por 4,9. Cada vez que multiplicas los pedazos por cinco, el error baja casi cinco veces.
- Cuantifica: el error se comporta como $1/n$. Duplicar los pedazos reduce el error a la mitad; multiplicar por 10 lo reduce a la décima parte.
- Nombra: cuando al aumentar $n$ el error tiende a cero, se dice que la suma **converge** a la integral definida. Ese límite es, literalmente, la integral.
- Verifica: con 100 pedazos el error es 0,20 sobre 213,33, o sea 0,09 %; con 20 pedazos es 0,46 %. Los números confirman el patrón.
- Decide: para presupuestar alcanza con 20 pedazos; para facturar conviene 100 o un método de orden superior como Simpson.
:::

Y si quieres ver de dónde salen esas cifras, se despliegan una por una:

::: desglose
## n = 4 → 208,75 W·h
- Ancho: 2 h ÷ 4 = 0,5 h
- Potencias en los extremos izquierdos: f(0) = 100; f(0,5) = 101,25; f(1) = 105; f(1,5) = 111,25
- Suma de las alturas: 100 + 101,25 + 105 + 111,25 = 417,5 W
- Energía: 417,5 W × 0,5 h = 208,75 W·h
- Error: 213,33 − 208,75 = 4,58 W·h, un 2,15 %

## n = 20 → 212,35 W·h
- Ancho: 2 h ÷ 20 = 0,1 h (6 minutos)
- Suma de las 20 alturas: 2.123,5 W
- Energía: 2.123,5 W × 0,1 h = 212,35 W·h
- Error: 0,98 W·h, un 0,46 %

## n = 100 → 213,13 W·h
- Ancho: 2 h ÷ 100 = 0,02 h (72 segundos)
- Suma de las 100 alturas: 10.656,7 W
- Energía: 10.656,7 W × 0,02 h = 213,13 W·h
- Error: 0,20 W·h, un 0,09 %
- Lectura: el ancho es tan pequeño que cada pedazo casi no cambia de potencia
:::

## Tres maneras de aproximar lo mismo {practica}

::: enfoques
- **Rectángulos por izquierda** — toman la altura al inicio de cada pedazo. Si la función crece, subestiman. Es la más simple de explicar y la que usa este ejercicio.
- **Trapecios** — unen los extremos de cada pedazo con una recta en vez de un escalón. Con la misma información bajan el error de 2,15 % a 0,03 % en el caso de cuatro pedazos.
- **Simpson** — ajusta una parábola cada dos pedazos. Con 20 pedazos el error ya es de millonésimas; se usa cuando hay que facturar, no cuando hay que decidir.
:::

## Procedimiento para resolver con cuatro pedazos {practica}

::: pasos
1. Calcula el ancho: $\Delta t = 2/4 = 0{,}5$ h.
2. Evalúa la potencia en el extremo izquierdo de cada pedazo: 100; 101,25; 105 y 111,25 W.
3. Suma las cuatro alturas: 417,5 W.
4. Multiplica por el ancho: $417{,}5 \times 0{,}5 = 208{,}75$ W·h.
5. Compara con el exacto y reporta el error: $213{,}33 - 208{,}75 = 4{,}58$ W·h, un 2,15 %.
:::

## Practica antes de seguir {practica}

Q: ¿Qué unidades tiene $f(2)$?
R: Vatios. Es la potencia en el instante $t = 2$, no una energía.

Q: ¿Por qué con un solo pedazo da 200 y no 213,33?
R: Porque usa la potencia del arranque, 100 W, durante las dos horas completas. La bomba terminó en 120 W, así que esa suposición se queda corta.

Q: ¿Qué es exactamente el ancho?
R: El tiempo que cubre cada pedazo: las dos horas divididas entre el número de pedazos. Con 4 pedazos son 0,5 h; con 100, 0,02 h.

Q: ¿Qué pasa con el error cuando duplicas los pedazos?
R: Se reduce a la mitad, porque el error se comporta como 1/n.

Q: ¿La suma se acerca por arriba o por abajo del valor exacto?
R: Por abajo, porque toma la altura en el extremo izquierdo y la función es creciente. Con el extremo derecho se acercaría por arriba.

Q: ¿Qué cambiaría si la bomba arrancara en 120 y bajara a 100?
R: La suma por izquierda pasaría a sobreestimar, porque el primer valor sería el más alto. El método no cambia; cambia el signo del error.

## Plan para no olvidarlo {practica}

::: plan
- Hoy — Leer la guía y responder las preguntas sin mirar.
- Día 2 — Rehacer el desglose de n = 4 sin ver los pasos.
- Día 5 — Explicarlo en voz alta, en tres minutos, a alguien que no sepa del tema.
- Día 12 — Resolver el caso de una bomba que se apaga a la hora 1.
- Día 25 — Aplicarlo a un problema de otro contexto sin mirar la guía.
:::

::: transferencia
Un plan de datos móviles «ilimitado con reducción» cobra distinto según el consumo de cada hora: es una suma de pedazos con precios distintos.
Una app que sube su uso de CPU de 100 a 120 unidades en dos horas consume energía; el cálculo es idéntico, solo cambian las unidades.
Escribe la suma para 8 pedazos y compárala con la tabla.
Busca en tu carrera un caso donde tengas la tasa y necesites el acumulado.
:::
