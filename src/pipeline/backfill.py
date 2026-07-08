import os
import sys
import time
import logging
from datetime import datetime, timedelta
import pandas as pd

# Garante que o Python consiga encontrar os módulos vizinhos se executado diretamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractor import BrazilHypeWorldCup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BrasilHypeBackfill")

def rodar_carga_retroativa():
    logger.info("⏳ Inicializando a engenharia de Backfill (29/06 a 07/07)...")
    
    pipeline = BrazilHypeWorldCup()
    data_corrente = datetime.strptime("2026-06-29", "%Y-%m-%d")
    data_fim = datetime.strptime("2026-07-07", "%Y-%m-%d")
    
    # Lista para juntar a carga de todos os dias na memória do PC
    todos_os_dados_backfill = []
    
    while data_corrente <= data_fim:
        dia_str = data_corrente.strftime("%Y-%m-%d")
        logger.info(f"📅 [BACKFILL] Processando extração filtrada para o dia: {dia_str}")
        
        # ==========================================
        # 🔄 SISTEMA DE RETRY (Tentativas em caso de falha na API 500/502)
        # ==========================================
        max_tentativas = 3
        for tentativa in range(1, max_tentativas + 1):
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
                break  # Sucesso! Sai do loop de tentativas e vai para o próximo dia
                
            except Exception as e:
                logger.warning(f"⚠️ [WARN] Falha no dia {dia_str} (Tentativa {tentativa}/{max_tentativas}): {e}")
                
                if tentativa == max_tentativas:
                    logger.error(f"❌ [BACKFILL] Desistindo do dia {dia_str} após {max_tentativas} tentativas. Registrando em DLQ.")
                    # Cria a fila de erros para não travar o código
                    with open("falhas_backfill.txt", "a") as f:
                        f.write(f"{dia_str}\n")
                else:
                    # Espera exponencial: 10s na 1ª falha, 20s na 2ª falha...
                    tempo_espera = 10 * tentativa
                    logger.info(f"⏳ Servidor sobrecarregado. Aguardando {tempo_espera}s antes da nova tentativa...")
                    time.sleep(tempo_espera)
        
        # Passa para o próximo dia independentemente de sucesso ou falha total após as tentativas
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
    else:
        logger.error("❌ Nenhum dado foi coletado durante o backfill.")

# ==========================================
# 🚀 O GATILHO DE EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    rodar_carga_retroativa()