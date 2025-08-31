from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as nb
import pytesseract
from googletrans import Translator
from flask import render_template, request, jsonify
from main import app
import base64
import io 

MAPA_GOOGLETRA = {
    'eng': 'en',
    'por': 'pt',
    'jpn': 'ja',
    'chi_sim': 'zh-CN', 
    'kor': 'ko',
    'spa': 'es',
    # Incluir também os códigos ISO para caso venham do frontend (para idioma_novo)
    'en': 'en',
    'pt': 'pt',
    'ja': 'ja',
    'zh': 'zh-CN', 
    'ko': 'ko',
    'es': 'es',
}
# Chama o popup
@app.route("/")
def popup():
    return render_template("popup.html")


# Iniciar código
@app.route("/", methods=["POST"])
def traduzir_imagem():
    dados = request.get_json()
    idioma_atual_raw = dados.get('atual')
    idioma_novo_raw = dados.get('novo')
    imagem_base64 = dados.get('imagem')

    # Verifica se a imagem foi enviada
    if not imagem_base64:
        return jsonify({"error": "Nenhuma imagem foi enviada.", "texto_traduzido": "Erro."}), 400


    # Alterações na imagem
    if "base64," in imagem_base64:
        imagem_base64 = imagem_base64.split("base64,")[1]
    try:
        imagem_bytes = base64.b64decode(imagem_base64)
        screenshot_pil = Image.open(io.BytesIO(imagem_bytes))#se transformou em imagem
        imagem_original = screenshot_pil
        img = cv2.cvtColor(nb.array(screenshot_pil), cv2.COLOR_RGB2BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.Laplacian(img,cv2.CV_8U)
        _, screenshot_pil = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY_INV)

    except Exception as e:
        return jsonify({"error": f"Erro ao decodificar a imagem: {e}", "texto_traduzido": "Erro."}), 400 #tem que atualizar dps
    
    idioma_atual_gt = MAPA_GOOGLETRA.get(idioma_atual_raw, idioma_atual_raw)
    idioma_novo_gt = MAPA_GOOGLETRA.get(idioma_novo_raw, idioma_novo_raw)

    traducao = capturar_traduzir(screenshot_pil, imagem_original, idioma_atual_raw, idioma_novo_gt, idioma_atual_gt)
    
    # Retorna o resultado como JSON
    return jsonify(traducao)



# Codigo para print e tradução
def capturar_traduzir(imagem_pil, imagem_ori, idioma_atual_tesseract, idioma_novo_googletrans, idioma_atual_googletrans):
    try:
        # Executar OCR com bounding boxes
        info = pytesseract.image_to_data(imagem_pil, lang=idioma_atual_tesseract, output_type=pytesseract.Output.DICT)

        desenho = ImageDraw.Draw(imagem_ori)#deve se tornar a imagem original
        fonte = ImageFont.truetype("arial.ttf", 20)
        tradutor = Translator()

        parte_traduzido = []

        parte_traduzido = []
        blocos = [i for i, lvl in enumerate(info['level']) if lvl == 2]
        texto = []

        for i in blocos:
            num_bloco = info['block_num'][i]
            texto_bloco = []
            for j in range(len(info['level'])):
                if info['level'][j] == 5 and info['block_num'][j] == num_bloco:
                    if int(info['conf'][j]) != -1:
                        palavra = info['text'][j].strip()
                        if palavra:
                            texto_bloco.append(palavra)

            texto = " ".join(texto_bloco)
            if texto:
                x, y, w, h = info['left'][i], info['top'][i], info['width'][i], info['height'][i]
    # Traduzir texto
                try:
                    texto_traduzido = tradutor.translate(texto, src=idioma_atual_googletrans , dest=idioma_novo_googletrans).text
                    parte_traduzido.append(texto_traduzido)
                except Exception as e:
                    texto_traduzido = texto + " (erro trad.)"
                    parte_traduzido.append(texto_traduzido)

                largura = w 

                linha = []
                separado = texto_traduzido.split()
                linha_atual = ""

                for s in separado:
                    teste = linha_atual + (" " if linha_atual else "") + s
                    caixa = fonte.getbbox(teste)
                    linha_largura = caixa[2] - caixa[0]
                    if linha_largura <= largura:
                        linha_atual = teste
                    else:
                        linha.append(linha_atual)
                        linha_atual = s

                if linha_atual:
                    linha.append(linha_atual)

                # Apaga texto original
                desenho.rectangle([(x, y), (x + w, y + h)], fill="white")

                # Desenha texto traduzido
                caixa = fonte.getbbox('A')
                linha_altura = caixa[3] - caixa[1]
                for l, line in enumerate(linha):
                    desenho.text((x, y + l * linha_altura), line, fill="black", font=fonte)

        # Converter imagem final para base64
        buffer = io.BytesIO()
        imagem_ori.save(buffer, format="PNG")
        imagem_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "imagem_modificada": f"data:image/png;base64,{imagem_base64}",
            "texto_traduzido": "\n".join(parte_traduzido)
        }

    except Exception as e:
        return {"error": f"Erro ao processar imagem: {e}", "texto_traduzido": "Erro"}