import os
import openai
from dotenv import load_dotenv
import json

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def montar_prompt(text):
    return f"""
Você receberá o texto de uma nota fiscal extraído via OCR.  
Cada linha representa um item e pode conter:  
- Nome do produto  
- Quantidade (ex: 1 UN, 0,875 KG, 2,5 LT)  
- Valor unitário (R$ por UN ou KG)  
- Valor total (quantidade × valor unitário)  
- Código de barras (às vezes presente)  

Sua tarefa é:
1. Identificar corretamente a **unidade de medida** (UN, KG, LT, etc).
2. Corrigir possíveis erros de OCR.
3. Verificar se o valor total está coerente com o valor unitário × quantidade.
4. Retornar uma lista em formato JSON com os seguintes campos:
  - nome
  - quantidade (float)
  - unidade (UN, KG, LT, etc)
  - valor_unitario (float)
  - valor_total (float)
  - codigo_barras (string ou null)

Exemplo de linha:
BANANA PRATA 0,875KG R$3,99 R$3,49

Texto da nota:
{text}

Retorne apenas a lista JSON. Não escreva explicações.
"""

def validar_items(items):
    for item in items:
        try:
            qtd = float(item["quantidade"])
            val_unit = float(item["valor_unitario"])
            val_total = float(item["valor_total"])
            if abs((qtd * val_unit) - val_total) > 0.10:
                return False
        except:
            return False
    return True

def requisitar_openai(text, modelo):
    prompt = montar_prompt(text)
    resposta = client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta.choices[0].message.content.strip()

def parse_items_from_text(text):
    modelos = ["gpt-3.5-turbo", "gpt-4o"]

    for modelo in modelos:
        print(f"🧠 Usando modelo {modelo}...")
        try:
            resposta = requisitar_openai(text, modelo)
            items = json.loads(resposta)
            if validar_items(items):
                return items
            else:
                print(f"❌ Erro de validação: totais incorretos com {modelo}")
        except Exception as e:
            print(f"⚠️ Erro com {modelo}: {e}")
            continue

    print("💀 Nenhum modelo retornou dados válidos.")
    return []
