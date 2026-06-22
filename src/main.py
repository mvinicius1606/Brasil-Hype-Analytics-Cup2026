# ==============================================================================
# GATILHADOR DIÁRIO AUTOMATIZADO - BRASILHYPE WORLD CUP (D-1 CRON JOB)
# ==============================================================================

import os
import logging
from datetime import datetime, timedelta
from pipeline.extractor import BrazilHypeWorldCup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BrasilHypeGatilho")

def disparar_carga_diaria():
    logger.info("🎬 [MAIN_START] Inicializando a orquestração diária automatizada via GitHub Actions...")
    
    # 1. Instancio o motor de dados
    pipeline = BrazilHypeWorldCup()
    
    # 2. Eu calculo ontem apenas para logs e nomenclatura de arquivos locais
    ontem_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    TOTAL_POSTS_POR_JOGADOR = 100  
    
    # 3. Disparo o processo sem passar datas fixas para ativar o gatilho automático de D-1
    df_obt_final = pipeline.processar_pipeline_copa(
        data_inicio=None,
        data_fim=None,
        meta_posts_por_entidade=TOTAL_POSTS_POR_JOGADOR
    )
    
    # 4. Gravo o espelho de segurança local com a data da carga
    if not df_obt_final.empty:
        os.makedirs("data", exist_ok=True)
        caminho_arquivo = f"data/obt_carga_diaria_{ontem_str}.parquet"
        
        df_obt_final.to_parquet(caminho_arquivo, index=False, engine="pyarrow")
        logger.info(f"✨ [MAIN_SUCCESS] Execução diária concluída! Matriz de {ontem_str} salva localmente e despachada para a AWS.")
    else:
        logger.error(f"⚠️ [MAIN_FAIL] O DataFrame final retornou vazio para o dia anterior.")

if __name__ == "__main__":
    disparar_carga_diaria()