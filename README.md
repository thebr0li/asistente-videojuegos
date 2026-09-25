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

- **Sistema operativo**: Windows (la voz de `pyttsx3` usa las voces SAPI5 de Windows).
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

`PyAudio` es necesario para leer el microfono. En Windows normalmente instala con
`pip`, pero si da error proba:

```
pip install pipwin
pipwin install pyaudio
```

o descarga el archivo `.whl` correspondiente a tu version de Python desde
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio y luego:

```
pip install pyaudio‑0.2.14‑cp312‑cp312‑win_amd64.whl
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
| `webbrowser`, `datetime`, `sys`, `warnings`, `re` | Librerias estandar de Python (no se instalan). |

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

## Como funciona el codigo

El archivo completo es `asistente.py`. Se explica por partes.

### 1. Imports y configuracion inicial (lineas 1-22)

Se importan las librerias, se silencian advertencias (`warnings.filterwarnings`)
y se fuerza la salida en UTF-8 (`sys.stdout.reconfigure`) para que los acentos y
caracteres especiales no rompan la consola de Windows.

- `voz_es`: ruta de la voz de Windows (ES-ES Helena). Se aplica al motor de voz.
- `motor_voz = pyttsx3.init()`: se inicializa el motor de texto a voz **una sola vez**.
- `reconocedor = sr.Recognizer()`: objeto que captura y transcribe audio.
- `wikipedia.set_lang("es")` y `wikipedia.set_user_agent(...)`: Wikipedia en espanol
  y un User-Agent propio, porque Wikipedia bloquea el que trae la libreria por defecto.

### 2. Bases de datos (lineas 24-99)

- `JUEGOS`: diccionario de juegos. Cada juego guarda `"min"` (minimos) y `"rec"`
  (recomendados), con 4 valores: `ram` y `vram` en GB, y `gpu`/`cpu` como nivel 1-10.
- `GRAFICAS`: cada placa de video con su `nivel` (1-10) y su `vram` en GB.
- `PROCESADORES`: cada procesador con su nivel (1-10).

Los niveles permiten comparar componentes de distinta generacion con un solo numero.

### 3. Funciones de compatibilidad (lineas 102-187)

- `juegos_disponibles()`: devuelve la lista de nombres de juegos cargados.
- `buscar_grafica(nombre)`: busca una GPU por texto (ej. "rtx 3060" dentro de la frase)
  y devuelve su nivel y VRAM.
- `buscar_procesador(nombre)`: idem para CPU.
- `crear_equipo(grafica, procesador, ram)`: arma el diccionario del equipo del usuario
  con `{"ram", "vram", "gpu", "cpu"}`.
- `comparar(equipo, juego)`: recorre los requisitos minimos y recomendados. Si supera
  los recomendados devuelve calidad **alta**; si solo supera los minimos, calidad
  **baja**; si no llega a los minimos, avisa que **no corre**.
- `extraer_ram(texto)`: usa expresiones regulares (`re`) para encontrar la cantidad de
  RAM en la frase, por ejemplo "16 de ram" o "8gb de ram".
- `componentes_sueltos(texto)`: detecta en la frase SOLO los componentes que aparezcan
  (GPU, CPU y/o RAM) y devuelve un diccionario parcial. Permite cargar los componentes
  de a uno.
- `detectar_juego(texto)`: busca en la frase el nombre de algun juego de la base.
- `responder_juego(equipo, texto)`: detecta el juego y responde con `comparar`. Si no
  hay juego o no hay componentes, avisa.

### 4. Hora, fecha y saludo (lineas 190-212)

- `pedir_hora()`: toma `datetime.now()` y arma un texto con horas y minutos.
- `pedir_dia()`: usa `weekday()` (0-6) y un diccionario para decir el dia de la semana.
- `saludo_inicial()`: saluda segun la hora (Buen dia / Buenas tardes / Buenas noches).

### 5. Wikipedia (lineas 215-237)

- `buscar_wikipedia(pedido)`: limpia la frase (saca "busca en wikipedia"), usa
  `wikipedia.search()` para obtener el titulo mas parecido y `wikipedia.summary()` para
  el resumen. Maneja errores: ambiguedad (`DisambiguationError`, lista opciones), pagina
  inexistente (`PageError`) y fallos de red o limite de peticiones.

### 6. Voz y escucha (lineas 240-261)

- `hablar(mensaje)`: imprime el texto y lo reproduce con `say()` + `runAndWait()`.
- `transformar_audio_texto()`: abre el microfono, graba hasta detectar una pausa
  (`pause_threshold = 0.8` segundos) y transcribe con Google en espanol
  (`recognize_google(audio, language="es-ES")`). Si no entiende o no hay internet,
  devuelve `"Sigo esperando"`.

### 7. Acciones (lineas 264-310)

- `reproducir_cancion(pedido)`: quita las palabras de comando y llama a
  `pywhatkit.playonyt(cancion)` para reproducir en YouTube.
- `consultar_accion(pedido)`: toma la empresa de la frase, la traduce a su ticker
  bursatil usando el diccionario `cartera` y consulta el precio con `yfinance`.
- `contar_chiste()`: obtiene un chiste en espanol con `pyjokes.get_joke("es")`.

### 8. Bucle principal `centro_pedido()` (lineas 313-385)

Es el corazon del asistente:

1. Saluda con `saludo_inicial()`.
2. Crea `equipo_usuario` (los componentes) y `datos_usuario` (componentes acumulados).
3. Entra en un `while True`: en cada vuelta transcribe tu pedido y lo compara con una
   cadena de `if / elif` para decidir que funcion ejecutar (hora, fecha, wikipedia,
   abrir web, buscar, reproducir, acciones, chistes, juegos, componentes o despedida).
4. Ignora los pedidos vacios o mal reconocidos (`"sigo esperando"`).
5. Se cierra con "adios" o con `Ctrl + C` (capturado con `except KeyboardInterrupt`).

---

## Como personalizar

### Agregar un juego

En el diccionario `JUEGOS` agrega una entrada:

```python
"fifa 25": {
    "min": {"ram": 8, "vram": 4, "gpu": 4, "cpu": 4},
    "rec": {"ram": 16, "vram": 6, "gpu": 6, "cpu": 6},
},
```

### Agregar una placa de video

En `GRAFICAS` agrega el modelo con su nivel y VRAM:

```python
"rtx 4080": {"nivel": 9, "vram": 16},
```

### Agregar un procesador

En `PROCESADORES` agrega el modelo con su nivel:

```python
"ryzen 7 7800x3d": 8,
```

### Agregar una accion

En el diccionario `cartera` dentro de `consultar_accion` agrega la empresa:

```python
"valve": "VALVE",
```

---

## Solucion de problemas

- **"No pude buscar en wikipedia en este momento"**: Wikipedia limita la cantidad de
  peticiones seguidas (error 429). Espera unos segundos y volve a intentar.
- **No se escucha la voz**: revisa el volumen de Windows y que la voz
  `TTS_MS_ES-ES_HELENA_11.0` este instalada (Configuracion > Hora e idioma > Voz).
- **No reconoce la voz**: revisa el microfono, el idioma (espanol) y la conexion a
  internet (el reconocimiento usa Google).
