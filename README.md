# 🏆 BrasilHype World Cup Data Pipeline

## Resumo do Projeto
O **BrasilHype World Cup** é uma arquitetura de dados de ponta a ponta desenvolvida para monitorar, extrair e analisar o sentimento público e o engajamento digital em torno dos jogadores da Seleção Brasileira durante a Copa do Mundo de 2026. 

Este projeto atua como um termômetro social automatizado. Por meio de um ecossistema conteinerizado, o pipeline realiza a ingestão diária de postagens, aplica Processamento de Linguagem Natural (NLP) bilíngue (Português e Inglês) para classificar o sentimento das interações e estrutura os dados em formato colunar (Parquet) em um Data Lake na AWS. O objetivo final é alimentar painéis analíticos no Power BI que medem a polarização, o impacto e a demografia das discussões esportivas rodada a rodada.

---

## 🛠️ Ferramentas Usadas

A infraestrutura foi construída priorizando alta performance, escalabilidade e interoperabilidade de sistemas:

| Ferramenta | Ecossistema | Descrição e Bibliotecas Utilizadas |
| :--- | :--- | :--- |
| **Python 3.11** | 🐍 Linguagem Base | Motor principal da aplicação. Bibliotecas: `pandas` e `pyarrow` (estruturação de dados Parquet), `nltk`, `vaderSentiment` e `LeIA` (análise de NLP e stopwords). |
| **Bluesky / AT Protocol** | 🦋 Ingestão de Dados | Fonte primária de extração de textos sociais via biblioteca `atproto`. |
| **AWS S3** | 🪣 Data Lake | Armazenamento de dados analíticos particionados (ano/mês/dia) via `boto3` e `s3fs`. |
| **AWS CloudWatch** | ☁️ Observabilidade | Monitoramento e ingestão de logs em tempo real do ecossistema via `watchtower`. |
| **Docker** | 🐳 Conteinerização | Empacotamento do motor de extração em uma imagem `python-slim` para portabilidade. |
| **GitHub Actions** | ⚙️ CI/CD | Orquestração de tarefas (Cron Job) para automação diária do gatilho de extração na nuvem. |
| **Power BI** | 📊 Visualização | Consumo direto da One Big Table (OBT) do AWS S3 para a geração de dashboards dinâmicos. |

---

## 📡 Ingestão via Redes Sociais: A Escolha do Bluesky

Durante a fase de arquitetura, enfrentamos bloqueios técnicos comerciais significativos: as APIs do Threads e do Reddit apresentaram barreiras de acesso (paywalls restritivos) e limites de paginação que inviabilizavam uma ingestão volumétrica diária sem custos exorbitantes. 

A solução de engenharia foi pivotar a fonte de dados para a **API do Bluesky**. Apesar de possuir uma base nominalmente menor que os gigantes tradicionais, o Bluesky registrou um tráfego de mais de **44 milhões de usuários ativos** e aproximadamente **159 milhões de visitas mensais** (dados consolidados até junho de 2026). A rede possui um protocolo aberto descentralizado (AT Protocol) que garante excelente taxa de transferência e alta densidade de engajamento passional — o cenário ideal para análise de sentimento esportivo.

### A API do Bluesky (Como Funciona)
A comunicação com o Bluesky é feita de forma nativa e autenticada. A lógica de consumo funciona no seguinte fluxo:
1. **Autenticação:** O cliente estabelece uma sessão usando o *Handle* (nome de usuário) e um *App Password*.
2. **Busca Paginada:** Utilizamos o endpoint `app.bsky.feed.search_posts`, passando o termo de busca (ex: "Vinicius Júnior") e o limite por requisição.
3. **Cursor Dinâmico:** A API retorna um `cursor` ao fim de cada página de resultados, que é retroalimentado no laço de repetição (Loop) para continuar varrendo o histórico até atingir a data limite estipulada (D-1).

### Modelagem de Dados: A Lógica de Árvore
Para contornar o ruído natural das redes sociais, modelamos a ingestão usando um conceito de **Árvore de Interações**:
* **O Tronco (Post Mestre):** A postagem original que cita o jogador. É nela que aplicamos os motores de Inteligência Artificial (NLP) para determinar o sentimento central (Positivo, Negativo ou Neutro) e capturar os adjetivos-chave.
* **As Ramificações:** O volume de comentários, likes e reposts que o tronco gera. 
Em vez de analisar cada comentário individualmente, calculamos a **Polarização** e o **Impacto** do debate baseados na volumetria de galhos que o post mestre sustentou. Se o tronco é negativo e possui mil comentários, inferimos a propagação desse sentimento em escala.

---

## 🐍 Pipeline em Python

O motor da aplicação foi desenvolvido sob o paradigma de Orientação a Objetos (POO) para garantir manutenção ágil e clareza estrutural. A arquitetura é dividida em dois arquivos principais:

* **`extractor.py`**: Contém a classe `BrazilHypeWorldCup`. Ela encapsula os métodos de autenticação, paginação na API, mapeamento do catálogo de entidades, aplicação simultânea de NLP bilíngue, exclusão estruturada de ruídos textuais (Stopwords NLTK) e o particionamento colunar rumo à AWS.
* **`main.py`**: O orquestrador (*Gatilho*). Ele calcula dinamicamente a janela temporal (D-1) e aciona a extração de forma isolada e performática.

### 📇 Catálogo de Entidades e Termos de Busca
Para garantir uma cobertura analítica precisa sem estourar os limites de processamento, estruturamos o robô para focar em uma lista fechada de entidades estratégicas do ecossistema da Copa do Mundo. O catálogo mapeia:
* Os **26 jogadores convocados** que formam o elenco oficial da Seleção Brasileira.
* **Seleções rivais** (adversários do Brasil na fase de grupos e mata-mata).
* A **Comissão Técnica**, monitorando a aceitação do técnico atual (Carlo Ancelotti) e criando métricas comparativas com o técnico do ciclo passado (Tite).
* **Ausências notáveis** (jogadores de peso que ficaram de fora por lesão) e **Lendas históricas** (como Pelé, Ronaldo e Romário) para entender como a saudade ou a comparação afeta o engajamento atual.

Para cada entidade mapeada, o pipeline não realiza uma busca literal simples. Injetamos uma matriz de **termos de busca** e *aliases* customizados. Isso significa que a API varre a rede atrás de nomes completos, apelidos e abreviações (ex: "vini jr", "pombo", "adulto ney"), capturando o engajamento real e orgânico da torcida.

### 🧠 Motor de Análise de Sentimento e Lexicologia Esportiva
A classificação do tom das interações (Positivo, Negativo ou Neutro) exige um rigor matemático. O processamento é aplicado diretamente no tronco da árvore (o post mestre) através de um roteador de idiomas que aciona duas bibliotecas padrão de mercado:
* **VADER Sentiment:** Responsável pela análise polarizada das interações identificadas em inglês (medindo a repercussão internacional e de rivais).
* **LeIA (Léxico para Inferência Adaptada):** Um motor otimizado para as nuances sintáticas do português brasileiro.

**O Dicionário de Palavras Críticas:**
Modelos tradicionais de NLP, treinados com bases acadêmicas ou jornalísticas, frequentemente falham ao interpretar o "dialeto do futebol" brasileiro. Para contornar isso, adicionamos uma camada de inteligência com um dicionário de **palavras críticas** e adjetivos de alto impacto (ex: *bagre, pereba, pardal, frango, craque, gênio, monstro*). 
Se o modelo estatístico base julgar uma frase como "neutra", mas o nosso dicionário rastrear uma dessas palavras-chave, o algoritmo recalcula a nota matemática (Compound) e força a classificação correta. Isso blinda a análise contra ironias sutis e garante uma precisão cirúrgica na avaliação do sentimento esportivo.

### ☁️ Logging na Nuvem
A observabilidade é gerida em nível de produção. Toda a classe base está acoplada à biblioteca `watchtower`, que converte os logs internos do Python (`logging.INFO`, `logging.ERROR`) em fluxos de dados enviados diretamente para o **AWS CloudWatch**. Isso garante que o status de saúde do robô e as métricas de ingestão diária sejam monitoradas em tempo real na AWS, sem necessidade de acesso direto ao servidor onde o Docker está rodando.

### 💻 Como Replicar o Projeto Localmente
1. Realize o clone do repositório:
   ```bash
   git clone [https://github.com/SeuUsuario/BrasilHype-WorldCup.git](https://github.com/SeuUsuario/BrasilHype-WorldCup.git)
   cd BrasilHype-WorldCup

2. Crie um arquivo .env na raiz do projeto contendo as credenciais de autenticação:

Snippet de código
BLUESKY_HANDLE=seu_usuario.bsky.social
BLUESKY_PASSWORD=sua_senha_de_app
AWS_ACCESS_KEY_ID=sua_chave_aws
AWS_SECRET_ACCESS_KEY=seu_segredo_aws
AWS_DEFAULT_REGION=sa-east-1
AWS_S3_BUCKET_NAME=nome_do_seu_bucket

3. Construa a imagem e inicie o ecossistema:

docker build -t brasilhype-pipeline:latest .
docker run --env-file .env brasilhype-pipeline:latest

## ⚙️ DevOps: Docker e CI/CD com GitHub Actions
O projeto não depende de máquinas locais ou servidores manuais para funcionar.

Docker: O ambiente foi selado em uma imagem enxuta baseada em python:3.11-slim, garantindo que todas as dependências (requirements.txt) e downloads paralelos (como o NLTK) sejam imutáveis em qualquer sistema operacional.

GitHub Actions (CI/CD): Configuramos um Cron Job no arquivo main.yml que provisiona uma máquina Ubuntu na nuvem automaticamente todos os dias às 03:00 UTC (Meia-noite de Brasília). O robô injeta os segredos do repositório, monta o contêiner, processa as opiniões da internet das últimas 24 horas e despacha a One Big Table gerada diretamente para o S3, encerrando o servidor logo em seguida para otimização de recursos.

## 📊 Dashboards e Visualização (Power BI)
A consagração dos dados ingeridos ocorre no Power BI. O ecossistema está configurado para consumir os arquivos Parquet do AWS S3 gerando painéis interativos que serão atualizados rodada a rodada, conforme o avanço do Brasil na Copa do Mundo.

### Principais Insights Analisados:

Pirâmide Demográfica de Sentimento: Um cruzamento exato do volume de comentários alocados em espectros Positivos e Negativos.

Taxa de Polarização: Relação matemática entre o barulho (comentários) e a concordância (likes) de um tópico.

Nuvem de Coocorrências e Adjetivos-Chave: Mapeamento lexicológico para identificar com quem um jogador é mais comparado e como é rotulado.

📌 Nota Analítica: Para uma leitura aprofundada dos dados brutos, insights comportamentais e as variações estatísticas específicas consolidadas a cada rodada da seleção, consulte o arquivo detalhado em ANALYTICS.md.