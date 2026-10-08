# Asistente Virtual de Hardware para Videojuegos

Asistente de voz en Python pensado para el mundo gamer. Escucha tus ordenes por
microfono, responde con voz y puede decirte si un videojuego te corre segun los
componentes (GPU, CPU y RAM) que le indiques.

El proyecto usa exclusivamente las librerias de la consigna: `pyttsx3`,
`speech_recognition`, `pywhatkit`, `yfinance`, `pyjokes`, `webbrowser`,
`datetime` y `wikipedia`.

---

## Funcionalidades

- **Conversion de texto a voz**: el asistente responde hablando (`pyttsx3`).
- **Reconocimiento de voz**: escucha tus comandos por microfono (`speech_recognition`).
- **Compatibilidad de juegos**: compara tus componentes con los requisitos minimos
  y recomendados de una base de datos local y te dice si el juego corre.
- **Hora y fecha**: informa la hora y el dia actuales (`datetime`).
- **Wikipedia**: busca informacion de cualquier tema (`wikipedia`).
- **Buscar en internet**: abre una busqueda de Google (`pywhatkit`).
- **Reproducir canciones en YouTube**: busca y reproduce (`pywhatkit`).
- **Abrir sitios web**: YouTube y Google (`webbrowser`).
- **Precio de acciones**: valor actual de marcas de hardware y estudios (`yfinance`).
- **Chistes**: cuenta un chiste en espanol (`pyjokes`).

---

## Requisitos

- **Sistema operativo**: Windows (usa la voz SAPI5 `TTS_MS_ES-ES_HELENA_11.0`) o
  macOS (usa una voz en espanol del sistema como plan B).
- **Python**: 3.10 o superior (probado en 3.12).
- **Microfono** conectado y funcionando.
- **Conexion a internet**: necesaria para el reconocimiento de voz, Wikipedia,
  la busqueda en internet, YouTube y las acciones.

---

## Instalacion

1. Clonar el repositorio:

   ```
   git clone <URL_DEL_REPOSITORIO>
   cd Asistente
   ```

2. (Opcional, recomendado) Crear un entorno virtual:

   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Instalar las dependencias:

   ```
   pip install -r requirements.txt
   ```

4. Ejecutar el asistente:

   ```
   python asistente.py
   ```

### Si PyAudio falla al instalar

`PyAudio` es necesario para leer el microfono y siempre compila desde el codigo
fuente.

**En macOS** hace falta `portaudio` y, con el SDK de Xcode 27, hay que apuntar a un
SDK anterior porque el linker no reconoce las arquitecturas `arm64e`:

```
brew install portaudio
SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
MACOSX_DEPLOYMENT_TARGET=13.0 \
pip install "PyAudio==0.2.14"
```

**En Windows** normalmente instala con `pip`. Si falla:

```
pip install pipwin
pipwin install pyaudio
```

o descarga el `.whl` de https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### Si `pip install` se corta y no instala nada

`pip` aborta **todas** las dependencias cuando una falla. Si PyAudio no compila,
las otras librerias tampoco se instalan. Instalas por partes:

```
pip install pyttsx3 SpeechRecognition pywhatkit yfinance pyjokes wikipedia
```

---

## Dependencias

| Libreria | Para que se usa |
|---|---|
| `pyttsx3` | Convertir texto a voz (que el asistente hable). |
| `speech_recognition` | Reconocimiento de voz (escuchar por microfono). |
| `PyAudio` | Acceso al microfono (dependencia de `speech_recognition`). |
| `pywhatkit` | Buscar en internet y reproducir en YouTube. |
| `yfinance` | Precios de acciones desde Yahoo Finance. |
| `pyjokes` | Generar chistes en espanol. |
| `wikipedia` | Busquedas en Wikipedia. |
| `webbrowser`, `datetime`, `re`, `unicodedata`, `unittest` | Librerias estandar de Python (no se instalan). |

---

## Comandos por voz

Decile estos comandos al asistente. Ejemplos entre comillas.

| Comando de ejemplo | Que hace |
|---|---|
| "tengo una rtx 3060, un ryzen 5 y 16 de ram" | Anota tus componentes (puede ser todo junto o de a uno). |
| "procesador: ryzen 5" / "gpu: rtx 3060" / "16 gb de ram" | Anota el componente que digas y pide el que falta. |
| "me corre cyberpunk 2077" | Te dice si corre y en que calidad. |
| "que hora es" | Informa la hora actual. |
| "que dia es hoy" / "que fecha es" | Informa el dia / la fecha. |
| "busca en wikipedia lionel messi" | Lee un resumen de Wikipedia. |
| "abrir youtube" | Abre YouTube en el navegador. |
| "abrir navegador" / "abrir google" | Abre Google. |
| "busca en internet requisitos gta 5" | Busca en Google. |
| "reproducir bohemian rhapsody" | Reproduce en YouTube. |
| "precio de la accion de nvidia" | Precio actual de la accion. |
| "contame un chiste" | Cuenta un chiste. |
| "adios" / "chau" / "salir" / "terminar" | Cierra el asistente. |

Tambien podes cerrarlo en cualquier momento con `Ctrl + C` en la terminal.

### Juegos y componentes cargados

- **Juegos**: minecraft, league of legends, valorant, counter strike 2, fortnite,
  gta 5, cyberpunk 2077, elden ring, red dead redemption 2, god of war.
- **Graficas**: integrada, gtx 1050, gtx 1650, gtx 1660, rx 580, rtx 2060, rx 6600,
  rtx 3050, rtx 3060, rx 6700, rtx 3070, rtx 4060, rtx 4070, rtx 4090.
- **Procesadores**: athlon, core i3/i5/i7/i9, ryzen 3/5/7/9.
- **Acciones**: nvidia, amd, intel, sony, microsoft, logitech, corsair,
  electronic arts (ea) y take two.

---

## Estructura del proyecto

La aplicacion esta dividida por funcionalidad (*feature-based*). Cada carpeta
`features/...` es una funcionalidad completa con su logica y sus comandos, y el
nucleo (`app/`) solo se ocupa de escuchar, guardar el estado y elegir a quien
le toca responder.

```text
asistente.py               punto de entrada: crea el asistente y lo ejecuta
app/
  assistant.py             bucle de la conversacion y armado de la aplicacion
  router.py                CommandRouter y la lista de comandos
  session.py               estado de la conversacion (Session y Context)
features/
  hardware/                dominio principal: componentes y compatibilidad
    data.py                  juegos, graficas y procesadores
    models.py                HardwareProfile, Spec, GameRequirements, GpuSpec
    parser.py                logica pura para leer RAM, GPU, CPU y juego del texto
    compatibility.py         regla de minimos y recomendados
    commands.py              comandos hablados de hardware
  wikipedia/
    errors.py                errores propios de la feature
    client.py                consultas a Wikipedia
    commands.py              comando de busqueda
  datetime/
    time.py                  mensajes que dependen del reloj
    commands.py              comandos de hora y fecha
  stocks/
    quotes.py                precios de acciones (yfinance)
    commands.py              comando de acciones
  media/
    playback.py              busqueda en internet y YouTube (pywhatkit)
    commands.py              comandos de busqueda y cancion
  browser/
    commands.py              apertura de YouTube y Google
  jokes/
    jokes.py                 chistes en espanol (pyjokes)
    commands.py              comando de chistes
shared/
  command.py                Command y KeywordCommand (contrato de los comandos)
  text.py                   utilidades de texto
  voice.py                  VoiceService: hablar (pyttsx3) y escuchar (speech_recognition)
tests/
  doubles.py                dobles de prueba compartidos
  test_hardware.py          parser, modelos, compatibilidad y datos
  test_text.py              utilidades de texto
  test_datetime.py          mensajes que dependen del reloj
  test_router.py            ruteo de pedidos a cada feature
  test_assistant.py         bucle de la conversacion
requirements.txt
README.md
```

### Documentacion

| Documento | Que explica |
|---|---|
| [docs/arquitectura.md](docs/arquitectura.md) | Ruta de lectura del proyecto, responsabilidades y diagramas |
| [docs/conceptos.md](docs/conceptos.md) | Glosario: `Callable`, el asterisco de las listas, `Session` vs `Context`, inyeccion de dependencias |

### Responsabilidades

| Parte | Que hace | Que no hace |
|---|---|---|
| `asistente.py` | Arranca la aplicacion. | No sabe de juegos ni de acciones. |
| `app/assistant.py` | Bucle: saluda, escucha, resuelve y ejecuta. | No reconoce pedidos por su cuenta. |
| `app/router.py` | Elige el comando que responde a un pedido. | No sabe que significa "rtx 3060" ni "wikipedia". |
| `app/session.py` | Unico lugar donde vive el estado (equipo, componentes parciales). | No decide que hacer con el estado. |
| `features/*/parser.py` | Convierte texto en datos del dominio. | No habla con el usuario ni con internet. |
| `features/*/compatibility.py` | Decide si un equipo cumple los requisitos. | No guarda estado ni habla. |
| `features/*/commands.py` | Conecta el pedido hablado con la feature. | No implementa la logica de dominio. |
| `shared/voice.py` | Hablar y escuchar. | No decide que se responde. |
| `shared/command.py` | Contrato `Command` y el comando genérico por palabras clave. | No sabe de que feature se trata. |

### Flujo principal

```text
asistente.py
  -> create_assistant()          arma router + features + voz
    -> Assistant.run()           saluda y entra al bucle
      -> voice.listen()          transcribe el pedido
        -> router.resolve(text)  primer comando que lo reconoce
          -> command.execute(context, text)
            -> feature            (parser + dominio + voz)
```

Para agregar un comando nuevo se escribe su feature y se agrega una linea en
`build_router()` (`app/router.py`). No hay que tocar el bucle ni el router.

### Los comandos no dependen de las librerias

Los comandos se arman con funciones simples que se pasan por parametro
(`wikipedia_commands(summarize)`, `browser_commands(open_url)`, etc.). Las
librerias reales se conectan en un unico lugar, `create_assistant()`
(`app/assistant.py`). Por eso los tests pueden correr sin microfono, parlantes
ni conexion a internet.

Los `except Exception` quedan solo en los adaptadores que habla con una libreria
(`client.py`, `quotes.py`, `playback.py`, `voice.py`) y devuelven un valor que el
comando sabe traducir a un mensaje. El nucleo y los comandos no silencian
errores internos.

---

## Tests

Los tests usan `unittest` (viene con Python, no hace falta instalar nada) y no
necesitan microfono, parlantes, navegador, Wikipedia ni `yfinance`: las
dependencias se reemplazan por dobles de prueba.

```bash
python -m unittest discover -s tests -v
```

Que cubren:

- `test_hardware.py`: deteccion de RAM, GPU, CPU y juego en texto; todos los
  modelos de la base; los tres casos de compatibilidad sobre cada juego; y
  invariantes de los datos.
- `test_text.py`: normalizacion, busqueda de palabras y limpieza de texto.
- `test_datetime.py`: hora, dia de la semana y saludo en cada franja horaria.
- `test_router.py`: cada pedido por voz cae en la feature correcta, el orden de
  prioridad se respeta y los fallos de YouTube o Google se avisan.
- `test_assistant.py`: el bucle completo (saludo, pedidos, fallback, despedida,
  `Ctrl + C`) y los componentes dichos de a uno.

---

## Como personalizar

### Agregar un juego

En `features/hardware/data.py`, dentro de `GAMES`, agrega una entrada:

```python
"fifa 25": GameRequirements(
    minimum=Spec(ram=8, vram=4, gpu=4, cpu=4),
    recommended=Spec(ram=16, vram=6, gpu=6, cpu=6),
),
```

### Agregar una placa de video

En `features/hardware/data.py`, dentro de `GPUS`, agrega el modelo:

```python
"rtx 4080": GpuSpec(level=9, vram=16),
```

### Agregar un procesador

En `features/hardware/data.py`, dentro de `CPUS`, agrega el modelo con su nivel:

```python
"ryzen 7 7800x3d": 8,
```

### Agregar una accion

En `features/stocks/commands.py`, dentro de `TICKERS`, agrega la empresa:

```python
"valve": "VALVE",
```

### Agregar una funcionalidad nueva

1. Crear la carpeta en `features/` con su logica de dominio y su `commands.py`
   (que devuelve `list[Command]`).
2. Si necesita una libreria externa, aislarla en un modulo propio (por ejemplo
   `playback.py`) y recibirla como funcion en `commands.py`.
3. Agregar su comando a la lista de `build_router()` en `app/router.py`, en el
   orden de prioridad que corresponda.
4. Cubrirlo en `tests/`: los comandos no dependen de la libreria, asi que los
   tests no la necesitan.

---

## Solucion de problemas

- **"No pude buscar en wikipedia en este momento"**: Wikipedia limita la cantidad de
  peticiones seguidas (error 429). Espera unos segundos y volve a intentar.
- **No se escucha la voz**: en Windows revisa que la voz `TTS_MS_ES-ES_HELENA_11.0`
  este instalada (Configuracion > Hora e idioma > Voz). En macOS el asistente
  elige sola una voz en espanol del sistema; para ver cual usa, corré
  `python -c "from shared.voice import VoiceService; print(VoiceService().voice_id)"`.
- **Habla en ingles en macOS**: no hay ninguna voz en espanol instalada. Descarga
  una desde Ajustes > Accesibilidad > Contenido hablado > Voces del sistema.
- **No reconoce la voz**: revisa el microfono, el idioma (espanol) y la conexion a
  internet (el reconocimiento usa Google).