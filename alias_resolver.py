
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CACHE_FILE = "alias_cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        alias_cache = json.load(f)
else:
    alias_cache = {}

def salvar_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(alias_cache, f, ensure_ascii=False, indent=2)

def padronizar_nome(nome_bruto):
    nome_bruto = nome_bruto.strip().upper()

    if nome_bruto in alias_cache:
        return alias_cache[nome_bruto]

    try:
        prompt = f"""
Padronize o nome do produto da seguinte forma:
- Remova quantidades, pesos, códigos e informações desnecessárias.
- Mantenha um nome claro, completo e conciso.

Agora padronize este:
Entrada: {nome_bruto}
Saída:
"""
        resposta = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        nome_final = resposta.choices[0].message.content.strip().upper()

        alias_cache[nome_bruto] = nome_final
        salvar_cache()

        print(f"[ALIAS] {nome_bruto} ➝ {nome_final}")

        return nome_final

    except Exception as e:
        print(f"[ERRO ALIAS] {e}")
        return nome_bruto
