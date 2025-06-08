import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Cache de itens já pesquisados com validade
cache_validades = {}

def estimar_validade(produto_nome):
    if produto_nome in cache_validades:
        return cache_validades[produto_nome]

    try:
        prompt = (
            f"Qual a validade média em dias para armazenar o item '{produto_nome}' em geladeira ou despensa, considerando padrões comuns de conservação? "
            "Responda apenas com o número de dias (ex: 30)."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        texto = response.choices[0].message.content.strip()
        dias = int("".join(c for c in texto if c.isdigit()))
        cache_validades[produto_nome] = dias
        return dias

    except Exception as e:
        print(f"Erro na consulta de validade para '{produto_nome}': \n{e}")
        return 30  # valor padrão de fallback

