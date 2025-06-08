import requests
from validade_util_ia import estimar_validade
from config import GROCY_URL, GROCY_API_KEY, DEFAULT_LOCATION_ID

API_KEY = GROCY_API_KEY

UNIDADES = {
    "KG": 5,
    "UN": 13,
    "G": 4,
    "L": 9,
    "ML": 10,
    "PCT": 3
}

LOCAIS = {
    "Amazon": 4,
    "Baklizi SB": 9,
    "Carrefour": 1,
    "Extra": 2,
    "Guanabara": 3,
    "Mercado Livre": 5,
    "Nacional SB": 8,
    "Nosso mercado SB": 10,
    "Shopee": 6,
    "Stok Center": 7
}

def get_headers():
    return {
        "GROCY-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

def get_location_id(nome_loja):
    for loja, lid in LOCAIS.items():
        if loja.lower() in nome_loja.lower():
            return lid
    return None

def buscar_produto_por_nome(nome):
    r = requests.get(f"{GROCY_URL}/api/objects/products", headers=get_headers())
    if r.status_code == 200:
        produtos = r.json()
        for p in produtos:
            if p["name"].strip().lower() == nome.strip().lower():
                return p["id"]
    return None

def send_items_to_grocy(itens, loja_nome, data_compra):
    from datetime import datetime, timedelta

    location_id = get_location_id(loja_nome)
    erros = []

    for item in itens:
        nome = item["nome"]
        unidade_nome = item["unidade"].upper()
        unidade_id = UNIDADES.get(unidade_nome, 13)
        quantidade = item["quantidade"]
        total = item["valor_total"]
        validade_dias = estimar_validade(nome)

        try:
            dt = datetime.strptime(data_compra, "%Y-%m-%d")
        except:
            dt = datetime.today()

        validade = (dt + timedelta(days=validade_dias)).strftime("%Y-%m-%d")
        compra_formatada = dt.strftime("%Y-%m-%d")

        produto_id = buscar_produto_por_nome(nome)

        if not produto_id:
            produto_data = {
                "name": nome,
                "qu_id_stock": unidade_id,
                "qu_id_purchase": unidade_id,
                "qu_id_consume": unidade_id,
                "location_id": location_id or DEFAULT_LOCATION_ID
            }

            r = requests.post(f"{GROCY_URL}/api/objects/products", json=produto_data, headers=get_headers())
            if r.status_code != 200:
                try:
                    erro_msg = r.json().get("error_message", "")
                except:
                    erro_msg = r.text
                erros.append(f"❌ Falha ao criar produto {nome}: {r.status_code} - {erro_msg}")
                continue
            produto_id = r.json()["created_object_id"]

        # Novo formato de endpoint para adicionar estoque
        payload = {
            "amount": quantidade,
            "best_before_date": validade,
            "purchased_date": compra_formatada,
            "location_id": location_id or DEFAULT_LOCATION_ID,
            "price": round(total, 2)
        }

        print(f"[DEBUG] Adicionando '{nome}' ao estoque: {payload}")
        r2 = requests.post(f"{GROCY_URL}/api/stock/products/{produto_id}/add", json=payload, headers=get_headers())

        if r2.status_code != 200:
            try:
                erro_msg = r2.json().get("error_message", "")
            except:
                erro_msg = r2.text
            print(f"[ERRO RESPOSTA] {r2.status_code} - {erro_msg}")
            erros.append(f"⚠️ Produto '{nome}' ignorado: {erro_msg}")
        else:
            print(f"[OK] Estoque adicionado com sucesso para '{nome}'.")

    return erros

def summarize_items(itens):
    total = sum(i["valor_total"] for i in itens)
    linhas = [f"- {i['nome']} ({i['quantidade']} {i['unidade']}, R${i['valor_total']:.2f})" for i in itens]
    return "🧾 Itens identificados:\n" + "\n".join(linhas) + f"\n\n💰 Total: R${total:.2f}"
