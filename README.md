# 🏆 BrasilHype World Cup Data Pipeline (🏁 Projeto Encerrado)

> 🚨 **STATUS: PROJETO ENCERRADO.** 
> Com a eliminação do Brasil na Copa do Mundo de 2026, nossa campanha chegou ao fim. **O período de monitoramento e ingestão de dados ocorreu entre 12/06 e 07/07.** O projeto cumpriu sua missão de monitorar as redes durante o torneio e todos os dados consolidados foram salvos no Data Lake. Este repositório serve agora como portfólio de uma arquitetura de dados focada em extração, análise de sentimentos e entrega de valor via BI.

## Resumo do Projeto
O **BrasilHype World Cup** foi um projeto de engenharia e análise de dados desenvolvido para monitorar, extrair e analisar o sentimento público e o engajamento digital em torno dos jogadores da Seleção Brasileira durante a Copa do Mundo de 2026. 

Atuando como um termômetro social, o ecossistema realizou a ingestão em lote (*batch*) de postagens, aplicou Processamento de Linguagem Natural (NLP) bilíngue (Português e Inglês) para classificar o sentimento das interações e estruturou os dados em formato colunar (Parquet) em um Data Lake na AWS. O foco principal da arquitetura foi garantir a alimentação dos painéis analíticos no Power BI para medir a polarização, o impacto e a demografia das discussões esportivas rodada a rodada, capturando inclusive anomalias de comportamento das redes.

---

## 🛠️ Ferramentas Usadas

A infraestrutura foi construída priorizando alta performance de extração e interoperabilidade de sistemas analíticos:

| Ferramenta | Ecossistema | Descrição e Bibliotecas Utilizadas |
| :--- | :--- | :--- |
| **Python 3.11** | 🐍 Linguagem Base | Motor principal da aplicação. Bibliotecas: `pandas` e `pyarrow` (estruturação de dados Parquet), `nltk`, `vaderSentiment` e `LeIA` (análise de NLP e stopwords). |
| **Bluesky / AT Protocol** | 🦋 Ingestão de Dados | Fonte primária de extração de textos sociais via biblioteca `atproto`. |
| **AWS S3** | 🪣 Data Lake | Armazenamento de dados analíticos particionados (ano/mês/dia) via `boto3`. |
| **AWS CloudWatch** | ☁️ Observabilidade | Monitoramento e ingestão de logs em tempo real do ecossistema via `watchtower`. |
| **Docker** | 🐳 Conteinerização | Empacotamento do motor de extração em uma imagem `python-slim` para portabilidade e execução padronizada. |
| **Power BI** | 📊 Visualização | Consumo direto da One Big Table (OBT) do AWS S3 para a geração de dashboards dinâmicos. |

---

## 📡 Ingestão via Redes Sociais: A Escolha do Bluesky

Durante a fase de arquitetura, enfrentamos bloqueios técnicos comerciais significativos: as APIs do Threads e do Reddit apresentaram barreiras de acesso (paywalls restritivos) e limites de paginação que inviabilizavam uma ingestão volumétrica sem custos exorbitantes. 

A solução de engenharia foi pivotar a fonte de dados para a **API do Bluesky**. Apesar de possuir uma base nominalmente menor que os gigantes tradicionais, o Bluesky registrou um tráfego de mais de **44 milhões de usuários ativos** e aproximadamente **159 milhões de visitas mensais** (dados consolidados até junho de 2026). A rede possui um protocolo aberto descentralizado (AT Protocol) que garantiu excelente taxa de transferência e alta densidade de engajamento passional — o cenário ideal para análise de sentimento esportivo.

### Modelagem de Dados: A Lógica de Árvore
Para contornar o ruído natural das redes sociais, modelamos a ingestão usando um conceito de **Árvore de Interações**:
* **O Tronco (Post Mestre):** A postagem original que cita o jogador. É nela que aplicamos os motores de Inteligência Artificial (NLP) para determinar o sentimento central (Positivo, Negativo ou Neutro) e capturar os adjetivos-chave.
* **As Ramificações:** O volume de comentários, likes e reposts que o tronco gera. 
Em vez de analisar cada comentário individualmente, calculamos a **Polarização** e o **Impacto** do debate baseados na volumetria de galhos que o post mestre sustentou. Se o tronco é negativo e possui mil comentários, inferimos a propagação desse sentimento em escala.

---

## 🐍 Pipeline em Python e a Lógica de Extração

O motor da aplicação foi desenvolvido sob o paradigma de Orientação a Objetos (POO) para garantir manutenção ágil e clareza estrutural.

### 📇 Catálogo de Entidades e Termos de Busca
Para garantir uma cobertura analítica precisa sem estourar os limites de processamento, estruturamos o código para focar em uma lista fechada de entidades estratégicas do ecossistema da Copa do Mundo. O catálogo mapeou:
* Os **26 jogadores convocados** e o **Técnico**.

Injetamos uma matriz de **termos de busca** e *aliases* customizados (ex: "vini jr", "adulto ney"). A API varreu a rede capturando 100 posts e seus comentários de cada termo, vendo assim o engajamento real e orgânico da torcida.

### 🧠 Motor de Análise de Sentimento e Lexicologia Esportiva
A classificação do tom das interações exigiu um rigor matemático. O processamento foi feito através de um roteador de idiomas que acionou duas bibliotecas padrão de mercado:
* **VADER Sentiment:** Para análises em inglês.
* **LeIA:** Otimizado para o português brasileiro.

**O Dicionário de Palavras Críticas:**
Modelos de NLP frequentemente falham ao interpretar o "dialeto do futebol". Adicionamos uma camada de inteligência com um dicionário de **palavras críticas** (ex: *bagre, pereba, pardal, frango, craque, gênio, monstro*). Isso blindou a análise contra ironias sutis e garantiu precisão cirúrgica.

---

## 🚧 Decisão de Arquitetura: Entrega Analítica vs. Automação Total

O mundo dos dados exige pragmatismo. O plano original envolvia uma orquestração 100% automatizada na nuvem via GitHub Actions. No entanto, durante o andamento da Copa do Mundo, enfrentamos problemas de permissão e restrição de região na AWS que bloquearam o CI/CD.

**O *Timing* Inegociável da Copa:**
Como o evento estava acontecendo e os dashboards precisavam ser entregues rodada a rodada, tomei uma decisão técnica e de negócios: **despriorizar a correção da infraestrutura de automação para focar na entrega de valor analítico.**

A saída foi acionar a nossa ferramenta de resgate, o script de **Backfill** (`backfill.py`). Em vez de um *cron job* na nuvem, o fluxo de dados foi mantido vivo por meio de execuções em *batch* controladas manualmente. 

**Resiliência da API:**
O desafio escalou quando a própria API do Bluesky começou a devolver seguidos erros `502 Bad Gateway` devido ao volume do *backfill*. Refatoramos o extrator implementando um bloco `try/except` robusto com um sistema de **Retry com Espera Exponencial**. Se a rede social engasgasse, o código pausava (5s, 10s...) e tentava recuperar a página perdida em vez de quebrar.

**A Lição Aprendida:** A entrega do produto final (os dados processados) é a prioridade absoluta. Em um cenário com prazo inegociável, construir arquiteturas de contingência (*Disaster Recovery*) prova ser mais valioso do que ter um pipeline perfeitamente automatizado, mas que não entrega os dados a tempo.

---

## 📊 Dashboards e Visualização (Power BI)
A consagração dos dados extraídos e processados ocorreu no Power BI. O ecossistema consumiu os arquivos Parquet do AWS S3 gerando painéis interativos que mostraram a pulsação do torcedor durante o período de **12/06 a 07/07**. 

### Principais Insights Analisados na Campanha:
* **Pirâmide Demográfica de Sentimento:** Um cruzamento exato do volume de comentários alocados em espectros Positivos e Negativos.
* **Taxa de Polarização:** Relação matemática entre o barulho (comentários) e a concordância (likes) de um tópico.
* **Detector de Hate Train:** Cruzamento do aumento de tráfego internacional com o nível de passionalidade para identificar ataques coordenados aos jogadores.
* **Nuvem de Coocorrências e Adjetivos-Chave:** Mapeamento lexicológico para identificar com quem um jogador era mais comparado e como era rotulado após cada partida.
* **Criação de um painel inspirado a plataforma SofaScore** com estátistica de hype e engajamento de cada entidade.

📌 **Nota Analítica:** Para uma leitura aprofundada dos dados brutos, insights comportamentais e as variações estatísticas específicas consolidadas durante a passagem do Brasil pela Copa do Mundo de 2026, consulte o arquivo detalhado em `ANALYTICS.md`.