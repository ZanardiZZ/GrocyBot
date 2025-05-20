import pdfplumber
import re
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def padronizar_nome(nome_bruto):
    try:
        prompt = f"Padronize o nome de produto da seguinte forma, removendo códigos, quantidades e mantendo o nome claro e conciso.\nEntrada: {nome_bruto}\nNome padronizado:"
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        return response.choices[0].message.content.strip()
    except:
        return nome_bruto

def extract_items_from_pdf(pdf_path, usar_openai_para_nome=True):
    items = []
    estabelecimento = None
    regex_item = re.compile(r"^\d+\s+(.*?)\s+([\d,.]+)\s+(UN|KG|L|LT|ML|G)\s+([\d,.]+)$")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split("\n")

            for i, line in enumerate(lines):
                # Loja
                if not estabelecimento and i + 1 < len(lines) and "CNPJ" in lines[i + 1]:
                    estabelecimento = line.strip()

                # Linha de item compacta
                match = regex_item.match(line.strip())
                if match:
                    nome_raw = match.group(1)
                    quantidade = float(match.group(2).replace(",", "."))
                    unidade = match.group(3).strip()
                    valor_total = float(match.group(4).replace(",", "."))
                    valor_unitario = round(valor_total / quantidade, 2) if quantidade > 0 else 0.0

                    nome_final = padronizar_nome(nome_raw) if usar_openai_para_nome else nome_raw

                    item = {
                        "nome": nome_final,
                        "quantidade": quantidade,
                        "unidade": unidade,
                        "valor_total": valor_total,
                        "valor_unitario": valor_unitario,
                        "codigo_barras": None  # ignorado nesse formato simples
                    }

                    items.append(item)

    return items, estabelecimento
