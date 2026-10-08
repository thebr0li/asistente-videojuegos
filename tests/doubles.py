"""Dobles de prueba compartidos: fakes sin dependencias externas."""

from features.wikipedia.errors import AmbiguousQuery, LookupFailed


class FakeVoice:
    """Guarda los mensajes del asistente en vez de hablar por el parlante."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def say(self, message: str) -> None:
        self.messages.append(message)

    @property
    def last_message(self) -> str:
        return self.messages[-1]


class ScriptedVoice(FakeVoice):
    """Voz que devuelve los pedidos guionizados y despues corta con Ctrl+C."""

    def __init__(self, inputs) -> None:
        super().__init__()
        self.inputs = list(inputs)
        self.inputs_heard: list[str | None] = []

    @property
    def heard(self) -> int:
        return len(self.inputs_heard)

    def listen(self) -> str | None:
        if not self.inputs:
            raise KeyboardInterrupt
        heard = self.inputs.pop(0)
        self.inputs_heard.append(heard)
        return heard


class WikipediaStub:
    """Wikipedia con tema conocido, ambiguo, inexistente y sin conexion."""

    AMBIGUOUS = ("Nintendo", "Nintendo Switch", "Nintendo 64", "Nintendo DS")

    def __init__(self, ambiguous=("ambiguo",), missing=("sin informacion",), offline=("sin conexion",)) -> None:
        self.ambiguous = ambiguous
        self.missing = missing
        self.offline = offline
        self.queries: list[str] = []

    def search(self, query: str) -> str | None:
        self.queries.append(query)
        if query in self.ambiguous:
            raise AmbiguousQuery(list(self.AMBIGUOUS))
        if query in self.offline:
            raise LookupFailed("sin red")
        if query in self.missing:
            return None
        return f"Resumen de {query}"


class MediaStub:
    """YouTube y el navegador: guarda lo pedido y simula que falla si se le pide."""

    def __init__(self, failing=False) -> None:
        self.failing = failing
        self.opened: list[str] = []
        self.played: list[str] = []
        self.searched: list[str] = []

    def open_url(self, url: str) -> bool:
        self.opened.append(url)
        return not self.failing

    def play_on_youtube(self, song: str) -> bool:
        self.played.append(song)
        return not self.failing

    def search_on_internet(self, query: str) -> bool:
        self.searched.append(query)
        return not self.failing


class PricesStub:
    """Precios de acciones: solo NVDA y AMD tienen dato."""

    PRECIOS = {"NVDA": 100.5, "AMD": 52.3}

    def __init__(self) -> None:
        self.tickers: list[str] = []

    def price_of(self, ticker: str) -> float | None:
        self.tickers.append(ticker)
        return self.PRECIOS.get(ticker)


class JokeStub:
    """Un chiste fijo con un salto de linea y un caracter invisible."""

    CHISTE = "\u200bPrimer chiste\ncon remate"

    def tell(self) -> str:
        return self.CHISTE


def build_test_router(wikipedia=None, media=None, prices=None):
    """Arma el router real con dobles de prueba."""
    from app.router import build_router

    wikipedia = wikipedia or WikipediaStub()
    media = media or MediaStub()
    prices = prices or PricesStub()
    return build_router(
        summarize=wikipedia.search,
        open_url=media.open_url,
        play_on_youtube=media.play_on_youtube,
        search_on_internet=media.search_on_internet,
        last_price=prices.price_of,
        fetch_joke=JokeStub().tell,
    )
