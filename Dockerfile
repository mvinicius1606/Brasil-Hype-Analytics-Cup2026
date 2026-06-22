FROM python:3.11-slim

# Eu defino o diretório de trabalho interno do contêiner
WORKDIR /app

# Copio o gerenciador de dependências localizado na raiz
COPY requirements.txt .

# Instalo as bibliotecas em modo de produção (sem cache para diminuir a imagem)
RUN pip install --no-cache-dir -r requirements.txt

# Eu realizo o download prévio do dicionário NLTK para acelerar o pipeline
RUN python -m nltk.downloader stopwords

# Copio toda a estrutura da pasta src para dentro do contêiner
COPY src/ /app/

# Garanto que os logs do Python sejam enviados em tempo real para o console do GitHub
ENV PYTHONUNBUFFERED=1

# Eu configuro o caminho padrão de execução do Python para localizar a pasta 'pipeline'
ENV PYTHONPATH=/app

# Comando que aciona o maestro do pipeline
CMD ["python", "pipeline/main.py"]