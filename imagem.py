import os
import base64
import pandas as pd

# 1. Altere para o caminho da pasta onde estão as suas 31 imagens
# Substitua o final pelo nome exato da pasta onde estão as imagens
pasta_imagens = r"C:\Users\mvini\OneDrive\Área de Trabalho\PROJETOS\Brasil-Hype-Analytics-Cup2026\dashboards\imagens entidades"

dados = []
extensoes_validas = ('.png', '.jpg', '.jpeg', '.webp')

# 2. Percorre a pasta convertendo cada imagem
for arquivo in os.listdir(pasta_imagens):
    if arquivo.lower().endswith(extensoes_validas):
        caminho_completo = os.path.join(pasta_imagens, arquivo)
        
        # Identifica a extensão para montar o prefixo correto
        ext = arquivo.split('.')[-1].lower()
        if ext == 'jpg': 
            ext = 'jpeg'
        
        with open(caminho_completo, "rb") as image_file:
            # Converte o binário da imagem para string Base64
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Monta a estrutura que o Power BI reconhece como imagem
            url_base64 = f"data:image/{ext};base64,{encoded_string}"
            
            # Usa o nome do arquivo (sem a extensão) como ID/Nome correspondente
            nome_identificador = os.path.splitext(arquivo)[0]
            
            dados.append({
                "ID_Imagem": nome_identificador,
                "Imagem_Base64": url_base64
            })

# 3. Salva o resultado em um arquivo CSV na mesma pasta do script
df = pd.DataFrame(dados)
df.to_csv("imagens_prontas_powerbi.csv", index=False, encoding="utf-8")
print("Arquivo 'imagens_prontas_powerbi.csv' gerado com sucesso!")