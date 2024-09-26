import requests

WEATHER_API_KEY = "JKJ6ZMNP2JKMVHPRYSPT8DALL"

def clima_mes(ano: str, mes: str, dia_inicio: str, dia_fim: str) -> list:
    global WEATHER_API_KEY
    URL_BASE = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    LOCAL = "Sao Paulo"
    DIA_INICIAL = f"{ano}-{mes}-{dia_inicio}"
    DIA_FINAL = f"{ano}-{mes}-{dia_fim}"

    url = f"{URL_BASE}{LOCAL}/{DIA_INICIAL}/{DIA_FINAL}?unitGroup=metric&key={WEATHER_API_KEY}&include=days"

    resposta = requests.get(url)

    if resposta.status_code == 200:
        data = resposta.json()

        total_temp_max = 0
        total_temp_min = 0
        total_umidade = 0
        contagem_dias = 0

        for day_data in data['days']:
            total_temp_max += day_data['tempmax']
            total_temp_min += day_data['tempmin']
            total_umidade += day_data['humidity']
            contagem_dias += 1

        # Calculando a média das temperaturas e umidade
        med_temp_max = total_temp_max / contagem_dias
        med_temp_min = total_temp_min / contagem_dias
        med_humidity = total_umidade / contagem_dias

        return [med_temp_max, med_temp_min, med_humidity]
    else:
        return "Erro"


def clima_dia(ano: str, mes: str, dia: str) -> list:
    global WEATHER_API_KEY
    URL_BASE = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    LOCAL = "Sao Paulo"
    DATA = f"{ano}-{mes}-{dia}"

    url = f"{URL_BASE}{LOCAL}/{DATA}?unitGroup=metric&key={WEATHER_API_KEY}&include=days"

    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()

        # Extraindo dados de temperatura e umidade do dia específico
        dados_dia = dados['days'][0]
        temp_max = dados_dia['tempmax']
        temp_min = dados_dia['tempmin']
        umidade = dados_dia['humidity']

        return [temp_max,temp_min, umidade]
    else:
        return "Erro"