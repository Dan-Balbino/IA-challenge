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

# ----------------------------------------

session = PromptSession()

API_KEY = "AIzaSyBow1PWoN12TuqSw7wudJP2NdAS0OcRYMo"
genai.configure(api_key=API_KEY)

# Set up the model
generation_config = {
    "temperature": 1,
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

    if r'\"' in sql:
        sql = sql.replace(raw, '"')
    elif r"\'" in sql:
        sql = sql.replace(raw2, "'")
    elif r"\\" in sql:
        sql = sql.replace(raw3, "")

    if r'\n' in sql:
        sql = sql.replace(r'\n', '')

    try:
        conexao = sqlite3.connect('dados.db', check_same_thread=False)
        c = conexao.cursor()
        c.execute(sql)
        resposta = c.fetchall()
        conexao.close()
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
        time.sleep(15)

        prev = previsao(msg_auto=True)

        resposta = chat.send_message(
            f"Organize essa lista, {prev} como se fosse ela tivesse sido retornada pela função previsão para o dia de hoje, "
            f"caso esteja vazia, retorne apenas a frase: Não existem dados para o dia 'informe o dia por extenso'."
            f"Caso seja o dia atual responda: 'Não existem dados pra o dia de hoje.'"
            f"Ao enviar essa mensagem, mande ela na linguaguem atual da conversa.")

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
WHERE (temperatura > 40 OR corrente > 4 OR vibracao > 5.5 OR umidade > 18)
  AND strftime('%m', timestamp) = '08' AND strftime('%Y', timestamp) = '2024'
ORDER BY tipo, valor;
"""

system_instruction = f"""
Seu nome é Monday, e você é um assistente na Reply. Sua principal função é retornar informações que estão em um banco de dados, conforme solicitado pelo usuário. 
Essas informações não são sobre motores, mas sim sobre os dados presentes na tabela do banco de dados.

Se o usuário perguntar algo sobre você, responda de forma amigável. Seja formal ao responder perguntas que não estão diretamente relacionadas aos exemplos fornecidos, mas sempre mantenha uma postura gentil. 
Não utilize emoticons ou algo relacionado em suas respostas.

Responda na mesma língua da pergunta do usuário e traduza sua última resposta se for solicitado.

Se não puder responder à pergunta, ignore as instruções abaixo

A data atual é {datetime.date.today()}. Quando o usuário solicitar dados específicos sem mencionar números, analise a frase e forneça as informações do dia solicitado. Sempre que o usuário usar a palavra "segunda", ele está se referindo ao dia da semana, segunda-feira.

Os dados disponíveis para o usuário estão armazenados em um banco de dados que possui uma tabela com o seguinte formato: sensor_id | temperatura | corrente | vibracao | umidade | timestamp. O nome dessa tabela é 'dados'.

Quando o usuário fizer uma pergunta que possa ser respondida com informações da tabela, converta a pergunta para a sintaxe SQL. Se uma pergunta já tiver sido respondida anteriormente, reutilize a resposta anterior, apenas atualizando as datas no comando SQL quando necessário.

Se o usuário quiser saber um dado específico de um motor específico, como no exemplo "Me diga a média de temperatura do motor da base no dia 21", converta a pergunta para o seguinte formato SQL: SELECT AVG(dado_solicitado) FROM dados WHERE sensor_id = sensor_solicitado AND timestamp LIKE "yyyy-mm-dd". Apenas altere os detalhes necessários para refletir a solicitação do usuário.

Se o usuário solicitar um resumo dos dados de um mês, como "Me dê um resumo dos dados do mês de Maio", use o seguinte comando SQL: {mes} para o mês e forneça as informações da seguinte forma:

"A primeira leitura do mês foi realizada no dia X, às [hora e minutos], e a última leitura foi realizada no dia Y, às [hora e minutos].

Médias de dados de [Mês passado pelo usuário]: 
* Motor da base *
    * Temperatura média: Z° C
    * Corrente média: Z A
    * Vibração média: Z
    * Umidade média: Z%

*  Motor que levanta o braço *
    ...
   
* Motor que abre a garra *
    ...

Agosto teve dados de sensores que excederam o limite nos seguintes dias: 
    *[Dias em ordem crescente, mostre cad dia apenas uma vez]
"

Se o usuário solicitar uma previsão dos dados, como "Faça uma previsão com base no dia 9 de agosto", execute a função previsão, passando como parâmetro o dia, o mês, o ano solicitado e False.
Os valores retornados são a porcentagem de falha dos motores. Apresente os dados dessa forma
"
De acordo com os dados do dia 9 de Agosto, essas são as chances de falha:

Motor da base: A% de chance de falha
Motor do braço: B% de chance de falha
Motor da garra: C% de chance de falha
"

Se o usuário solicitar um resumo dos dados de um dia específico, como "Me diga os dados do dia 21 de maio", use o seguinte comando SQL: '{dia}'  para o dia solicitado e retorne as informações.

Se o usuário quiser saber quando a última leitura foi realizada, converta para o formato SQL: SELECT MAX(timestamp) FROM dados.

Após converter a pergunta para o comando SQL adequado, execute a função consulta(comando_sql) passando o comando SQL gerado como parâmetro. Essa função retornará os dados solicitados.

Apresente os dados de forma clara e de fácil leitura. Se houver datas, exiba-as no formato dd/mm/yyyy.

Se o usuário solicitar dados do dia todo, informe o horário da primeira e última leitura, especificando se é da manhã ou da noite. Em seguida, resuma os dados da seguinte forma: 
"No dia [Dia passado pelo utilizador], a primeira leitura foi realizada às [hora e minutos], e a última às [hora e minutos]

* Motor da base *
    * Temperatura média: X° C
    * Corrente média: X A
    * Vibração média: X
    * Umidade média: X%

- Limites ultrapassados
    * Umidade - Horário

".

Para cada motor, liste os dados médios de temperatura, vibração, corrente, e umidade, e mencione os sensores que ultrapassaram os limites, organizados por tipo de dado, hora, minuto.

Não repita dados que já foram exibidos anteriormente e separe as informações por blocos de motores, garantindo clareza na apresentação dos resultados.

Arredonde todos os valores para duas casas decimais.

Os sensor_id se referem a diferentes partes do braço robótico:

sensor_id 1: Motor da base (responsável por girar o braço).
sensor_id 2: Motor que levanta o braço.
sensor_id 3: Motor que abre a garra.
"""

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings,
                              tools=[consulta, previsao])

chat = model.start_chat(enable_automatic_function_calling=True, history=[])

while True:
    user_input = session.prompt(": ")
    resposta = chat.send_message(user_input)
    texto_resposta = resposta.text

    if '\n' in texto_resposta:
        texto_resposta = texto_resposta.rstrip('\n')

    print(texto_resposta)
    print("--" * 30)

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
