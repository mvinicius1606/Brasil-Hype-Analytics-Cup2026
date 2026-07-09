import os
import base64
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw

# Caminho da pasta
pasta_imagens = r"C:\Users\mvini\OneDrive\Área de Trabalho\PROJETOS\Brasil-Hype-Analytics-Cup2026\dashboards\assets\imagens entidades"

dados = []
extensoes_validas = ('.png', '.jpg', '.jpeg', '.webp')

for arquivo in os.listdir(pasta_imagens):
    if arquivo.lower().endswith(extensoes_validas):
        caminho_completo = os.path.join(pasta_imagens, arquivo)
        
        img = Image.open(caminho_completo).convert("RGBA")
        largura, altura = img.size
        
        # O Desvio da CBF (O arquivo DEVE ter "cbf" no nome)
        if "cbf" in arquivo.lower():
            maior_lado = max(largura, altura)
            lado_seguro = int(maior_lado * 1.1)
            
            img_quadrada = Image.new("RGBA", (lado_seguro, lado_seguro), (255, 255, 255, 0))
            
            pos_x = int((lado_seguro - largura) / 2)
            pos_y = int((lado_seguro - altura) / 2)
            img_quadrada.paste(img, (pos_x, pos_y))
            
            menor_lado = lado_seguro
        else:
            # Jogadores (Corte Central)
            menor_lado = min(largura, altura)
            esquerda = (largura - menor_lado) / 2
            topo = (altura - menor_lado) / 2
            direita = (largura + menor_lado) / 2
            fundo = (altura + menor_lado) / 2
            img_quadrada = img.crop((esquerda, topo, direita, fundo))
        
        # Máscara e Transparência
        mascara = Image.new("L", img_quadrada.size, 0)
        draw = ImageDraw.Draw(mascara)
        draw.ellipse((0, 0, menor_lado, menor_lado), fill=255)
        img_quadrada.putalpha(mascara)
        
        # Redução para não quebrar no Power BI (Limite de 32k)
        img_quadrada.thumbnail((100, 100))

        buffer = BytesIO()
        img_quadrada.save(buffer, format="PNG")
        imagem_bytes = buffer.getvalue()
        
        # O prefixo sagrado do Base64 (Intocável)
        encoded_string = base64.b64encode(imagem_bytes).decode('utf-8')
        url_base64 = f"data:image/png;base64,{encoded_string}"
        
        nome_identificador = os.path.splitext(arquivo)[0]
        
        dados.append({
            "ID_Imagem": nome_identificador,
            "Imagem_Base64": url_base64
        })

df = pd.DataFrame(dados)
df.to_csv("imagens_prontas_powerbi.csv", index=False, encoding="utf-8")
print("Processo concluído com sucesso!")