from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from urllib.parse import quote

def listar_iframes(codigo_completo):
    base = "https://dfe-portal.svrs.rs.gov.br/Dfe/QrCodeNFce?p="
    url = base + quote(codigo_completo, safe="")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(5)  # tempo para carregar se houver redirect ou JS

    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    print(f"🔍 Encontrados {len(iframes)} iframe(s):")
    for idx, iframe in enumerate(iframes):
        src = iframe.get_attribute("src")
        print(f" - iframe[{idx}]: src = {src}")

    driver.quit()

if __name__ == "__main__":
    # Substitua abaixo pelo código completo que vem do QR Code (parâmetro "p=" inteiro)
    listar_iframes("43250592016757008842651220000235441879174439|2|1|1|A342F47C41D8518E34BF7327E32C517AFCCEF582")
