# Arquitectura del Asistente de Videojuegos

Guía de lectura del código

---

## La regla

**Arrancá por el medio, no por el principio.**

El dominio (`features/hardware/`) es lo que el proyecto *es*. La infraestructura
(`app/`, `shared/`) es lo que lo sostiene. Si aprendés la plumbing primero, no
tenés contexto para entender por qué existe.

| Zona                        | Qué representa                                |
| --------------------------- | --------------------------------------------- |
| `features/hardware/`        | **El dominio**: juegos, componentes, requisitos |
| `features/*/commands.py`    | **La costura**: texto → dominio → voz           |
| `app/`, `shared/`           | **La plumbing**: bucle, ruteo, estado, voz      |
| `asistente.py`              | **La promesa**: crear y correr                  |

---

## Fase 0 — Mapa mental (5 min)

No leas código. Respondé esto con lo que ya sabés:

- **¿De qué trata?** → asistente de voz gamer, dice si un juego te corre
- **¿Qué entra?** → tu voz (micrófono → texto)
- **¿Qué sale?** → tu voz (texto → parlante)
- **¿Qué más hace?** → Wikipedia, acciones, YouTube, chistes, hora
- **¿Qué NO hace?** → no guarda archivos, no tiene base de datos, no necesita
  internet salvo para Wikipedia, Google y las acciones

Si podés contestar eso, ya tenés el 80% del proyecto. El resto es detalle.

---

## Fase 1 — La promesa (10 min)

Leé **exactamente dos archivos**, en este orden.

### `asistente.py` (5 líneas)

```python
from app.assistant import create_assistant

if __name__ == "__main__":
    create_assistant().run()
```

**Qué te dice sin leer nada más:** el proyecto entero se puede resumir en una
función que *crea* algo y lo *corre*. Todo lo demás son detalles de qué se crea.

> **Checkpoint:** si alguien te pregunta "¿qué hace `asistente.py`?", la
> respuesta es "nada interesante, delega". Ese es el punto.

### `README.md`, sección *Flujo principal* (5 min)

Guardá este diagrama, es el mapa de todos los que vengas después.

```text
asistente.py
  -> create_assistant()          arma router + features + voz
    -> Assistant.run()           saluda y entra al bucle
      -> voice.listen()          transcribe el pedido
        -> router.resolve(text)  primer comando que lo reconoce
          -> command.execute(context, text)
            -> feature            (parser + dominio + voz)
```

> **Checkpoint:** ¿sabés decir de memoria qué hace `router.resolve`? Si no, no
> sigas.

---

## Fase 2 — Un feature completo, de punta a punta (45 min)

Esta es la fase que importa. No leas todas las features: leé **una** entera y
entendé el patrón. Cuando lo entiendas, las otras seis son variaciones.

Elegí **`hardware/`** porque es el dominio del proyecto y el más rico.

### 2.1 `data.py` — los hechos (5 min)

Leé los tres diccionarios: `GAMES`, `GPUS`, `CPUS`.

```python
"rtx 3060": GpuSpec(level=7, vram=12),
"ryzen 5": 5,
```

**Prestá atención a esto:** el nivel no es un número real de FPS ni una spec
técnica. Es un **número comparable**. Alguien decidió que una RTX 3060 "vale"
un 7 y una RTX 4090 vale un 10.

> **Pregunta para después:** ¿por qué guardan `level` en vez de los specs
> técnicos reales? La respuesta es: el objetivo es *"¿te corre?"*, no *"¿cuántos
> FPS?"*.

### 2.2 `models.py` — el vocabulario (10 min)

Cuatro dataclasses, en este orden:

| Clase                | Qué representa                     | ¿Completo?         |
| -------------------- | ---------------------------------- | ------------------ |
| `HardwareProfile`    | el equipo del usuario              | siempre `int`      |
| `Spec`               | un conjunto de requisitos          | siempre `int`      |
| `GameRequirements`   | los dos `Spec` de un juego         | —                  |
| `DetectedParts`      | lo que detectamos **de a uno**     | puede ser `None`   |

El truco es que son **dos conceptos distintos**:

- `DetectedParts` está **a medio camino** (puede tener `gpu_model=None`)
- `HardwareProfile` está **terminado** (todos los campos son `int`)

Por eso el `None` en uno y no en el otro.

Fijate también en `missing_components`:

```python
@property
def missing_components(self) -> tuple[str, ...]:
```

Devuelve una tupla de strings: `("cpu", "ram")`. Eso se usa directo para armar
el mensaje *"Anote. Todavia me falta cpu, ram"*. El dato y la presentación
juntos en una sola propiedad.

### 2.3 `parser.py` — la lógica pura (10 min)

Acá está el corazón técnico.

```text
find_ram(text)       -> int | None
find_gpu(text)       -> str | None
find_cpu(text)       -> str | None
find_game(text)      -> str | None
detect_parts(text)   -> DetectedParts
build_profile(parts) -> HardwareProfile | None
```

`RAM_PATTERNS` son dos regex porque hay dos formas de decirlo:

```python
re.compile(r"(\d+)\s*(?:gb|gigas?)?\s*(?:de\s*)?ram")   # "16 de ram", "16 gb de ram"
re.compile(r"ram\D{0,12}?(\d+)")                         # "ram 16", "ram: 16"
```

Y prestá mucha atención al **contraste con la app**:

- `parser.py` **no importa nada**. Cero librerías.
- No habla, no guarda estado, no sabe que existe un micrófono.

Eso es lo que lo hace testeable. Si este archivo importara `pyttsx3`, los tests
no correrían en ningún lado.

> **Checkpoint:** ¿puedés explicar por qué `build_profile` devuelve `None` en
> vez de un perfil incompleto?

### 2.4 `compatibility.py` — la regla (5 min)

Son **18 líneas**. Leelas enteras:

```python
def check_compatibility(profile: HardwareProfile, game: str) -> str:
    requirements = GAMES.get(game)
    if requirements is None:
        return UNKNOWN_GAME_MESSAGE
    if requirements.recommended.is_met_by(profile):
        return f"Si, {game} te corre en calidad alta (recomendado)"
    if requirements.minimum.is_met_by(profile):
        return f"Si, {game} te corre, pero en calidad baja (minimo)"
    return f"No, no te corre {game} con esos componentes"
```

Notá la estructura: **early returns**. Cada caso sale apenas se decide. No hay
`else` anidados ni flags.

Notá también que devuelve **texto**, no hace nada. La función que decide y la
función que habla están separadas.

### 2.5 `commands.py` — la costura (15 min)

Acá se juntan las dos mitades:

```python
def answer_game(context: Context, text: str) -> None:
    game = find_game(text)
    if game is None:
        context.voice.say(UNKNOWN_GAME_MESSAGE)
        return
    profile = context.session.hardware
    if profile is None:
        context.voice.say("Primero decime tus componentes")
        return
    context.voice.say(check_compatibility(profile, game))
```

Leé eso tres veces. Es el patrón que se repite en todas las features:

```text
extraer  ->  si falta algo, avisar y salir  ->  si no, usar el dominio  ->  hablar
```

Y después `RecordComponents`, el comando custom:

```python
@dataclass(frozen=True)
class RecordComponents:
    name: str = "hardware.components"
    ends_session: bool = False

    def matches(self, text: str) -> bool:
        if not detect_parts(text).is_empty:
            return True
        return any(contains_keyword(text, keyword) for keyword in COMPONENT_KEYWORDS)

    def execute(self, context: Context, text: str) -> None:
        parts = detect_parts(text)
        report_detected(parts)
        context.session.record_parts(parts)
        ...
```

> **Checkpoint:** si podés describir `RecordComponents` sin mirar el código,
> entendiste el feature.

---

## Fase 3 — Verificar (15 min)

Ahora corré los tests de hardware **con el debugger puesto**. Esto vale más que
leer.

```bash
python -m unittest tests.test_hardware.HardwareParserTest.test_detecta_los_componentes_en_una_frase -v
```

Y después leé `tests/test_hardware.py` greppeando los datos de entrada:

```bash
grep -n "tengo una" tests/test_hardware.py
```

Vas a ver cosas como:

```python
"tengo una rtx 3060, un ryzen 5 y 16 de ram"
```

Esos strings son **contratos**: te dicen exactamente qué frases tienen que
funcionar. Es la mejor documentación del comportamiento esperado, porque además
**se ejecuta**.

---

## Fase 4 — Las otras features: confirmar el patrón (20 min)

No las leas completas: es el mismo esqueleto.

| Feature      | Fijate en                                                                     |
| ------------ | ----------------------------------------------------------------------------- |
| `wikipedia/` | `errors.py` (excepciones propias) + `client.py` (el único que importa la lib)  |
| `stocks/`    | `quotes.py` (devuelve `float \| None`) + `commands.py`                          |
| `media/`     | `playback.py` (devuelve `bool`) + `commands.py`                                 |
| `datetime/`  | `time.py` (puro, recibe el momento) + `commands.py`                            |
| `browser/`   | un solo archivo: no necesita adaptador porque usa `webbrowser` (stdlib)         |
| `jokes/`     | el más chico, sirve de referencia                                              |

**El patrón universal:**

```text
features/<nombre>/
  <algo>.py      <- la lógica, no importa librerías
  commands.py    <- conecta el texto con la lógica y la voz
```

Y notá esto, que es **la clave de la arquitectura**:

```python
# features/stocks/commands.py
def stocks_commands(last_price: Callable[[str], float | None]) -> list[Command]:
```

`commands.py` **recibe la función, no la importa**. La librería real se conecta
en otro lado. Por eso los tests andan sin `yfinance` instalado.

> **Checkpoint:** ¿dónde se conecta `yfinance` de verdad? La respuesta es: en
> `app/assistant.py`, dentro de `create_assistant()`.

---

## Fase 5 — El núcleo (30 min)

Recién acá, porque ya sabés qué hay que conectar.

### 5.1 `app/session.py` (10 min) — el estado

```python
@dataclass
class Session:
    hardware: HardwareProfile | None = None
    detected: DetectedParts = field(default_factory=DetectedParts)

@dataclass(frozen=True)
class Context:
    session: Session
    voice: VoiceService
```

`Session` es mutable (el estado cambia), `Context` es frozen (lo que se le pasa a
un comando no se toca).

> **Pregunta:** ¿por qué una es frozen y la otra no?

### 5.2 `shared/command.py` (10 min) — el contrato

Este archivo es el **contrato de todo el proyecto**:

```python
class Command(Protocol):
    name: str
    ends_session: bool

    def matches(self, text: str) -> bool: ...
    def execute(self, context: Context, text: str) -> None: ...
```

Y después la implementación genérica:

```python
@dataclass(frozen=True)
class KeywordCommand:
    name: str
    keywords: tuple[str, ...]
    handler: Handler
    ends_session: bool = False
```

**Lo importante:** `Command` es un `Protocol`, no una clase base. No se hereda
nada. Es **estructural**: si tenés esos 4 miembros, sos un comando. Por eso
`RecordComponents` y `KeywordCommand` conviven en la misma lista sin relación
entre sí.

El tipo del handler:

```python
Handler = Callable[["Context", str], None]
```

Siempre recibe `(context, text)`. Por eso los handlers que no usan el texto lo
declaran como `_text`.

### 5.3 `app/router.py` (10 min) — el selector

El router es **trivial**, y es correcto que lo sea:

```python
def resolve(self, text: str) -> Command | None:
    for command in self._commands:
        if command.matches(text):
            return command
    return None
```

Y después `build_router()`. Prestá atención al **orden**: es el orden de prioridad
de negocio.

```python
def build_router(*, summarize, open_url, play_on_youtube, ...):
    return CommandRouter([
        *datetime_commands(),
        *wikipedia_commands(summarize),
        *browser_commands(open_url),
        *media_commands(play_on_youtube, search_on_internet),
        *stocks_commands(last_price),
        *jokes_commands(fetch_joke),
        *hardware_commands(),
        exit_command(),
    ])
```

> Si te preguntan *"¿cómo agrego un comando nuevo?"*, la respuesta es: escribís
> la feature y agregás **una línea** acá. No tocás el bucle.

---

## Fase 6 — La plumbing (20 min)

### 6.1 `app/assistant.py` (15 min) — el bucle

Leé `run()` primero. Es el corazón de la app:

```python
try:
    while True:
        text = self._voice.listen()
        if text is None or not text.strip():
            continue

        text = text.lower()
        print("Comando recibido:", text)
        command = self._router.resolve(text)
        if command is None:
            self._voice.say(FALLBACK_MESSAGE)
            continue

        command.execute(context, text)
        if command.ends_session:
            break
except KeyboardInterrupt:
    print()
    self._voice.say(GOODBYE_MESSAGE)
```

Es **un solo ciclo, sin `if/elif`**. Toda la lógica de qué hacer está en los
comandos.

Después leé `create_assistant()`. Y notá esto:

```python
def create_assistant() -> Assistant:
    import webbrowser
    from features.jokes.jokes import tell_joke
    ...
```

**Los imports están adentro de la función, a propósito.** Ese es el detalle más
importante del archivo: permite que el núcleo sea importable sin las librerías
instaladas. Si los imports estuvieran arriba del archivo, los tests no correrían.

### 6.2 `shared/text.py` (5 min) — chiquito

Cuatro funciones:

| Función            | Qué hace                                                     |
| ------------------ | ------------------------------------------------------------ |
| `normalize`        | saca tildes y pasa a minúsculas (para comparar)              |
| `contains_keyword` | ¿el texto contiene la palabra? (ignorando tildes)            |
| `remove_words`     | saca palabras del texto, respetando límites de palabra       |
| `clean_text`       | deja el texto en una línea, listo para hablar                |

El `\b` en `remove_words` es una corrección de bug: el original hacía
`.replace("pon", "")` y borraba *"pon"* **dentro** de *"componentes"*.

---

## Fase 7 — El experimento que consolida todo (30 min)

Antes de explicar nada a nadie, hacé esto.

### Tracé un comando de punta a punta

Elegí `"me corre cyberpunk 2077"` y escribí en un papel **cada archivo que toca
y en qué línea**:

```text
asistente.py                 -> llama create_assistant().run()
app/assistant.py             -> voice.listen() devuelve el texto
                              -> router.resolve(text)
app/router.py                -> itera comandos
shared/text.py               -> contains_keyword normaliza
features/hardware/commands.py-> matches() True (keyword "corre")
app/assistant.py             -> command.execute(context, text)
features/hardware/commands.py-> find_game(text)
features/hardware/parser.py  -> busca en GAMES
features/hardware/commands.py-> profile is None -> "Primero decime tus componentes"
app/assistant.py             -> ends_session? False -> sigue el bucle
```

**Si podés escribir esa lista sin abrir el editor, entendiste el proyecto.**

### Agregá algo chiquito

Agregá un comando nuevo. Sugerencia fácil: que `"cuantos fps"` dé una respuesta
fija. Tocás:

1. `features/hardware/commands.py` — un `KeywordCommand` más
2. `app/router.py` — una línea en `build_router()`
3. `tests/test_router.py` — el test

**No tocás** el bucle, ni `asistente.py`, ni los otros features. Esa es la
prueba de que la arquitectura sirve.

---

## Resumen: el orden en 7 líneas

| Fase | Qué                                        | Tiempo |
| ---- | ------------------------------------------ | ------ |
| 0    | Mapa mental: qué hace, no cómo             | 5 min  |
| 1    | `asistente.py`: la promesa                 | 10 min |
| 2    | `features/hardware/`: un feature COMPLETO  | 45 min |
| 3    | Los tests de hardware: verificar           | 15 min |
| 4    | Las otras features: confirmar el patrón    | 20 min |
| 5    | `app/` y `shared/`: la plumbing            | 30 min |
| 6    | El bucle + el trace: consolidar            | 30 min |
| 7    | Agregar algo: la prueba final              | 30 min |

---

## Preguntas frecuentes (y dónde está la respuesta)

| Pregunta                                                | Dónde está                                              |
| ------------------------------------------------------- | ------------------------------------------------------- |
| ¿Cómo agrego un comando?                                | `build_router()` en `app/router.py`                        |
| ¿Dónde se guarda el estado?                             | `Session`, en `app/session.py`                             |
| ¿Cómo maneja los errores de Wikipedia?                  | `client.py` traduce a `AmbiguousQuery` / `LookupFailed`    |
| ¿Por qué los tests corren sin internet?                 | Las features reciben funciones, no importan librerías     |
| ¿Qué pasa si agrego un juego a la base?                 | Nada: los tests parametrizados lo cubren solo              |
| ¿Cómo pruebo sin micrófono?                             | Fakes en `tests/doubles.py`                                |
| ¿Por qué `DetectedParts` y `HardwareProfile` son distintos? | Uno es parcial, el otro está completo                   |
| ¿Dónde está el punto de extensión?                      | `create_assistant()` en `app/assistant.py`                 |
| ¿Qué hace `ends_session`?                               | Le dice al bucle que termine después de ejecutar el comando |

---

## Cómo ejecutar la app

### Requisitos previos

| Requisito        | Detalle                                                     |
| ---------------- | ----------------------------------------------------------- |
| Python           | 3.10 o superior                                              |
| Micrófono        | Conectado y con permiso                                      |
| Internet         | Para voz, Wikipedia, Google, YouTube y acciones             |
| Sistema          | Windows (voz SAPI5) o macOS (voz en espanol del sistema)     |

### Instalar y correr

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar
python asistente.py
```

La voz se elige sola: primero intenta la de Windows, y si no esta, busca una en
espanol del sistema. Para ver cual usa:

```bash
python -c "from shared.voice import VoiceService; print(VoiceService().voice_id)"
```

### Si `PyAudio` falla al instalar

`PyAudio` siempre compila desde el codigo fuente.

**macOS**: necesita `portaudio`, y con el SDK de Xcode 27 hay que apuntar a un SDK
anterior porque el linker no reconoce `arm64e`.

```bash
brew install portaudio
SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
MACOSX_DEPLOYMENT_TARGET=13.0 \
pip install "PyAudio==0.2.14"
```

**Linux**:

```bash
sudo apt install portaudio19-dev python3-dev && pip install pyaudio
```

**Windows**: normalmente funciona directo con `pip`.

### Si `pip install` se corta y no instala nada

`pip` aborta todas las dependencias cuando una falla. Instalas por partes:

```bash
pip install pyttsx3 SpeechRecognition pywhatkit yfinance pyjokes wikipedia
```

### Entorno virtual (recomendado)

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
python asistente.py
```

### Correr los tests

```bash
python -m unittest discover -s tests -v
```

No necesitan micrófono, parlantes, navegador ni internet: corren en cualquier
lado, incluso sin las dependencias instaladas.

```bash
# Un solo test
python -m unittest tests.test_hardware.HardwareParserTest -v

# Ver la cobertura
python -m coverage run -m unittest discover -s tests
python -m coverage report --include="app/*,features/*,shared/*"
```

### Comandos de voz que podés probar

| Decí                                     | Qué hace                            |
| ---------------------------------------- | ----------------------------------- |
| "tengo una rtx 3060, un ryzen 5 y 16 gb de ram" | Anota tu equipo             |
| "me corre cyberpunk 2077"                | Veredicto de compatibilidad          |
| "que hora es" / "que dia es hoy"          | Hora y fecha                         |
| "busca en wikipedia lionel messi"        | Lee un resumen                       |
| "abrir youtube" / "abrir google"          | Abre el navegador                    |
| "busca en internet requisitos gta 5"      | Busca en Google                      |
| "reproducir bohemian rhapsody"            | Reproduce en YouTube                 |
| "precio de la accion de nvidia"           | Precio actual                        |
| "contame un chiste"                       | Cuenta un chiste                     |
| "adios" / "salir"                         | Cierra el asistente                  |
| `Ctrl + C`                                | También cierra                      |

---

## Diagrama de arquitectura

### Capas

```text
+----------------------------------------------------------+
|  asistente.py          entry point, 4 lineas             |
+----------------------------------------------------------+
|  app/                  el nucleo                          |
|    assistant.py        bucle + composition root            |
|    router.py           CommandRouter + build_router       |
|    session.py          Session (estado) + Context        |
+----------------------------------------------------------+
|  shared/               building blocks                     |
|    command.py          Command (Protocol) + KeywordCommand|
|    text.py             normalizacion y limpieza           |
|    voice.py            VoiceService (hablar / escuchar)    |
+----------------------------------------------------------+
|  features/             una carpeta = una funcionalidad     |
|                                                          |
|    hardware/     [dominio principal]                      |
|      data.py           juegos, graficas, procesadores      |
|      models.py         HardwareProfile, Spec, ...         |
|      parser.py         logica pura (sin imports)          |
|      compatibility.py  la regla de min/recomendado        |
|      commands.py       comandos hablados                  |
|                                                          |
|    wikipedia/  [adaptador + comando]                     |
|    datetime/   [puro + comando]                          |
|    stocks/     [adaptador + comando]                     |
|    media/      [adaptador + comando]                     |
|    browser/    [comando]                                 |
|    jokes/      [adaptador + comando]                     |
+----------------------------------------------------------+
|  tests/                129 tests, sin deps externas       |
+----------------------------------------------------------+
```

### Flujo de una peticion

```text
  "tengo una rtx 3060, un ryzen 5 y 16 de ram"
                    |
                    v
        +-----------------------+
        |  VoiceService.listen  |   microfono -> texto
        +-----------------------+
                    |
                    v  "tengo una rtx 3060, un ryzen 5 y 16 de ram"
        +-----------------------+
        |   Assistant.run       |   .lower(), imprime
        +-----------------------+
                    |
                    v
        +-----------------------+
        | router.resolve(text)  |   primer comando que matchea
        +-----------------------+
                    |
                    v  RecordComponents
        +-----------------------+
        |  detect_parts(text)  |   -> DetectedParts("rtx 3060","ryzen 5",16)
        +-----------------------+
                    |
        +-----------+-----------+
        v                       v
+---------------+      +-----------------+
| report_detected|      | Session.record  |   estado de la conversacion
+---------------+      +-----------------+
                                |
                                v
                     +--------------------+
                     | missing_components |   ("gpu","cpu","ram")
                     +--------------------+
                          |             |
                    faltan         completos
                          v             v
              "Anote. Todavia    +-------------------+
               me falta ..."     | build_profile     | -> HardwareProfile(16,12,7,5)
                                +-------------------+
```

### Flujo de una consulta de juego

```text
  "me corre cyberpunk 2077"
                    |
                    v
        +-----------------------+
        | hardware.game         |   keyword "corre" / "me corre"
        +-----------------------+
                    |
                    v
        +-----------------------+
        | find_game(text)       |   busca en GAMES -> "cyberpunk 2077"
        +-----------------------+
                    |
        +-----------+-----------+
        v           v           v
    no hay     no hay        hay perfil
    juego      perfil
        |           |           |
        v           v           v
  "No tengo   "Primero     check_compatibility
  ese juego   decime tus       (puro, devuelve texto)
  en mi base  componentes"           |
                                  v
              "Si, cyberpunk 2077 te corre en calidad alta
               (recomendado)"
```

### Como se inyectan las dependencias

```text
  TESTS                          APLICACION
  ------                         ---------
                                  create_assistant()
  build_test_router()                 |
    |                                 |
    | MediaStub                       | play_on_youtube
    | WikipediaStub                   | wikipedia_client.summarize
    | PricesStub                      | last_price
    | JokeStub                        | tell_joke
    |                                 | VoiceService
    +--> build_router(...) <-----------+
              |
              v
        CommandRouter
          datetime_commands()
          wikipedia_commands(summarize)
          browser_commands(open_url)
          media_commands(play_on_youtube, search_on_internet)
          stocks_commands(last_price)
          jokes_commands(fetch_joke)
          hardware_commands()
          exit_command()
              |
              v
        [KeywordCommand, ..., RecordComponents]
```

Los comandos **no saben** de dónde vienen las funciones. Por eso los tests
corren sin `pywhatkit`, `yfinance`, `wikipedia` ni `pyjokes` instalados.

### Regla de dependencia

```text
  app/  ──────X──────>  pyttsx3, speech_recognition
  features/*/commands  ──────X──────>  wikipedia, yfinance,
                                              pywhatkit, pyjokes

  Solo 5 modulos importan librerias de terceros:
    shared/voice.py
    features/wikipedia/client.py
    features/stocks/quotes.py
    features/media/playback.py
    features/jokes/jokes.py

  Y ninguno lo importan los tests.
```