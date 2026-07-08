# 📊 Analytics & Insights - BrasilHype World Cup

O projeto chegou oficialmente ao fim com a eliminação do Brasil na Copa do Mundo de 2026. Ao longo da nossa jornada, a variação de sentimento, o impacto das partidas e o engajamento da torcida nas redes sociais foram documentados e consolidados em três dashboards principais, divididos cronologicamente para refletir o clima de cada fase do torneio. 

O primeiro painel engloba os **primeiros 10 dias de Copa (12/06 a 21/06)**, capturando a expectativa inicial; o segundo reflete o impacto e a repercussão da **rodada do jogo contra a Escócia (22/06 a 28/06)**, momento em que detectamos anomalias na rede; e o terceiro e último painel documenta o clima da nossa reta final, cobrindo a alta tensão do período entre o **jogo contra o Japão até a fatídica eliminação pela Noruega (29/06 a 07/07)**.
## 🟢 Fase 1: Expectativa, Estreia e Instabilidade (12/06 a 21/06)

**Dashboard de Referência:**

<div align="center">
  <img src="dashboards/prints dashboards/1782342554448.jpg" width="800">
</div>


O primeiro ciclo de monitoramento compreendeu os 10 dias iniciais da Copa do Mundo, englobando a tensão pré-torneio e os primeiros confrontos contra Marrocos e Haiti. Para esta análise preliminar, o pipeline processou uma amostra robusta de **3.000 postagens-tronco** (expandidas para milhares de interações secundárias) via API do Bluesky. O objetivo foi cruzar o sentimento processado via NLP (LeIA e VADER) com a intensidade do engajamento para separar o "ruído" das redes de *insights* táticos reais.

### 📐 Metodologia e Modelagem DAX (O Motor do Dashboard)

Para traduzir a volumetria de textos em indicadores visuais claros, estruturamos medidas complexas em DAX que categorizam e isolam entidades específicas no modelo semântico:

*   **Termômetro para o Hexa (42,6%):** Representa o "Otimismo Geral". Em DAX, essa medida foi construída utilizando a função `CALCULATE`, filtrando o modelo exclusivamente pela entidade "Brasil" (ID 4) e dividindo o volume de interações positivas pelo total de comentários válidos.
*   **Confiança no Elenco (41,5%):** Representa a "Aprovação Direta" das peças individuais. A medida aplica um filtro restrito na `Dimensão_Entidades`, isolando apenas os **26 jogadores convocados**, excluindo técnico, seleção e lendas históricas.
*   **O Algoritmo do HypeScore:** Inspirado em plataformas esportivas (como o SofaScore), criamos um índice normalizado (de 0 a 10). A fórmula DAX multiplica o **Saldo de Comentários** (Positivos - Negativos) pela **Intensidade do Post** (`1 + Likes + Reposts`). Isso garante que um post viral tenha peso exponencial na nota final do jogador, penalizando a irrelevância e premiando o engajamento massivo.

### 📊 Principais Insights e Anomalias do Período

A visualização do gráfico de barras (*Opinião sobre a Seleção Brasileira*) e os cartões laterais revelam o comportamento e a volatilidade do torcedor nesta primeira janela:

#### 1. A Montanha-Russa: Efeito Marrocos vs. Haiti
O início da jornada foi marcado por extrema instabilidade. O jogo contra o Marrocos (entre 13 e 14/06) gerou um pico severo de rejeição, consolidando um saldo negativo de **-41 no dia 14/06**. Contudo, os dados mapearam uma tendência de recuperação técnica e emocional na janela do jogo contra o Haiti (19 a 21/06), culminando no ápice de positividade do período no dia 19/06 (49 pontos positivos).

#### 2. O Cenário de Ancelotti & Neymar
*   **Carlo Ancelotti (Técnico):** Apesar da instabilidade do time, o treinador demonstrou uma resiliência notável na opinião pública, sustentando **42,3% de aprovação** e um HypeScore sólido de **6,1**.
*   **Neymar (Atacante):** O monitoramento detectou o "peso da expectativa". O jogador se consolidou como o líder em saldo negativo absoluto (-94 interações) e obteve um HypeScore baixo de **3,4** (com **30,9% de aprovação**). A inteligência de dados revelou um padrão curioso: os piores índices de aprovação de Neymar ocorreram exatamente nos dias de jogos, evidenciando uma cobrança passional severa mesmo quando ele não estava em campo.

#### 3. A "Polarização Raphinha" (Case de Sucesso do Modelo)
Este foi o *insight* técnico mais rico da primeira fase. Raphinha apresentou um volume altíssimo de críticas, o que matematicamente deveria afundar sua nota. No entanto, ele finalizou a rodada com um **HypeScore de 6,1** (Top 3 do elenco). 
*   **Por que isso aconteceu?** O nosso cálculo de impacto provou que o barulho negativo em torno do jogador foi totalmente neutralizado por uma base de defensores que produziu engajamento de **alta intensidade**. É um caso clássico onde a polarização extrema não destrói a relevância da entidade, classificando Raphinha em um estado de *equilíbrio instável*.

#### 4. Top & Bottom Performers
O algoritmo de HypeScore destacou **Endrick (6,1)** e **Vini Jr. (5,8)** ao lado de Raphinha como os motores positivos da Seleção. No extremo oposto, o setor defensivo sofreu as piores sanções da torcida: **Léo Pereira (2,1)**, **Alisson (2,3)** e **Igor Thiago (3,0)** lideraram a base da pirâmide de rejeição inicial.

## 🟡 Fase 2: O Triunfo sobre a Escócia e a Anomalia do "Hate Train" (22/06 a 28/06)

**Arquivos de Referência:** 
<div align="center">
  <img src="dashboards/prints dashboards/1782837361520 (1).jpg" width="800">
  <br><br>
  <img src="dashboards/prints dashboards/1782837362016.jpg" width="800">
</div>
<br>

O segundo ciclo de monitoramento englobou o período de consolidação após a vitória contra a Escócia e a escalada de tensão para o confronto contra o Japão. Analiticamente, a expectativa era de que a tendência de alta no Otimismo Geral decolasse de vez. 

No entanto, o carregamento dos dados revelou um cenário assustador: o painel foi inundado por uma onda de negatividade extrema, com números piores do que os do tenso jogo contra o Marrocos na primeira fase, atingindo um pico de rejeição de -85 no dia 28/06. Em um primeiro momento, a reação natural de engenharia foi assumir uma falha técnica: *"A ingestão falhou e o pipeline quebrou, invertendo os sentimentos"*. 

Contudo, ao destrinchar a base de dados, a resposta não estava no código, mas em uma **anomalia comportamental da rede**: o transbordamento de uma guerra virtual (*Hate Train*) entre torcedores de Brasil e Japão.

### 📐 Metodologia Analítica: Validando a Anomalia com DAX

Para não basear a análise em "achismos" e comprovar que o modelo estava lendo corretamente um ataque coordenado, desenvolvemos três métricas de validação cruzada no Power BI utilizando DAX avançado:

#### 1. Salto de Passionalidade (Filtro de Subjetividade)
A primeira etapa foi isolar os comentários negativos para auditar se possuíam base tática/factual ou se eram puramente emocionais (caixa alta, excesso de pontuação, xingamentos). 
*   **A Medida DAX:** Criamos um indicador que calcula o percentual de postagens com a *flag* `Sentimental/Passional` (gerada pelo nosso motor de NLP) sobre o volume total de interações negativas do dia.
*   **O Insight:** Os dados confirmaram a quebra de padrão. A partir de 25/06, quando o confronto Brasil x Japão foi confirmado, a passionalidade saltou de um patamar estável de **14,5%** para impressionantes **41,6%** no dia 28/06. O torcedor parou de analisar o jogo e partiu para o ataque coordenado.

#### 2. Pico Internacional vs. O Paradoxo do Idioma
O painel detectou um aumento substancial no percentual de comentários originados de contas com marcadores internacionais. 
*   **A Análise Semântica:** Ao cruzar essa volumetria com a Nuvem de Palavras (segunda imagem), o dashboard revelou um *plot twist* de ingestão. Apesar do fluxo internacional e de o Japão ser o Top 3 global de usuários ativos no Bluesky, o idioma predominante nos ataques rastreados ainda era o **Português** (como visível em termos como *cunhã*, *seleção*, *lixo*). 
*   **O Diagnóstico:** A arquitetura de dados levantou duas hipóteses comportamentais claras: o Brasil estava sofrendo "fogo amigo" de torcedores locais embarcando no *hate* por engajamento (*bait*), ou agentes internacionais estavam utilizando tradutores automáticos para direcionar as ofensas na língua nativa dos jogadores.

#### 3. Cruzamento de Entidades: O Alvo Principal do Furacão
Para fechar o diagnóstico e atestar o *Hate Train*, utilizamos o DAX para cruzar a `Negatividade Absoluta` com a `Dimensão_Entidades`.
*   **O Insight Tático:** Se a negatividade fosse orgânica, ela seria direcionada aos jogadores com os piores desempenhos em campo. O painel mostrou o exato oposto. A tabela de "Vítimas" (canto superior direito) comprova que o ataque foi cirurgicamente focado nos nossos pilares e melhores jogadores: **Bruno Guimarães (-136)**, **Neymar (-133)**, **Vinicius Júnior (-94)** e no técnico **Carlo Ancelotti (-70)**. 

A conclusão analítica foi irrefutável: o pipeline não estava quebrado. Ele funcionou com tamanha precisão que conseguiu mapear, quantificar e isolar uma tentativa coordenada de desestabilização psicológica dos nossos principais nomes às vésperas de um jogo eliminatório.