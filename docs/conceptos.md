# Conceptos del proyecto

Glosario de las piezas del asistente: qué son, por qué están así y cómo
explicarlas. Complementa [arquitectura.md](arquitectura.md), que explica **el
orden de lectura**.

---

## 1. El asterisco: desempaquetado de listas

En `app/router.py`, la lista de comandos se arma así:

```python
CommandRouter(
    [
        *datetime_commands(),
        *wikipedia_commands(summarize),
        *browser_commands(open_url),
        *media_commands(play_on_youtube, search_on_internet),
        *stocks_commands(last_price),
        *jokes_commands(fetch_joke),
        *hardware_commands(),
        exit_command(),
    ]
)
```

El `*` es **desempaquetado** (*unpacking*): "sacá los elementos de esta lista y
ponelos acá adentro".

Cada `xxx_commands()` devuelve una **lista** de comandos. Sin el `*`, quedaría
una lista de listas:

```python
[['datetime.hour', 'datetime.day'], ['wikipedia.summary'], 'session.exit']
#   3 elementos: lista, lista, string  -> el router fallaría
```

Con el `*` se aplana:

```python
['datetime.hour', 'datetime.day', 'wikipedia.summary', 'session.exit']
#   4 elementos, todos comandos
```

```text
[  📦📦📦  ]   sin *  -> 3 cajas
[  a b c d  ]   con *  -> 4 cosas sueltas
```

**Por qué `exit_command()` no lleva `*`:** porque devuelve **un** comando, no
una lista.

```python
def exit_command() -> Command:      # Command, no list[Command]
    ...

exit_command()                       # ok
*exit_command()                      # TypeError: 'KeywordCommand' is not iterable
```

> **Truco para leer código:** el `*` te dice que esa función devuelve *varios*.
> Si no lo tiene, devuelve *uno*.

---

## 2. `Callable`: el contrato de una función

`Callable` es un tipo que significa: *"esto es una función, y funciona así"*.

```python
Callable[[ARGUMENTOS], RETORNO]
```

| Parte       | Qué dice                                  |
| ----------- | ----------------------------------------- |
| `Callable`  | esto se puede llamar                      |
| `[...]`     | qué recibe (tipos de los parámetros)      |
| `...`       | qué devuelve (tipo de retorno)            |

### Los tipos que se usan en el proyecto

| Anotación                        | Se lee como                                                   |
| -------------------------------- | ------------------------------------------------------------- |
| `Callable[[], str]`              | función sin argumentos que devuelve texto                    |
| `Callable[[str], bool]`          | recibe texto, devuelve sí/no                                  |
| `Callable[[str], str \| None]`    | recibe texto, devuelve texto o nada                           |
| `Callable[[str], float \| None]`  | recibe texto, devuelve número decimal o nada                  |
| `Callable[[Context, str], None]`  | recibe contexto y texto, no devuelve nada                     |

### Por qué `float` y no `str` para los precios

```python
last_price: Callable[[str], float | None]
#                          ^^^^^^^^^^^^
#                     recibe un TICKER (texto), devuelve un NÚMERO
```

El ticker es texto (`"NVDA"`), pero el precio es un número (`100.5`). Permitir
aritmética sin convertir:

```python
# MAL: el precio es texto
precio = last_price("NVDA")   # "100.50"
total = float(precio) + 10    # hay que convertir cada vez

# BIEN: el precio ya es número
precio = last_price("NVDA")   # 100.5
total = precio + 10            # listo
```

### Por qué `None` y no `0`

`None` significa **"no pude obtenerlo"**, que es distinto de "el precio es cero".

```python
last_price(ticker) -> float | None
#                          ^^^^^^^^
#                     "un float, O no hay ninguno"
```

Una acción puede cotizar legitimately en 0. Si el tipo fuera `float` solo, no
podrías distinguir *"vale 0"* de *"no sé"*. El comando lo maneja explícito:

```python
price = last_price(ticker)
if price is None:
    context.voice.say("No pude encontrar la informacion de la accion")
    return
```

### Por qué `bool` para YouTube y el navegador

```python
open_url: Callable[[str], bool]         # ¿se abrió?
play_on_youtube: Callable[[str], bool]  # ¿se reprodujo?
```

Estas acciones solo te interesta **si funcionaron**, no qué devolvieron:

```python
if not play_on_youtube(song):
    context.voice.say("No pude reproducir la cancion en YouTube")
```

### Por qué `None` como retorno en los handlers

```python
Handler = Callable[[Context, str], None]
#                             ^^^^ no devuelve nada
```

Un handler **hace algo** (habla, guarda, abre) pero no devuelve nada útil:

```python
def farewell(context: Context, _text: str) -> None:
    context.voice.say(FAREWELL_MESSAGE)   # va a la voz, no se devuelve
```

El `None` documenta: "esta función produce un efecto, no un valor".

---

## 3. `CommandRouter`: es una clase

```python
class CommandRouter:
    def __init__(self, commands):
        self._commands = tuple(commands)

    def resolve(self, text):
        for command in self._commands:
            if command.matches(text):
                return command
        return None
```

| Concepto | En código              | Analogía      |
| -------- | ---------------------- | ------------- |
| Clase    | `class CommandRouter:` | el plano       |
| Objeto   | `CommandRouter([...])` | un auto concreto |
| Método   | `.resolve(texto)`      | la acción       |

El **auto**: la clase es el plano, el objeto es el auto concreto, el método es
"arrancar". En `build_router()` se crea el objeto:

```python
router = CommandRouter([...])   # acá nace el objeto
command = router.resolve(text)  # se usa el método
```

### Qué hace `__init__`

Recibe la lista de 12 comandos y la guarda. **No hace nada más.** El `self` es
"este objeto en particular".

El `tuple(commands)` convierte la lista en colección **inmutable**: una vez
armado el router, los comandos no se agregan ni se quitan.

### Qué hace `resolve`

Es un bucle que prueba comandos **en orden**. El primero cuyo `matches()`
reconoce el texto gana.

```text
Texto: "me corre valorant"
   │
   ▼
┌─────────────────────────┐
│  ¿abrir youtube?        │ no
├─────────────────────────┤
│  ¿wikipedia?            │ no
├─────────────────────────┤
│  ¿hora?                 │ no
├─────────────────────────┤
│  ¿hardware.game?        │ ¡SÍ!  ← el router se detiene acá
└─────────────────────────┘
   │
   ▼
devuelve ese comando
```

El router **solo elige**. No habla ni ejecuta. Eso lo hace `command.execute()`
después.

---

## 4. `Session` vs. `Context`

Los dos nombres suenan parecidos pero guardan cosas distintas.

| Aspecto       | `Session`                    | `Context`                    |
| ------------- | ---------------------------- | ---------------------------- |
| **Qué es**        | estado / memoria            | kit de trabajo             |
| **Qué guarda**    | `hardware`, `detected`       | `session`, `voice`            |
| **Cambia?**       | Sí, se va llenando           | No, es fijo                   |
| **Cuántos**       | uno en toda la app           | uno, se pasa a todos        |
| **Quién lo recibe** | nadie, se accede directo   | cada comando                 |
| **Es `frozen`?**  | No (mutable)                 | Sí (inmutable)               |

### `Session` — la memoria

```python
@dataclass
class Session:
    hardware: HardwareProfile | None = None      # tu equipo armado
    detected: DetectedParts = field(...)         # componentes parciales
```

Guarda **datos que cambian** durante la conversación. Existe **una sola** en
toda la app.

| Momento              | `Session`                          |
| -------------------- | --------------------------------- |
| Al empezar           | vacío                              |
| "tengo una rtx 3060" | `detected.gpu_model = "rtx 3060"`  |
| "un ryzen 5"         | `detected.cpu_model = "ryzen 5"`   |
| "16 gb de ram"       | `detected.ram = 16`                |
| (los 3 completos)    | `hardware = HardwareProfile(...)`  |

### `Context` — el kit de trabajo

```python
@dataclass(frozen=True)
class Context:
    session: Session        # la memoria
    voice: VoiceService     # la voz
```

**No guarda nada del usuario.** Es el bolsillo que cada comando recibe para
trabajar: acceso a la memoria **y** a la voz.

### La analogía

Una **reunión de trabajo**:

- **Session** = el cuaderno con las notas. Se va llenando.
- **Context** = lo que cada persona tiene en la mano: el cuaderno (Session) y un
  micrófono (voice).

El cuaderno se comparte. El bolsillo se pasa a cada participante.

### Cómo se usan

```python
# El Assistant crea UN context y lo pasa a todos
def run(self):
    context = Context(session=self._session, voice=self._voice)
    ...
        command.execute(context, text)   # ← el mismo para todos
```

Cada comando usa lo que necesita:

```python
context.voice.say("No entendi el pedido")           # la voz
if context.session.hardware is None:                # la memoria
    context.voice.say("Primero decime tus componentes")
```

### Por qué `Context` es `frozen`

`frozen=True` significa **inmutable**. Es el **límite de confianza** entre el
núcleo y los comandos:

```python
context.session.record_parts(parts)   # permitido: mutar la sesión
context.voice.say("Hola")             # permitido: hablar
context.session = Session()           # IMPOSIBLE: Context es frozen
```

Python lo impide. Un comando no puede reemplazar la sesión entera y romper el
estado de toda la conversación. Es una garantía del lenguaje, no una
convención.

---

## 5. ¿Por qué existe el `Context`?

Porque sin él cada comando recibe las cosas sueltas:

```python
# SIN contexto
def answer_game(session: Session, voice: VoiceService, text: str) -> None:
```

Y el contrato de handlers sería:

```python
Handler = Callable[[Session, VoiceService, str], None]
```

Funciona... hasta que necesitás **una dependencia más**. Y hay 10 comandos:

```python
# Con una cosa más, el problema explota en los 10
Handler = Callable[[Session, VoiceService, Repositorio, Logger, str], None]
```

### Los 4 problemas que resuelve

**1. Todos los comandos se ven iguales.** Sin contexto, cada feature inventa su
firma. Con contexto, todos tienen la misma: `execute(context, text)`.

**2. El router se mantiene simple.** Siempre `command.execute(context, text)`.
Si la firma creciera, el router también tendría que cambiar.

**3. Marca un límite de permisos.** `frozen=True` garantiza que un comando no
pueda romper el estado global.

**4. Los tests son triviales.** El `FakeVoice` entra una vez:

```python
context = Context(session=Session(), voice=FakeVoice())
command.execute(context, text)   # ejecuta sin hablar de verdad
```

### El patrón: objeto de parámetros

Esto es un **parameter object**: un patrón clásico de refactoring.

> Si un grupo de parámetros se pasa siempre junto, convertilo en un objeto.

Acá el "grupo siempre junto" es `session` + `voice`.

| Aspecto            | Parámetros sueltos                | `Context`                    |
| ------------------ | --------------------------------- | ---------------------------- |
| Firma del handler  | Cambia si agregás una dependencia | Siempre `[[Context, str], None]` |
| Tocar al agregar   | 10 comandos + router              | 1 clase                      |
| garantía de estado | Ninguna                           | `frozen=True`                |
| Claridad           | `f(voz, sesión, texto)`           | `f(context, texto)`          |

---

## 6. Inyección de Dependencias

El nombre general de la técnica es **Inyección de Dependencias** (*Dependency
Injection*, DI). El proyecto usa dos variantes.

### Por constructor — objetos

```python
class Assistant:
    def __init__(self, voice: VoiceService, router: CommandRouter, ...):
        self._voice = voice
        self._router = router
```

Acá creás un **objeto** (`VoiceService`, `CommandRouter`) y lo pasás. Es DI
clásica.

### Por parámetro — funciones

```python
def stocks_commands(last_price: Callable[[str], float | None]) -> list[Command]:
```

Acá no creás ningún objeto. Pasás **la función suelta**. Se llama **inyección de
funciones**. Es la variante funcional, más ligera, para cuando la dependencia
es una sola operación.

### El problema que resuelve

Sin DI, cada feature se acopla a su librería:

```python
# SIN DI — la feature depende de yfinance
def stocks_commands():
    import yfinance
    def answer(context, text):
        price = yfinance.Ticker(ticker).info   # atado a yfinance
```

Con DI:

```python
# CON DI — la feature no sabe de dónde viene la función
def stocks_commands(last_price):
    def answer(context, text):
        price = last_price(ticker)   # solo "llamá a esta función"
```

| Problema           | Sin DI                       | Con DI              |
| ------------------ | ---------------------------- | ------------------- |
| Acoplamiento       | sabe de `yfinance`           | no sabe nada        |
| Testeable          | necesita internet            | corre en cualquier lado |
| Reemplazable       | hay que monkeypatchear       | pasás una lambda    |

### Cómo se conecta (composition root)

Todo se conecta en **un solo lugar**, `create_assistant()`:

```python
def create_assistant() -> Assistant:
    return Assistant(
        voice=VoiceService(),                       # ← objeto real
        router=build_router(
            summarize=wikipedia_client.summarize,   # ← función real
            last_price=last_price,
            ...
        ),
    )
```

Este lugar se llama **composition root** (raíz de composición). Es el único
punto del proyecto que sabe qué librerías existen.

### Duck typing

Python no necesita interfaces. Basta con que el objeto tenga el método:

```python
open_url(YOUTUBE_URL)   # solo necesita que sea llamable
```

- En producción: `webbrowser.open`
- En tests: una lambda

Ambos cumplen. No hay `isinstance`, ni protocolo, ni herencia. El `Callable` solo
**documenta** el contrato.

---

## Resumen en una línea cada cosa

| Pieza             | Qué es en una frase                                            |
| ----------------- | -------------------------------------------------------------- |
| `*`               | Desempaquetar una lista de comandos en otra lista              |
| `Callable`        | El tipo "esto es una función, y funciona así"                  |
| `CommandRouter`   | Una clase que elige el primer comando que reconoce el pedido  |
| `Session`         | La memoria de la conversación (equipo, componentes parciales)   |
| `Context`         | El kit que recibe cada comando (memoria + voz), inmutable      |
| DI                | Pasar las dependencias por parámetro en vez de crearlas        |
| Duck typing       | No importa el tipo, solo que tenga el método                  |

---

## Dónde mirar el código

| Para entender            | Archivo                  |
| ------------------------ | ------------------------ |
| El asterisco y el router | `app/router.py`          |
| La memoria y el kit      | `app/session.py`         |
| Los contratos            | `shared/command.py`      |
| La inyección             | `app/assistant.py`       |
| Un ejemplo de DI         | `features/stocks/commands.py` |