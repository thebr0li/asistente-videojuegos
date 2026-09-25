import pyttsx3
import speech_recognition as sr
import re
import datetime
import wikipedia
import pywhatkit
import pyjokes
import yfinance as yf
import webbrowser
import sys
import warnings

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

voz_es = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0"

motor_voz = pyttsx3.init()
motor_voz.setProperty("voice", voz_es)
reconocedor = sr.Recognizer()
wikipedia.set_lang("es")
wikipedia.set_user_agent("AsistenteGamer/1.0 (asistente educativo de videojuegos)")

JUEGOS = {
    "minecraft": {
        "min": {"ram": 2, "vram": 1, "gpu": 1, "cpu": 1},
        "rec": {"ram": 4, "vram": 2, "gpu": 2, "cpu": 2},
    },
    "league of legends": {
        "min": {"ram": 2, "vram": 1, "gpu": 1, "cpu": 1},
        "rec": {"ram": 4, "vram": 2, "gpu": 2, "cpu": 2},
    },
    "valorant": {
        "min": {"ram": 4, "vram": 1, "gpu": 2, "cpu": 2},
        "rec": {"ram": 8, "vram": 2, "gpu": 3, "cpu": 3},
    },
    "counter strike 2": {
        "min": {"ram": 8, "vram": 1, "gpu": 2, "cpu": 2},
        "rec": {"ram": 8, "vram": 2, "gpu": 3, "cpu": 3},
    },
    "fortnite": {
        "min": {"ram": 8, "vram": 2, "gpu": 3, "cpu": 3},
        "rec": {"ram": 16, "vram": 6, "gpu": 6, "cpu": 5},
    },
    "gta 5": {
        "min": {"ram": 4, "vram": 2, "gpu": 3, "cpu": 3},
        "rec": {"ram": 8, "vram": 4, "gpu": 5, "cpu": 5},
    },
    "cyberpunk 2077": {
        "min": {"ram": 8, "vram": 3, "gpu": 4, "cpu": 4},
        "rec": {"ram": 16, "vram": 6, "gpu": 7, "cpu": 6},
    },
    "elden ring": {
        "min": {"ram": 12, "vram": 3, "gpu": 4, "cpu": 4},
        "rec": {"ram": 16, "vram": 6, "gpu": 6, "cpu": 6},
    },
    "red dead redemption 2": {
        "min": {"ram": 8, "vram": 2, "gpu": 4, "cpu": 4},
        "rec": {"ram": 12, "vram": 6, "gpu": 6, "cpu": 6},
    },
    "god of war": {
        "min": {"ram": 8, "vram": 4, "gpu": 4, "cpu": 4},
        "rec": {"ram": 16, "vram": 8, "gpu": 7, "cpu": 6},
    },
}


def juegos_disponibles():
    return list(JUEGOS.keys())


GRAFICAS = {
    "integrada": {"nivel": 1, "vram": 1},
    "gtx 1050": {"nivel": 3, "vram": 2},
    "gtx 1650": {"nivel": 4, "vram": 4},
    "gtx 1660": {"nivel": 5, "vram": 6},
    "rx 580": {"nivel": 4, "vram": 8},
    "rtx 2060": {"nivel": 6, "vram": 6},
    "rx 6600": {"nivel": 6, "vram": 8},
    "rtx 3050": {"nivel": 5, "vram": 8},
    "rtx 3060": {"nivel": 7, "vram": 12},
    "rx 6700": {"nivel": 7, "vram": 12},
    "rtx 3070": {"nivel": 8, "vram": 8},
    "rtx 4060": {"nivel": 7, "vram": 8},
    "rtx 4070": {"nivel": 9, "vram": 12},
    "rtx 4090": {"nivel": 10, "vram": 24},
}

PROCESADORES = {
    "athlon": 2,
    "core i3": 3,
    "core i5": 5,
    "core i7": 7,
    "core i9": 9,
    "ryzen 3": 3,
    "ryzen 5": 5,
    "ryzen 7": 7,
    "ryzen 9": 9,
}


def buscar_grafica(nombre):
    for modelo, datos in GRAFICAS.items():
        if modelo in nombre:
            return datos
    return None


def buscar_procesador(nombre):
    for modelo, nivel in PROCESADORES.items():
        if modelo in nombre:
            return nivel
    return None


def crear_equipo(grafica, procesador, ram):
    datos_gpu = buscar_grafica(grafica)
    nivel_cpu = buscar_procesador(procesador)
    if datos_gpu is None or nivel_cpu is None:
        return None
    return {"ram": ram, "vram": datos_gpu["vram"], "gpu": datos_gpu["nivel"], "cpu": nivel_cpu}


def comparar(equipo, juego):
    requisitos = JUEGOS[juego]

    def cumple(req):
        return (equipo["ram"] >= req["ram"] and equipo["vram"] >= req["vram"]
                and equipo["gpu"] >= req["gpu"] and equipo["cpu"] >= req["cpu"])

    if cumple(requisitos["rec"]):
        return "Si, " + juego + " te corre en calidad alta (recomendado)"
    elif cumple(requisitos["min"]):
        return "Si, " + juego + " te corre, pero en calidad baja (minimo)"
    else:
        return "No, no te corre " + juego + " con esos componentes"


def extraer_ram(texto):
    coincidencia = re.search(r"(\d+)\s*(?:gb|gigas?)?\s*(?:de\s*)?ram", texto)
    if coincidencia:
        return int(coincidencia.group(1))
    coincidencia = re.search(r"ram\D{0,12}?(\d+)", texto)
    if coincidencia:
        return int(coincidencia.group(1))
    return None


def componentes_sueltos(texto):
    datos = {}
    for modelo in GRAFICAS:
        if modelo in texto:
            datos["gpu"] = GRAFICAS[modelo]["nivel"]
            datos["vram"] = GRAFICAS[modelo]["vram"]
            print("Grafica detectada:", modelo)
            break

    for modelo in PROCESADORES:
        if modelo in texto:
            datos["cpu"] = PROCESADORES[modelo]
            print("Procesador detectado:", modelo)
            break

    ram = extraer_ram(texto)
    if ram is not None:
        datos["ram"] = ram
        print("Ram detectada:", ram, "GB")

    return datos


def detectar_juego(texto):
    for juego in JUEGOS:
        if juego in texto:
            return juego
    return None


def responder_juego(equipo, texto):
    juego = detectar_juego(texto)
    if juego is None:
        hablar("No tengo ese juego en mi base de datos")
        return
    if equipo is None:
        hablar("Primero decime tus componentes")
        return
    hablar(comparar(equipo, juego))


def pedir_hora():
    hora = datetime.datetime.now()
    mensaje = "En este momento son las " + str(hora.hour) + " horas con " + str(hora.minute) + " minutos"
    print(mensaje)
    hablar(mensaje)


def pedir_dia():
    dia = datetime.datetime.today()
    dias = {0: "Lunes", 1: "Martes", 2: "Miercoles", 3: "Jueves",
            4: "Viernes", 5: "Sabado", 6: "Domingo"}
    hablar("Hoy es " + dias[dia.weekday()])


def saludo_inicial():
    hora = datetime.datetime.now()
    if hora.hour < 6 or hora.hour > 20:
        momento = "Buenas noches"
    elif 6 <= hora.hour < 13:
        momento = "Buen dia"
    else:
        momento = "Buenas tardes"
    hablar(momento + ", en que te puedo ayudar?")


def buscar_wikipedia(pedido):
    consulta = pedido.replace("busca en wikipedia", "").replace("buscar en wikipedia", "")
    consulta = consulta.replace("wikipedia", "").replace("busca", "").replace("buscar", "").strip()
    hablar("Buscando en wikipedia")

    try:
        resultados = wikipedia.search(consulta)
        if not resultados:
            hablar("No encontre informacion sobre eso")
            return
        resumen = wikipedia.summary(resultados[0], sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        hablar("Hay varias opciones: " + ", ".join(e.options[:3]))
        return
    except wikipedia.exceptions.PageError:
        hablar("No encontre informacion sobre eso")
        return
    except Exception:
        hablar("No pude buscar en wikipedia en este momento")
        return

    resumen = resumen.replace("\u200b", "").replace("\n", " ")
    hablar(resumen)


def hablar(mensaje):
    print("Asistente:", mensaje)
    motor_voz.say(mensaje)
    motor_voz.runAndWait()


def transformar_audio_texto():
    with sr.Microphone() as origen:
        reconocedor.pause_threshold = 0.8
        print("Ya puedes hablar")
        audio = reconocedor.listen(origen)

    try:
        pedido = reconocedor.recognize_google(audio, language="es-ES")
        print("Dijiste:", pedido)
        return pedido
    except sr.UnknownValueError:
        print("Ups, no entendi")
        return "Sigo esperando"
    except sr.RequestError:
        print("Ups, no hay servicio")
        return "Sigo esperando"


def reproducir_cancion(pedido):
    cancion = pedido
    for palabra in ["reproducir", "reproduce", "reproducime", "poner", "pone", "pon",
                    "en youtube", "cancion", "canción"]:
        cancion = cancion.replace(palabra, "")
    cancion = cancion.strip()

    if cancion == "":
        hablar("Que cancion queres que reproduzca?")
        return
    hablar("Reproduciendo " + cancion + " en YouTube")
    pywhatkit.playonyt(cancion)


def consultar_accion(pedido):
    empresa = pedido.split("de")[-1].strip().lower()
    cartera = {
        "nvidia": "NVDA",
        "amd": "AMD",
        "intel": "INTC",
        "sony": "SONY",
        "microsoft": "MSFT",
        "logitech": "LOGI",
        "corsair": "CRSR",
        "electronic arts": "EA",
        "ea": "EA",
        "take two": "TTWO",
    }

    if empresa not in cartera:
        hablar("No tengo informacion sobre la accion de " + empresa)
        return

    try:
        ticker = yf.Ticker(cartera[empresa])
        precio = ticker.info.get("regularMarketPrice")
        if precio is None:
            precio = ticker.fast_info["last_price"]
        hablar("El precio de " + empresa + " es " + str(round(precio, 2)) + " dolares")
    except Exception:
        hablar("No pude encontrar la informacion de la accion")


def contar_chiste():
    chiste = pyjokes.get_joke("es")
    chiste = chiste.replace("\u200b", "")
    hablar(chiste)


def centro_pedido():
    saludo_inicial()
    equipo_usuario = None
    datos_usuario = {}

    try:
        while True:
            pedido = transformar_audio_texto().lower()
            print("Comando recibido:", pedido)

            if pedido in ("sigo esperando", ""):
                continue

            pide_dia = ("que dia" in pedido or "que día" in pedido or "día es" in pedido
                        or "dia es" in pedido or "dia de hoy" in pedido or "día de hoy" in pedido
                        or "fecha" in pedido)

            if "hora" in pedido:
                pedir_hora()
                continue
            elif pide_dia:
                pedir_dia()
                continue
            elif "wikipedia" in pedido:
                buscar_wikipedia(pedido)
                continue
            elif "abrir youtube" in pedido:
                hablar("Abriendo YouTube")
                webbrowser.open("https://www.youtube.com")
                continue
            elif "abrir google" in pedido or "abrir navegador" in pedido or "abrir el navegador" in pedido:
                hablar("Abriendo el navegador")
                webbrowser.open("https://www.google.com")
                continue
            elif "busca en internet" in pedido or "buscar en internet" in pedido:
                consulta = pedido.replace("buscar en internet", "").replace("busca en internet", "").strip()
                hablar("Buscando en internet")
                pywhatkit.search(consulta)
                continue
            elif ("reproducir" in pedido or "reproduce" in pedido or "poner" in pedido
                  or "pone" in pedido or "cancion" in pedido or "canción" in pedido):
                reproducir_cancion(pedido)
                continue
            elif "accion" in pedido or "acción" in pedido or "bolsa" in pedido:
                consultar_accion(pedido)
                continue
            elif "chiste" in pedido:
                contar_chiste()
                continue

            if "me corre" in pedido or "corre" in pedido:
                responder_juego(equipo_usuario, pedido)
                continue

            partes = componentes_sueltos(pedido)
            pide_componentes = "componentes" in pedido or "mi pc" in pedido or "mi equipo" in pedido

            if partes or pide_componentes:
                datos_usuario.update(partes)
                faltan = [p for p in ["gpu", "cpu", "ram"] if p not in datos_usuario]
                if faltan:
                    hablar("Anote. Todavia me falta " + ", ".join(faltan))
                else:
                    equipo_usuario = dict(datos_usuario)
                    hablar("Perfecto, ya tengo tu equipo completo")
            elif "adios" in pedido or "chau" in pedido or "salir" in pedido or "terminar" in pedido:
                hablar("Nos vemos, avisame si necesitas otra cosa")
                break
            else:
                hablar("No entendi el pedido")
    except KeyboardInterrupt:
        print()
        hablar("Hasta luego")


if __name__ == "__main__":
    centro_pedido()
