manual_instrucoes = """
Manual de Instruções para Motores de Braço Robótico
1. Introdução
Este manual contém informações sobre a operação segura e eficiente dos motores utilizados em um braço robótico. Ele fornece orientações para minimizar os riscos associados a fatores como temperatura, corrente e vibrações excessivas, garantindo a longevidade dos componentes do sistema.

2. Especificações dos Motores
Tipo de Motor: Motor de passo
Faixa de Temperatura de Operação: 0°C a 45°C
Corrente Nominal: 5 A
Nível Máximo de Vibração Tolerada: 5.5 mm/s²

3. Riscos de Operação
3.1 Riscos de Temperatura Elevada
Perigo: Temperaturas elevadas acima dos níveis operacionais recomendados (acima de 45°C) podem causar o seguinte:

Danos aos componentes internos do motor, como isolamento dos enrolamentos.
Aumento da resistência elétrica, levando a um aquecimento adicional.
Falha prematura dos rolamentos devido à dilatação térmica.
Desgaste acelerado dos materiais e perda de precisão no controle de movimento.
Consequências:

O desempenho do braço robótico será comprometido.
Há um risco elevado de falhas catastróficas que podem causar a interrupção total das operações.
Medidas de Correção:

Instale sensores de temperatura próximos aos motores para monitoramento contínuo.
Utilize dissipadores de calor ou sistemas de refrigeração (ventiladores, radiadores) para dissipar o calor.
Certifique-se de que o ambiente de operação do braço robótico tenha ventilação adequada ou controle de temperatura.
Reduza a carga operacional do braço robótico para diminuir o esforço do motor e, consequentemente, a geração de calor.

3.2 Riscos de Corrente Elevada
Perigo: Correntes acima do limite nominal (5 A) resultam em:

Sobrecarga nos enrolamentos dos motores, causando aumento significativo da temperatura.
Queima dos enrolamentos, resultando em curto-circuitos ou falha total do motor.
Redução drástica da vida útil do motor devido à degradação acelerada dos componentes.
Consequências:

Danos permanentes ao motor, necessitando substituição.
Falha completa do braço robótico, com riscos de acidentes operacionais.
Medidas de Correção:

Use drivers de motor com proteção contra sobrecorrente para limitar o fluxo de corrente excessiva.
Ajuste os parâmetros de controle do motor (corrente de fase, microstepping) para operar dentro dos limites seguros.
Verifique periodicamente as fontes de alimentação para garantir que forneçam correntes estáveis.
Distribua a carga entre múltiplos motores, se possível, para evitar sobrecarga em um único componente.

3.3 Riscos de Vibração Excessiva
Perigo: Vibrações muito elevadas (acima de 5.5 mm/s²) podem resultar em:

Desgaste acelerado dos rolamentos e eixos do motor.
Perda de precisão no controle de posicionamento, causando movimentos erráticos ou imprecisos do braço robótico.
Afrouxamento de componentes mecânicos, que podem comprometer toda a estrutura do sistema.
Consequências:

Redução da precisão operacional e perda de eficiência.
Danos progressivos aos motores, eixos e engrenagens, aumentando os custos de manutenção.
Medidas de Correção:

Instale amortecedores de vibração entre os motores e a estrutura do braço robótico.
Realize inspeções regulares dos rolamentos e do alinhamento mecânico do sistema.
Reduza as velocidades de operação e acelerações, para diminuir o impacto de vibrações.
Certifique-se de que o braço robótico esteja montado em uma superfície estável e livre de outras fontes de vibração.

4. Manutenção Preventiva
Para garantir a vida útil prolongada dos motores e a eficiência do braço robótico, siga estas práticas de manutenção preventiva:

Verificações diárias de temperatura durante a operação.
Inspeção mensal dos rolamentos para verificar folgas ou desgastes.
Monitoramento semanal da corrente de operação para garantir que está dentro do especificado.
Lubrificação dos componentes móveis do braço conforme especificado no manual de manutenção.

5. Procedimentos de Emergência
Em caso de falhas ou operação anormal:

Desligue imediatamente o braço robótico.
Verifique as leituras de temperatura e corrente para identificar possíveis causas.
Inspecione visualmente os motores e rolamentos em busca de sinais de desgaste ou danos.
Substitua qualquer motor danificado ou sobreaquecido antes de retomar as operações.
"""

formato_pdf = f"""
[Preencha esse relatório de acordo com as informações retornadas pela função consulta. Não exiba essa frase]
Relatório Técnico
Data: [Data, no formato dia/mês/ano, em que o relatório foi gerado]
Empresa/Organização: FIAP em parceria com a Reply
Nome do Técnico ou Engenheiro Responsável: [Seu nome] + Grupo FailGuard
1. Identificação da Máquina
Nome/Modelo da Máquina: BR-FGRF
Número de Série: 2512A
Localização: Linha de Montagem
2. Resumo Executivo
Objetivo do Relatório: [Coloque o objetivo do relátorio, de acordo com as informações que serão colocadas no relatório]
Principais Constatações:[Se um ou mais limites tenham sido ultrapassados, informe os problemas identificados durante a operação do braço.]
3. Descrição Técnica da Máquina
Especificações Técnicas:O braço é equipado com 4 motores de passo.
Componentes: Os principais componentes do braço robótico incluem:
    Motores de passo - (Nema 17)
    Câmera térmica para monitoramento da temperatura - (AMG88xx)
    Sensores de vibração - (MPU6050)
    Sensor de corrente elétrica - (ACS712)
    Controlador de movimento - (Arduino Mega / CNC Shield)
    Sistema de comunicação - (Esp32)
4. Histórico de Operação
Horas de Trabalho: 26.5 horas
Ciclos de Operação: 300 ciclos realizados
Condições de Operação:
    Temperatura ambiente: 25°C
    Temperatura média do braço durante a operação: [Temperatura do braço]
    Corrente média do braço: [Corrente do braço]
    Vibração da base: [Vibração da base]
    Vibração do braço: [Vibração do braço]
    Vibração da garra: [Vibração da garra]   
Dias com limites de leitura ultrapassados:
    [Insira em formato de listae em ordem crescente. por exemplo:
    -07/10/2024
    -18/10/2024]
    [Caso a quantidade de dias em sequência seja maior que 4, faça da seguinte forma:
    -07/10/2024...20/10/2024]
5. Procedimentos de Inspeção ou Manutenção
Métodos Utilizados: Os dados de temperatura, corrente e vibração são monitorados continuamente durante a operação da máquina.
Ferramentas e Instrumentos:
    Uma câmera térmica para monitorar a temperatura..
    3 sensores de vibração para monitorar a vibração em pontos do braço.
    Um sensor de corrente para medir a corrente elétrica que chega aos motores.
Critérios de Avaliação: Os limites de operação para temperatura, corrente e vibração são definidos no manual de instruções do braço robótico.
6. Diagnóstico e Condição da Máquina
Desempenho Atual: [Coloque uma resposta condizente com os dados apresentados, levando em conta o limite de cada medida, e que a temperatura ambiente é 25°C]
Análise de Vibrações, Ruídos, etc.: [Coloque uma resposta condizente com os dados apresentados]
Desgaste e Danos: Não foram observados sinais de desgaste ou danos nos componentes do braço robótico.
7. Recomendações
Reparos Necessários: Não há reparos necessários no momento.
Manutenção Preventiva: [Sugestões de ações preventivas para melhorar o desempenho ou evitar falhas]
Ações Corretivas: Nenhuma ação corretiva é necessária.
8. Conclusão
Resumo das Condições: [Avaliação geral da condição da máquina, levando em conta o limite de cada medida, os dados apresentados e que a temperatura ambiente é 25°C]
Prognóstico: [Expectativas para o funcionamento futuro da máquina com base no estado atual, levando em conta o limite de cada medida, e que a temperatura ambiente é 25°C]

"""