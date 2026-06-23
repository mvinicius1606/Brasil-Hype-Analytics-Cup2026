import os
import sys
import logging
from datetime import datetime, timedelta
import pandas as pd

# Garante que o Python consiga encontrar os módulos vizinhos se executado diretamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractor import BrazilHypeWorldCup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BrasilHypeBackfill")

def rodar_carga_retroativa():
    logger.info("⏳ Inicializando a engenharia de Backfill (22/06 a 28/06)...")
    
    pipeline = BrazilHypeWorldCup()
    data_corrente = datetime.strptime("2026-06-22", "%Y-%m-%d")
    data_fim = datetime.strptime("2026-06-28", "%Y-%m-%d")
    
    # Lista para juntar a carga de todos os dias na memória do PC
    todos_os_dados_backfill = []
    
    while data_corrente <= data_fim:
        dia_str = data_corrente.strftime("%Y-%m-%d")
        logger.info(f"📅 [BACKFILL] Processando extração filtrada para o dia: {dia_str}")
        
        try:
            # O método processa, envia o dia pro S3 e retorna o DataFrame do dia
            df_dia = pipeline.processar_pipeline_copa(
                data_inicio=dia_str,
                data_fim=dia_str,
                meta_posts_por_entidade=100
            )
            
            if not df_dia.empty:
                todos_os_dados_backfill.append(df_dia)
                
            logger.info(f"✅ [BACKFILL] Dia {dia_str} concluído com sucesso na nuvem.")
        except Exception as e:
            logger.error(f"❌ [BACKFILL] Erro crítico ao processar o dia {dia_str}: {e}")
        
        data_corrente += timedelta(days=1)

    # No final do loop de todos os dias, geramos UM ÚNICO arquivo local pro seu Power BI
    if todos_os_dados_backfill:
        df_completo = pd.concat(todos_os_dados_backfill, ignore_index=True)
        
        # Cria a pasta data caso ela não exista na raiz
        pasta_local = "data"
        if not os.path.exists(pasta_local):
            os.makedirs(pasta_local)
            
        caminho_local_unico = os.path.join(pasta_local, "obt_copa_atual.parquet")
        df_completo.to_parquet(caminho_local_unico, index=False, engine="pyarrow")
        logger.info(f"🎉 [BACKFILL SUCCESS] Arquivo ÚNICO local gerado com TODO o histórico: {caminho_local_unico}")

# ==========================================
# 🚀 O GATILHO DE EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    rodar_carga_retroativa()