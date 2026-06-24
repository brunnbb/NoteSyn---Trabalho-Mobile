# ==============================================================================
# core/weather.py
# Integração com Open-Meteo (https://open-meteo.com/) — sem API key necessária.
# Usa um httpx.Client persistente para reaproveitar conexões TCP entre chamadas,
# reduzindo o overhead de handshake nas duas requisições (geocoding + forecast).
# ==============================================================================

import httpx

_WMO_CODES: dict[int, tuple[str, str]] = {
    0: ("Céu limpo", "☀️"),
    1: ("Principalmente limpo", "🌤️"),
    2: ("Parcialmente nublado", "⛅"),
    3: ("Nublado", "☁️"),
    45: ("Neblina", "🌫️"),
    48: ("Geada com neblina", "🌫️"),
    51: ("Garoa leve", "🌦️"),
    53: ("Garoa moderada", "🌦️"),
    55: ("Garoa intensa", "🌧️"),
    61: ("Chuva leve", "🌧️"),
    63: ("Chuva moderada", "🌧️"),
    65: ("Chuva intensa", "🌧️"),
    71: ("Neve leve", "🌨️"),
    73: ("Neve moderada", "🌨️"),
    75: ("Neve intensa", "❄️"),
    77: ("Granizo", "🌨️"),
    80: ("Pancadas leves", "🌦️"),
    81: ("Pancadas moderadas", "🌧️"),
    82: ("Pancadas fortes", "⛈️"),
    85: ("Neve fraca", "🌨️"),
    86: ("Neve forte", "❄️"),
    95: ("Trovoada", "⛈️"),
    96: ("Trovoada com granizo", "⛈️"),
    99: ("Trovoada intensa", "⛈️"),
}

_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Timeout agressivo: connect=3s, read=5s
# A maioria das respostas chega em <1s; 5s já é muito conservador.
_TIMEOUT = httpx.Timeout(connect=3.0, read=5.0, write=3.0, pool=3.0)


def buscar_clima_cidade(cidade: str) -> tuple[dict, str] | None:
    """
    Encadeia geocoding + forecast num único cliente HTTP (conexão reutilizada).
    Retorna (dados_clima, nome_oficial_cidade) ou None em caso de falha.
    """
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            # 1. Geocoding
            geo_resp = client.get(
                _GEOCODING_URL,
                params={"name": cidade, "count": 1, "language": "pt", "format": "json"},
            )
            geo_resp.raise_for_status()
            results = geo_resp.json().get("results")
            if not results:
                return None
            r = results[0]
            lat, lon, nome = float(r["latitude"]), float(r["longitude"]), r["name"]

            # 2. Forecast (mesma conexão TCP quando possível)
            fc_resp = client.get(
                _FORECAST_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,weathercode,windspeed_10m,relative_humidity_2m",
                    "timezone": "America/Sao_Paulo",
                    "forecast_days": 1,
                },
            )
            fc_resp.raise_for_status()
            current = fc_resp.json()["current"]

        codigo = int(current.get("weathercode", 0))
        descricao, emoji = _WMO_CODES.get(codigo, ("Desconhecido", "🌡️"))

        return {
            "temperatura": current["temperature_2m"],
            "umidade": current["relative_humidity_2m"],
            "vento": current["windspeed_10m"],
            "descricao": descricao,
            "emoji": emoji,
            "codigo_wmo": codigo,
        }, nome

    except Exception:
        return None
