from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
from datetime import datetime
from urllib.parse import quote

def extrair_itens_nfe_via_selenium(codigo_completo):
    base = "https://dfe-portal.svrs.rs.gov.br/Dfe/QrCodeNFce?p="
    url = base + quote(codigo_completo, safe="")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr[id^='Item']"))
        )
    except Exception as e:
        html_falha = driver.page_source
        with open("debug_nfe_falha.html", "w", encoding="utf-8") as f:
            f.write(html_falha)
        driver.quit()
        raise Exception("❌ Conteúdo da nota não apareceu a tempo.") from e

    html = driver.page_source
    driver.quit()

    with open("debug_nfe_final.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    html_text = soup.get_text(" ", strip=True)

    data_compra = None
    match = re.search(r"Protocolo de Autorização:\s*\d+\s*(\d{2}/\d{2}/\d{4})", html_text)
    if match:
        try:
            data_br = match.group(1)
            data_dt = datetime.strptime(data_br, "%d/%m/%Y")
            data_compra = data_dt.strftime("%Y-%m-%d")
        except:
            data_compra = None

    itens = []
    linhas = soup.select("tr[id^=Item]")

    print(f"[DEBUG] {len(linhas)} itens encontrados na página final.")

    def parse_num(texto):
        matches = re.findall(r"[\d]+[\.,]?[\d]*", texto)
        if matches:
            val = matches[-1].replace(",", ".")
            try:
                return float(val)
            except:
                return 0.0
        return 0.0

    for linha in linhas:
        try:
            nome_tag = linha.select_one("span.txtTit")
            qtd_tag = linha.select_one("span.Rqtd")
            und_tag = linha.select_one("span.RUN")
            unit_tag = linha.select_one("span.RvlUnit")
            total_tag = linha.select_one("td.txtTit span.valor")

            nome = nome_tag.get_text(strip=True)
            qtd = parse_num(qtd_tag.text)
            unidade = re.search(r"UN: ?([A-Z]+)", und_tag.text)
            unidade = unidade.group(1).upper() if unidade else "UN"
            val_unit = parse_num(unit_tag.text)
            val_total = parse_num(total_tag.text)

            print(f"[DEBUG] {nome} - QTD extraída: {qtd}, UN: {unidade}, Total: R${val_total:.2f}")

            itens.append({
                "nome": nome,
                "quantidade": qtd,
                "unidade": unidade,
                "valor_unitario": val_unit,
                "valor_total": val_total,
                "codigo_barras": None
            })
        except Exception as e:
            print(f"[ERRO ITEM] {e}")
            continue

    return itens, data_compra


def extrair_valores_totais(soup):
    texto = soup.get_text(" ", strip=True)

    def buscar_valor(label):
        padrao = rf"{label} R\\$[\s]*([\d\.,]+)"
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(".", "").replace(",", "."))
        return 0.0

    valor_total = buscar_valor("Valor total")
    descontos = buscar_valor("Descontos")
    valor_a_pagar = buscar_valor("Valor a pagar")

    print(f"[DEBUG] Valor total: {valor_total}, Descontos: {descontos}, Valor a pagar: {valor_a_pagar}")
    return valor_total, descontos, valor_a_pagar


def verificar_necessidade_consulta_completa(itens, valor_total, descontos, valor_a_pagar):
    soma_itens = sum(item['valor_total'] for item in itens)
    print(f"[DEBUG] Soma dos itens: {soma_itens:.2f}, Valor Total: {valor_total:.2f}, Descontos: {descontos:.2f}, Valor a Pagar: {valor_a_pagar:.2f}")

    if descontos > 0:
        print("⚠️ Desconto detectado na nota. Acessar nota completa na SEFAZ.")
        return True

    if abs(soma_itens - valor_total) > 0.05:
        print("⚠️ Divergência nos itens. Acessar nota completa na SEFAZ.")
        return True

    if abs(soma_itens - valor_a_pagar) > 0.05:
        print("⚠️ Divergência entre itens e valor a pagar. Acessar nota completa na SEFAZ.")
        return True

    print("✅ Valores conferem. Nota do QRCode suficiente.")
    return False
