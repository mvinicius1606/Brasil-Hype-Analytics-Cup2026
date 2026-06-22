import os
import time
import re
from datetime import datetime, timedelta
import logging
from collections import Counter
import pandas as pd
from dotenv import load_dotenv
import boto3
import watchtower
import nltk
from nltk.corpus import stopwords
from atproto import Client
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from LeIA import SentimentIntensityAnalyzer as LeiaAnalyzer

load_dotenv()
nltk.download('stopwords', quiet=True)

# Configuro o Logger base
logger = logging.getLogger("BrasilHypeCloudPipeline")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class BrazilHypeWorldCup:
    def __init__(self):
        self.handle = os.getenv("BLUESKY_HANDLE")
        self.password = os.getenv("BLUESKY_PASSWORD")
        self.bucket_s3 = os.getenv("AWS_S3_BUCKET_NAME")
        
        # Estabeleço a conexão do Logger com o AWS CloudWatch
        self.configurar_cloudwatch()
        
        self.client = Client()
        self.autenticar_cliente()
        
        self.leia = LeiaAnalyzer()
        self.vader = SentimentIntensityAnalyzer()
        self.motores_nlp = {"pt": self.leia, "en": self.vader}
        
        # Inicializo as listas de exclusão e o dicionário de palavras críticas
        self.stopwords_projeto = set(stopwords.words('portuguese') + stopwords.words('english'))
        self.stopwords_projeto.update({"pra", "pro", "vai", "vou", "vão", "ia", "ta", "tá", "aqui", "aí", "ter", "ser", "sobre"})
        self.palavras_criticas = {"bagre", "pereba", "flop", "pardal", "fraud", "ruim", "horrivel", "frango", "gênio", "craque", "monstro"}
        
        self.catalogo_entidades = [
            {"id": 1, "nome": "Pelé", "funcao": "Lenda", "termos": ["pelé", "pele", "rei pele", "rei pelé"]},
            {"id": 2, "nome": "Ronaldo Fenômeno", "funcao": "Lenda", "termos": ["ronaldo", "fenomeno", "fenômeno", "r9"]},
            {"id": 3, "nome": "Ronaldinho Gaúcho", "funcao": "Lenda", "termos": ["ronaldinho", "gaucho", "gaúcho", "r10"]},
            {"id": 4, "nome": "Romário", "funcao": "Lenda", "termos": ["romário", "romario", "baixinho"]},
            {"id": 5, "nome": "Vinicius Júnior", "funcao": "Jogador", "termos": ["vinicius jr", "vini jr", "vinicius junior", "vinicius júnior", "vini"]},
            {"id": 6, "nome": "Neymar", "funcao": "Jogador", "termos": ["neymar jr", "neymar júnior", "neymar", "ney", "adulto ney", "menino ney"]},
            {"id": 7, "nome": "Rodrygo", "funcao": "Jogador", "termos": ["rodrygo", "rodrygo goes", "rayo"]},
            {"id": 8, "nome": "Estêvão", "funcao": "Jogador", "termos": ["estêvão", "estevão", "estevao", "messinho"]},
            {"id": 9, "nome": "Endrick", "funcao": "Jogador", "termos": ["endrick"]},
            {"id": 10, "nome": "Danilo (Flamengo)", "funcao": "Jogador", "termos": ["danilo do flamengo", "danilo lateral", "danilo ex-juve", "danilo fla"]},
            {"id": 11, "nome": "Danilo Santos", "funcao": "Jogador", "termos": ["danilo do botafogo", "danilo volante", "danilo botafogo", "danilo santos", "danilo fogão"]},
            {"id": 12, "nome": "Ederson (Goleiro)", "funcao": "Goleiro", "termos": ["ederson goleiro", "ederson do fenerbahce", "ederson fenerbahce"]},
            {"id": 13, "nome": "Éderson (Atalanta)", "funcao": "Jogador", "termos": ["ederson da atalanta", "ederson atalanta", "ederson volante"]},
            {"id": 14, "nome": "Danilo (Ambíguo)", "funcao": "Jogador", "termos": ["danilo"]},
            {"id": 15, "nome": "Marquinhos", "funcao": "Jogador", "termos": ["marquinhos"]},
            {"id": 16, "nome": "Gabriel Magalhães", "funcao": "Jogador", "termos": ["gabriel magalhães", "gabriel magalhaes", "magalhães", "magalhaes"]},
            {"id": 17, "nome": "Bremer", "funcao": "Jogador", "termos": ["bremer"]},
            {"id": 18, "nome": "Ibañez", "funcao": "Jogador", "termos": ["ibañez", "ibanez"]},
            {"id": 19, "nome": "Léo Pereira", "funcao": "Jogador", "termos": ["léo pereira", "leo pereira"]},
            {"id": 20, "nome": "Lucas Paquetá", "funcao": "Jogador", "termos": ["lucas paquetá", "lucas paqueta", "paquetá", "paqueta"]},
            {"id": 21, "nome": "Bruno Guimarães", "funcao": "Jogador", "termos": ["bruno guimarães", "bruno guimaraes", "bruninho", "bg"]},
            {"id": 22, "nome": "Casemiro", "funcao": "Jogador", "termos": ["casemiro", "gordomiro"]},
            {"id": 23, "nome": "Alisson", "funcao": "Goleiro", "termos": ["alisson becker", "alisson"]},
            {"id": 24, "nome": "Weverton", "funcao": "Goleiro", "termos": ["weverton"]},
            {"id": 25, "nome": "Raphinha", "funcao": "Jogador", "termos": ["raphinha"]},
            {"id": 26, "nome": "Gabriel Martinelli", "funcao": "Jogador", "termos": ["martinelli", "gabriel martinelli"]},
            {"id": 27, "nome": "Matheus Cunha", "funcao": "Jogador", "termos": ["matheus cunha", "cunha"]},
            {"id": 28, "nome": "Luiz Henrique", "funcao": "Jogador", "termos": ["luiz henrique", "lh"]},
            {"id": 29, "nome": "Rayan", "funcao": "Jogador", "termos": ["rayan"]},
            {"id": 30, "nome": "Igor Thiago", "funcao": "Jogador", "termos": ["igor thiago", "thiago brentford"]},
            {"id": 31, "nome": "João Pedro", "funcao": "Jogador", "termos": ["joão pedro", "joao pedro"]},
            {"id": 32, "nome": "Igor Jesus", "funcao": "Jogador", "termos": ["igor jesus"]},
            {"id": 33, "nome": "Gabriel Jesus", "funcao": "Jogador", "termos": ["gabriel jesus", "g. jesus", "jejim"]},
            {"id": 34, "nome": "Pedro", "funcao": "Jogador", "termos": ["pedro queixada", "pedro do flamengo"]},
            {"id": 35, "nome": "Richarlison", "funcao": "Jogador", "termos": ["richarlison", "pombo"]},
            {"id": 36, "nome": "Savino", "funcao": "Jogador", "termos": ["savino", "savinho"]},
            {"id": 37, "nome": "Gerson", "funcao": "Jogador", "termos": ["gerson", "coringa", "gerson do flamengo"]},
            {"id": 38, "nome": "Thiago Silva", "funcao": "Jogador", "termos": ["thiago silva"]},
            {"id": 39, "nome": "Éder Militão", "funcao": "Jogador", "termos": ["militão", "militao", "énder militao"]},
            {"id": 40, "nome": "Hugo Souza", "funcao": "Goleiro", "termos": ["hugo souza", "neneca"]},
            {"id": 41, "nome": "Bento", "funcao": "Goleiro", "termos": ["bento"]},
            {"id": 42, "nome": "Brasil", "funcao": "Seleção", "termos": ["seleção brasileira", "seleção do brasil", "brasil", "brazil", "canarinho", "seleção"]},
            {"id": 43, "nome": "Tite", "funcao": "Técnico Passado", "termos": ["tite", "adenor", "tite seleção"]},
            {"id": 44, "nome": "Marrocos", "funcao": "Seleção Adversária", "termos": ["marrocos", "marrocos seleção", "moroccans", "seleção marroquina"]},
            {"id": 45, "nome": "Haiti", "funcao": "Seleção Adversária", "termos": ["haiti", "haiti seleção", "haitians", "seleção haitiana"]},
            {"id": 46, "nome": "Escócia", "funcao": "Seleção Adversária", "termos": ["escócia", "escocia", "scotland", "seleção escocesa"]},
            {"id": 47, "nome": "Carlo Ancelotti", "funcao": "Técnico Atual", "termos": ["carlo ancelotti", "ancelotti", "carlo", "pardal"]},
        ]

    def configurar_cloudwatch(self):
        # Integro os logs com o AWS CloudWatch
        try:
            boto3_session = boto3.Session()
            cw_handler = watchtower.CloudWatchLogHandler(
                log_group_name="BrasilHypePipelineLogs",
                boto3_session=boto3_session
            )
            logger.addHandler(cw_handler)
            logger.info("☁️ [AWS] Conexão com CloudWatch estabelecida e configurada.")
        except Exception as e:
            logger.warning(f"⚠️ [AWS] CloudWatch não configurado. Mantendo logs locais: {e}")

    def autenticar_cliente(self):
        # Valido as credenciais e inicio a sessão no Bluesky
        try:
            logger.info(f"🔑 [AUTH] Autenticando perfil {self.handle} no Bluesky...")
            self.client.login(self.handle, self.password)
            logger.info("🎉 [AUTH] Login efetuado com sucesso.")
        except Exception as e:
            logger.error(f"❌ [CRITICAL] Falha de autenticação: {e}")
            raise e

    def identificar_idioma_e_regiao(self, texto):
        # Classifico o idioma com base em marcadores lexicais
        termos_internacionais = [" coach ", " player ", " fraud ", " washed ", " game ", " match ", " team "]
        if any(termo in texto.lower() for termo in termos_internacionais):
            return "en"
        return "pt"

    def extrair_posts_entidade(self, termos_busca, data_inicio, data_fim, meta_posts):
        # Carrego o histórico de postagens paginando a API
        posts_acumulados = []
        cursor_atual = None
        
        dt_inicio = pd.to_datetime(data_inicio).date()
        dt_fim = pd.to_datetime(data_fim).date()
        
        for termo in termos_busca:
            recolhidos_termo = 0
            logger.info(f"🔎 [SEARCH] Varrendo a árvore para o termo: '{termo}'...")
            
            while recolhidos_termo < (meta_posts // len(termos_busca)):
                params = {'q': termo, 'limit': 100}
                if cursor_atual:
                    params['cursor'] = cursor_atual
                    
                try:
                    resultado = self.client.app.bsky.feed.search_posts(params=params) # type: ignore
                    time.sleep(1.5)  
                    
                    if not resultado.posts:
                        break
                        
                    for post in resultado.posts:
                        if not hasattr(post.record, 'text') or not post.record.text.strip(): # type: ignore
                            continue
                            
                        data_post = pd.to_datetime(post.record.created_at).date() # type: ignore
                        
                        if dt_inicio <= data_post <= dt_fim:
                            posts_acumulados.append(post)
                            recolhidos_termo += 1
                            
                        if data_post < dt_inicio:
                            break
                            
                    cursor_atual = resultado.cursor
                    if not cursor_atual or (data_post < dt_inicio):
                        break
                        
                except Exception as e:
                    logger.warning(f"⚠️ [WARN] Falha na paginação do termo '{termo}': {e}")
                    break
                    
        return posts_acumulados

    def analisar_sentimento_mestre(self, texto, idioma):
        # Processo a polaridade via NLP e retorno o sentimento e o compound matemático
        motor = self.motores_nlp[idioma]
        scores = motor.polarity_scores(texto.lower())
        compound = scores["compound"]
        
        if compound > 0.05:
            return "POSITIVO", compound
        elif compound < -0.05:
            return "NEGATIVO", compound
        else:
            if any(p in texto.lower() for p in self.palavras_criticas):
                return "NEGATIVO", -0.1
            return "NEUTRO", 0.0

    def extrair_adjetivos_chave(self, texto, termos_entidade):
        # Isolo as palavras relevantes, removo stopwords e destaco os top adjetivos
        texto_limpo = re.sub(r'[^\w\s]', '', texto.lower())
        palavras_validas = [p for p in texto_limpo.split() if p not in self.stopwords_projeto and len(p) > 2]
        
        contador = Counter(palavras_validas)
        
        # Filtro o nome da própria entidade
        for termo in termos_entidade:
            for t in termo.split():
                if t in contador:
                    del contador[t]
                    
        adjetivos = []
        # Capturo com prioridade as palavras do dicionário crítico
        for p in self.palavras_criticas:
            if p in palavras_validas and p not in adjetivos:
                adjetivos.append(p)
                
        # Completo com as mais frequentes
        for termo, freq in contador.most_common(5):
            if termo not in adjetivos and len(adjetivos) < 3:
                adjetivos.append(termo)
                
        return ", ".join(adjetivos) if adjetivos else "factual"

    def mapear_coocorrencias(self, texto, id_entidade_atual):
        # Mapeio relações cruzadas entre entidades no mesmo post
        texto_low = texto.lower()
        citados = []
        for outra in self.catalogo_entidades:
            if outra["id"] != id_entidade_atual:
                if any(termo in texto_low for termo in outra["termos"]):
                    citados.append(outra["nome"])
        return ", ".join(citados) if citados else "Nenhuma"

    def enviar_dados_s3(self, df):
        # Particiono os dados por Data da Execução e faço o upload para o Data Lake (S3)
        hoje = pd.to_datetime('today')
        df['ano_particao'] = hoje.strftime('%Y')
        df['mes_particao'] = hoje.strftime('%m')
        df['dia_particao'] = hoje.strftime('%d')
        
        caminho_s3 = f"s3://{self.bucket_s3}/trusted/obt_copa/"
        
        try:
            logger.info(f"📤 [S3] Iniciando envio particionado para {caminho_s3}...")
            df.to_parquet(
                caminho_s3,
                index=False,
                engine="pyarrow",
                partition_cols=['ano_particao', 'mes_particao', 'dia_particao']
            )
            logger.info("✅ [S3] Carga no Data Lake concluída com sucesso!")
        except Exception as e:
            logger.error(f"❌ [S3] Falha na gravação no S3: {e}")

    def processar_pipeline_copa(self, data_inicio=None, data_fim=None, meta_posts_por_entidade=100):
        # Eu calculo dinamicamente a data de ontem (D-1) se as datas não forem informadas
        if data_inicio is None:
            data_inicio = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if data_fim is None:
            data_fim = data_inicio  # Janela diária foca apenas no dia anterior completo
            
        logger.info(f"🚀 [PIPELINE] Processando árvore da Copa de forma automatizada para o dia: {data_inicio}.")
        registros_obt = []
        
        for idx, entidade in enumerate(self.catalogo_entidades, start=1):
            logger.info(f"📦 [{idx}/{len(self.catalogo_entidades)}] Minerando árvore de: '{entidade['nome']}'...")
            
            posts_brutos = self.extrair_posts_entidade(
                termos_busca=entidade["termos"],
                data_inicio=data_inicio,
                data_fim=data_fim,
                meta_posts=meta_posts_por_entidade
            )
            
            for post in posts_brutos:
                texto = post.record.text
                id_post = getattr(post, 'uri', 'unknown')
                likes = int(post.like_count or 0)
                comentarios = int(post.reply_count or 0) 
                reposts = int(post.repost_count or 0)
                
                idioma = self.identificar_idioma_e_regiao(texto)
                nacionalidade = "Internacional" if idioma == "en" else "Nacional"
                
                sentimento, score_compound = self.analisar_sentimento_mestre(texto, idioma)
                
                # Garanto a divisão exata matemática de comentários para o gráfico de pirâmide demográfica
                if score_compound > 0:
                    comentarios_positivos = round(comentarios * score_compound)
                    comentarios_negativos = comentarios - comentarios_positivos
                elif score_compound < 0:
                    comentarios_negativos = round(comentarios * abs(score_compound))
                    comentarios_positivos = comentarios - comentarios_negativos
                else:
                    comentarios_positivos = comentarios // 2
                    comentarios_negativos = comentarios - comentarios_positivos

                adjetivos_chave = self.extrair_adjetivos_chave(texto, entidade["termos"])
                coocorrencias = self.mapear_coocorrencias(texto, entidade["id"])
                
                intensidade_impacto = abs(score_compound) * (1 + likes + reposts)
                polarizacao = comentarios / (likes + 1)
                
                is_passional = ("!" in texto or texto.isupper() or any(p in texto.lower() for p in self.palavras_criticas))
                subjetividade = "Sentimental/Passional" if is_passional else "Factual/Informativo"
                
                registros_obt.append({
                    "id_post": id_post,
                    "id_entidade": entidade["id"],
                    "nome_entidade": entidade["nome"],
                    "funcao": entidade["funcao"],
                    "nacionalidade": nacionalidade,
                    "data": pd.to_datetime(post.record.created_at).strftime('%Y-%m-%d'),
                    "sentimento_post": sentimento,
                    "adjetivos_chave": adjetivos_chave,
                    "coocorrencias": coocorrencias,
                    "comentarios_positivos": int(comentarios_positivos),
                    "comentarios_negativos": int(comentarios_negativos),
                    "numero_comentarios_total": comentarios,
                    "numero_likes": likes,
                    "numero_reposts": reposts,
                    "polarizacao": round(polarizacao, 4),
                    "subjetividade": subjetividade,
                    "intensidade_impacto": round(intensidade_impacto, 2)
                })
                
        df_obt = pd.DataFrame(registros_obt)
        logger.info(f"✨ [SUCCESS] Árvore consolidada. Total de {len(df_obt)} posts computados.")
        
        # Despacho o arquivo consolidado direto para o AWS S3
        if not df_obt.empty:
            self.enviar_dados_s3(df_obt)
            
        return df_obt