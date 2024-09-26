# ------------- Importações --------------
import google.generativeai as genai
from sklearn.preprocessing import StandardScaler
import numpy as np
import sqlite3
import datetime
import pickle
import ast
import threading
import time
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import print_formatted_text
from api_functions import clima_dia, clima_mes

# ----------------------------------------

session = PromptSession()

GEMINI_API_KEY = "AIzaSyBow1PWoN12TuqSw7wudJP2NdAS0OcRYMo"
genai.configure(api_key=GEMINI_API_KEY)

# Set up the model
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]


def consulta(sql: str) -> list:
    sql = rf'{sql}'
    raw = r'\"'
    raw2 = r"\'"
    raw3 = r"\\"
    raw4 = r"\\'"

    if r'\"' in sql:
        sql = sql.replace(raw, '"')
    if r"\'" in sql:
        sql = sql.replace(raw2, "'")
    if r"\\" in sql:
        sql = sql.replace(raw3, "")
    if r"\\'" in sql:
        sql = sql.replace(raw4, "'")

    if r'\n' in sql:
        sql = sql.replace(r'\n', '')

    #print(sql)
    #print("----------------------")

    try:
        conexao = sqlite3.connect('dados.db', check_same_thread=False)
        c = conexao.cursor()
        c.execute(sql)
        resposta = c.fetchall()
        conexao.close()
        print("Requisição feita \n----------------------")
        return resposta
    except:
        return []


def previsao(dia: str = '09', mes: str = '08', ano: str = '2024', msg_auto: bool = False) -> list:
    def prever_falha(modelo, dados):
        scaler = StandardScaler()
        dados_scaled = scaler.fit_transform(dados)
        probabilidades = modelo.predict_proba(dados_scaled)[:, 1]  # Probabilidade da classe 1
        return probabilidades

    with open("modelo_previsao.pkl", "rb") as arquivo:
        modelo = pickle.load(arquivo)

    lista_previsoes = list()

    if not msg_auto:
        comando_sql = f"""
        SELECT 
            sensor_id, 
            '[' || GROUP_CONCAT('[' || temperatura || ',' || corrente || ',' || vibracao || ',' || umidade || ']', ',') || ']' AS sensor_data
        FROM 
            dados 
        WHERE 
            DATE(timestamp) = '{ano}-{mes}-{dia}'
        GROUP BY 
            sensor_id
        ORDER BY 
            sensor_id;
        """
        
    else:
        comando_sql = """
        WITH UltimaLeituraGlobal AS (
            SELECT 
                MAX(timestamp) AS ultima_leitura
            FROM 
                dados 
            WHERE 
                DATE(timestamp) = DATE('now')  -- Considera a data atual
        )

        SELECT 
            sensor_id, 
            GROUP_CONCAT(
            '[' || temperatura || ',' || corrente || ',' || vibracao || ',' || umidade || ']', 
            ',' 
            ) AS sensor_data
        FROM 
            dados d
        JOIN 
            UltimaLeituraGlobal ul
        ON 
            d.timestamp BETWEEN datetime(ul.ultima_leitura, '-1 hour') AND ul.ultima_leitura  -- Intervalo de 1 hora antes da última leitura global
        WHERE 
            DATE(d.timestamp) = DATE('now')  -- Considera a data atual
        GROUP BY 
            sensor_id
        ORDER BY 
            sensor_id;
        """

    r_dados = consulta(comando_sql)

    try:
        lista = ast.literal_eval(r_dados)
    except:
        return '[]'

    dados = [(sensor_id, ast.literal_eval(sensor_data)) for sensor_id, sensor_data in lista]

    if not dados:
        return '[]'
    else:
        for i in range(len(dados)):
            dados_transformados = np.array(dados[i][1])

            probabilidades = prever_falha(modelo, dados_transformados)

            lista_previsoes.append(round(sum(probabilidades) / len(probabilidades) * 100, 2))

        return str(lista_previsoes)


def exibir_mensagem():
    while True:
        time.sleep(300)

        prev = previsao(msg_auto=True)

        resposta = chat.send_message(
            f"Organize essa lista, {prev} como se fosse ela tivesse sido retornada pela função previsão para o dia de hoje, "
            f"caso esteja vazia, diga ao usuário que não exixtem dados para o dia solicitado."
            f"Caso seja o dia atual responda que não existem dados pra o dia de hoje."
            f"Sempre ao responder, responda no idioma atual da conversa")

        texto_resposta = resposta.text
        if '\n' in texto_resposta:
            texto_resposta = texto_resposta.rstrip('\n')

        sys.stdout.write("\033[F")
        print_formatted_text(f"\n{texto_resposta}\n{'--' * 30}")

# Cria e inicia uma thread para exibir a mensagem
thread_mensagem = threading.Thread(target=exibir_mensagem)
thread_mensagem.daemon = True  # Faz com que a thread termine quando o programa principal termina
thread_mensagem.start()

dia = f"""
SELECT d.sensor_id, AVG(d.temperatura) AS media_temperatura, AVG(d.corrente) AS media_corrente, AVG(d.vibracao) AS media_vibracao, AVG(d.umidade) AS media_umidade, MIN(d.timestamp) AS primeira_leitura, MAX(d.timestamp) AS ultima_leitura, l.hora AS hora_limite_excedido, l.dado AS dado_limite_excedido FROM dados d LEFT JOIN (SELECT sensor_id, timestamp AS hora, 'temperatura' AS dado FROM dados WHERE temperatura > 40 UNION SELECT sensor_id, timestamp AS hora, 'corrente' AS dado FROM dados WHERE corrente > 5 UNION SELECT sensor_id, timestamp AS hora, 'vibracao' AS dado FROM dados WHERE vibracao > 5.5 UNION SELECT sensor_id, timestamp AS hora, 'umidade' AS dado FROM dados WHERE umidade > 18) AS l ON d.sensor_id = l.sensor_id AND DATE(d.timestamp) = DATE(l.hora) WHERE DATE(d.timestamp) = '2024-05-21' GROUP BY d.sensor_id, l.hora, l.dado;
"""

mes = f"""
SELECT 
    'Primeira leitura do mês' AS tipo,
    MIN(timestamp) AS valor,
    NULL AS sensor_id,
    NULL AS temperatura_media,
    NULL AS corrente_media,
    NULL AS vibracao_media,
    NULL AS umidade_media
FROM dados
WHERE strftime('%m', timestamp) = '08' AND strftime('%Y', timestamp) = '2024'

UNION ALL

SELECT 
    'Última leitura do mês' AS tipo,
    MAX(timestamp) AS valor,
    NULL AS sensor_id,
    NULL AS temperatura_media,
    NULL AS corrente_media,
    NULL AS vibracao_media,
    NULL AS umidade_media
FROM dados
WHERE strftime('%m', timestamp) = '08' AND strftime('%Y', timestamp) = '2024'

UNION ALL

SELECT 
    'Médias de dados' AS tipo,
    NULL AS valor,
    sensor_id,
    AVG(temperatura) AS temperatura_media,
    AVG(corrente) AS corrente_media,
    AVG(vibracao) AS vibracao_media,
    AVG(umidade) AS umidade_media
FROM dados
WHERE strftime('%m', timestamp) = '08' AND strftime('%Y', timestamp) = '2024'
GROUP BY sensor_id

UNION ALL

SELECT 
    'Dias com dados excedendo o limite' AS tipo,
    strftime('%d/%m/%Y', timestamp) AS valor,
    NULL AS sensor_id,
    NULL AS temperatura_media,
    NULL AS corrente_media,
    NULL AS vibracao_media,
    NULL AS umidade_media
FROM dados
WHERE (temperatura > 40 OR corrente > 5 OR vibracao > 5.5 OR umidade > 18)
  AND strftime('%m', timestamp) = '08' AND strftime('%Y', timestamp) = '2024'
ORDER BY tipo, valor;
"""

ranking = f"""
SELECT 
    DATE(timestamp) AS dia, 
    sensor_id,
    AVG(temperatura) AS media
FROM 
    dados
WHERE 
    strftime('%m', timestamp) = '08' -
GROUP BY 
    dia, sensor_id
ORDER BY 
    media DESC;
"""

system_instruction = f"""
Seu nome é Monday, e você atua como assistente especialista em SQL na Reply. Sua principal função é fornecer informações
armazenadas em um banco de dados, conforme solicitado pelo usuário. 
As informações que você retorna não são sobre motores em si, mas sim sobre os dados contidos na tabela do banco de dados.

Sempre, ao receber uma mensagem, indentifique o idioma utilizado e responda nesse mesmo idioma. traduza todas as suas respostas para esse idioma,
Se o usuário falou em inglês, responda em inglês. 
Se o usuário falou italiano, respinda em italiano.
Isso também se aplica as respostas prontas a baixo, traduza elas para o idioma que o usuário estiver utilizando.
Caso o idioma não seja reconhecida, utilize o inglês como padrão.

Se o usuário perguntar algo sobre você, responda de maneira amigável. 
Mantenha um tom formal e gentil para perguntas que não estejam diretamente relacionadas aos exemplos fornecidos. 
Evite responder perguntas sobre programação.

A data atual é {datetime.date.today()}. 
Quando o usuário solicitar dados sem especificar uma data clara, interprete a solicitação de acordo com o contexto e 
forneça as informações do dia solicitado. Sempre que o usuário mencionar "segunda", ele se refere à segunda-feira, 
o dia da semana.

Os dados disponíveis estão armazenados em uma tabela chamada "dados" com a seguinte estrutura:

sensor_id | temperatura | corrente | vibração | umidade | timestamp
A tabela "dados" contém leituras de três sensores, identificados por seus sensor_id:

sensor_id 1: Motor da base (responsável por girar o braço)
sensor_id 2: Motor que levanta o braço
sensor_id 3: Motor que abre a garra.

Ao converter uma solicitação em uma consulta SQL, certifique-se de adequar o comando conforme necessário. 
Se uma pergunta já foi respondida anteriormente, reutilize o comando SQL, atualizando as datas quando necessário.

Exemplos de conversão de perguntas para consultas SQL:
Para uma solicitação de dado específico, como: "Qual a média de temperatura do motor da base no dia 21?"
Use o comando SQL: SELECT AVG(temperatura) FROM dados WHERE sensor_id = sensor_solicitado AND timestamp LIKE 'yyyy-mm-dd';
Altere o comando apenas para refletir os detalhes da solicitação, como o sensor e a data.

Se o usuário solicitar algo como "Em média, quantas leituras são realizadas em um dia", use: SELECT DATE(timestamp) AS dia, COUNT(*) AS quantidade_leituras FROM dados GROUP BY dia ORDER BY dia
Então retorne a média.

Para um resumo mensal, como: "Me dê um resumo dos dados de Maio.", use o seguinte formato:{mes}
O resumo deverá ser apresentado assim, retorne a resposta no mesmo idioma utilizado pelo usuário.
Execute também a função "clima_mes" passando como parâmetros o ano, o mês, o dia inicial do mês e o dia final
Exiba apenas os dados que forem retornados pela função:

A primeira leitura do mês foi realizada no dia X, às [hora:minutos], e a última no dia Y, às [hora:minutos].
Temperatura máxima do mês: [teperatura máxima retornada pela função clima_mes] | Temperatura mínima do mês: [teperatura miníma retornada pela função clima_mes] | Umidade média do mês: [umidade média retornada pela função clima_mes]

Médias de dados de [Mês]:
* Motor da base *
    * Temperatura média: Z° C
    * Corrente média: Z A
    * Vibração média: Z
    * Umidade média: Z%

* Motor que levanta o braço *
    ...

* Motor que abre a garra *
    ...

Dados excedendo limites em [Mês][Caso nenhum dia tenha ultrapassado os limites, não mostre isso]:
    * [Dias, em ordem crescente, exiba cada dia apenas uma vez]

Para previsões de falha, como: "Faça uma previsão com base no dia 9 de agosto."
Execute a função 'previsão', passando o dia, o mês e o ano solicitados, além de False.
Apresente o resultado da seguinte forma,retorne a resposta no mesmo idioma utilizado pelo usuário:

De acordo com os dados de [Data], essas são as chances de falha:
Motor da base: X% de chance de falha
Motor do braço: Y% de chance de falha
Motor da garra: Z% de chance de falha
Para um resumo diário, como: "Me diga os dados do dia 21 de maio."

Para os dados de um dia inteiro, use: {dia}
Apresente o resumo assim, caso necessario traduza a mensagem para outra língua.
Execute também a função "clima_dia" passando como parâmetros o ano, o mês, o dia.
Exiba apenas os dados que forem retornados pela função:

No dia [Data], a primeira leitura foi às [hora:minutos], e a última às [hora:minutos].
Temperatura máxima do dia: [teperatura máxima retornada pela função clima_dia] | Temperatura mínima do dia: [teperatura miníma retornada pela função clima_dia] | Umidade média do dia: [umidade média retornada pela função clima_dia]

* Motor da base *
    * Temperatura média: X° C
    * Corrente média: X A
    * Vibração média: X
    * Umidade média: X%

- Limites ultrapassados[Caso nenhum dia tenha ultrapassado os limites, não mostre isso]:
    * Umidade - [Apenas o horário]

Para um ranking mensal, como: "Faça um ranking de temperatura de agosto, do dia mais quente ao mais frio.", use o comando SQL: {ranking}
Apresente o ranking assim, retorne a resposta no mesmo idioma utilizado pelo usuário.
Exiba apenas os dados que forem retornados pela função:
---------------------------------------------------------------------------
             Ranking de Temperatura (Mais quente -> Mais frio)
---------------------------------------------------------------------------
1º - Dia - Valor (unidade) - Motor
...
10º - Dia - Valor (unidade) - Motor

Para saber o dia mais quente do mês, como: "Qual foi o dia mais quente de agosto?", use o comando: SELECT DATE(timestamp) AS dia, AVG(temperatura) AS media_temperatura FROM dados GROUP BY DATE(timestamp) ORDER BY media_temperatura DESC;

Para verificar a última leitura registrada, use o comando SQL: SELECT MAX(timestamp) FROM dados;

Ao apresentar os resultados, arredonde os valores para duas casas decimais, exiba as datas no formato dd/mm/yyyy e organize as informações de maneira clara e de fácil leitura.
"""

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings,
                              tools=[consulta, previsao, clima_mes, clima_dia])

chat = model.start_chat(enable_automatic_function_calling=True, history=[])

while True:
    user_input = session.prompt(": ")

    if user_input == "sair":
        break

    resposta = chat.send_message(user_input)
    texto_resposta = resposta.text

    if '\n' in texto_resposta:
        texto_resposta = texto_resposta.rstrip('\n')

    print(texto_resposta)
    print("--" * 30)

print("Arrume Danilo")

# Me diga a hora da última leitura realizada
# Me diga a hora em que a última leitura foi realizada
#  Me diga os dados do dia 7 de agosto
# Em qual dia foi realizado a última leitura
# Me diga a média de temperatura do motor da base no dia 7 de agosto
# SELECT ROUND(AVG(temperatura),2) AS Temperatura_Media FROM dados WHERE sensor_id = 1 and timestamp BETWEEN '2024-05-21 00:00:00' AND '2024-05-21 23:59:59'
# SELECT d.sensor_id, AVG(d.temperatura) AS media_temperatura, AVG(d.corrente) AS media_corrente, AVG(d.vibracao) AS media_vibracao, AVG(d.umidade) AS media_umidade, MIN(d.timestamp) AS primeira_leitura, MAX(d.timestamp) AS ultima_leitura, l.hora AS hora_limite_excedido, l.dado AS dado_limite_excedido, CASE WHEN AVG(d.temperatura) > 40 THEN 'Temperatura' WHEN AVG(d.corrente) > 3 THEN 'Corrente' WHEN AVG(d.vibracao) > 4.5 THEN 'Vibracao' WHEN AVG(d.umidade) > 15 THEN 'Umidade' ELSE 'Dentro dos Limites' END AS limite_excedido FROM dados d LEFT JOIN (SELECT sensor_id, timestamp AS hora, 'temperatura' AS dado FROM dados WHERE temperatura > 40 UNION SELECT sensor_id, timestamp AS hora, 'corrente' AS dado FROM dados WHERE corrente > 3 UNION SELECT sensor_id, timestamp AS hora, 'vibracao' AS dado FROM dados WHERE vibracao > 4.5 UNION SELECT sensor_id, timestamp AS hora, 'umidade' AS dado FROM dados WHERE umidade > 15) AS l ON d.sensor_id = l.sensor_id AND DATE(d.timestamp) = DATE(l.hora) WHERE DATE(d.timestamp) = '2024-05-21' GROUP BY d.sensor_id, l.hora, l.dado;
# Me de um resumo do mês de agosto
# Me diga os dados do dia 9 de agosto

# 40, 3, 4,5, 15
# temp, corrente, vibração, umidade

# Base: X
# Outros: Z e Y
