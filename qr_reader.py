from pyzbar.pyzbar import decode
from PIL import Image

def extrair_link_qrcode(imagem_path):
    imagem = Image.open(imagem_path)
    resultados = decode(imagem)
    for resultado in resultados:
        if resultado.type == 'QRCODE':
            return resultado.data.decode('utf-8')
    return None
