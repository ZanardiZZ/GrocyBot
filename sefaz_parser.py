from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import quote
import time
import re
from datetime import datetime


def acessar_nota_completa(chave_acesso):
    url = "https://www.sefaz.rs.gov.br/dfe/Consultas/ConsultaPublicaDfe"

    # Configuração para ambiente headless/server
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(url)
    driver.save_screenshot("screenshot_abertura.png")

    try:
        # Preencher chave de acesso
        input_chave = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ChaveAcessoDfe"))
        )
        input_chave.send_keys(chave_acesso)
        print(f"[DEBUG] Chave preenchida: {chave_acesso}")
        driver.save_screenshot("screenshot_chave_preenchida.png")

        # === Resolver reCAPTCHA (clicar na checkbox) ===
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
            )
        )

        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "recaptcha-checkbox-border"))
        )
        checkbox.click()
        print("[DEBUG] Checkbox do reCAPTCHA clicada")
        driver.save_screenshot("screenshot_checkbox_clicada.png")

        driver.switch_to.default_content()

        # Clicar no botão Consultar
        driver.execute_script("document.getElementById('btnConsultar').click()")

        time.sleep(5)  # Esperar carregar
        driver.save_screenshot("screenshot_depois_submit.png")

        html = driver.page_source
        with open("nota_sefaz_completa.html", "w", encoding="utf-8") as f:
            f.write(html)

        driver.quit()
        return html

    except Exception as e:
        driver.save_screenshot("screenshot_erro.png")
        driver.quit()
        print(f"❌ Erro geral: {e}")
        raise e


def extrair_itens_nfe_sefaz(chave_acesso):
    html = acessar_nota_completa(chave_acesso)
    if not html:
        return [], None

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
    print(f"[DEBUG] {len(linhas)} itens encontrados.")

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

            print(f"[DEBUG] {nome} - QTD: {qtd}, UN: {unidade}, Total: R${val_total:.2f}")

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
