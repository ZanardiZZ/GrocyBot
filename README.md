# 🤖 GrocyBot — Integração automática de notas fiscais com Grocy via Telegram

Este bot permite enviar **notas fiscais por QR Code ou PDF** via Telegram. Ele extrai os produtos da nota, permite aplicar **descontos manualmente por item**, calcula validade estimada e **insere automaticamente no Grocy** via API.

---

## 🚀 Funcionalidades

✅ Envio da nota via **foto do QR Code**  
✅ Extração de dados via **Selenium da SEFAZ-RS**  
✅ Suporte a PDFs (com parser OpenAI ou regras)  
✅ Validação e correção dos dados via **Inteligência Artificial**  
✅ Estimativa automática de **validade dos produtos**  
✅ Escolha do **estabelecimento de compra**  
✅ Aplicação manual de **descontos por item**  
✅ Inserção direta no **estoque do Grocy** via API  
✅ Suporte a unidades, locais e fallback inteligente  
✅ Logs e mensagens informativas no Telegram

---

## 🧰 Requisitos

- Python 3.10+
- Docker (opcional para facilitar execução)
- Conta no Grocy com API ativada
- Bot Telegram com token
- Chave do Anti-Captcha (opcional, para resolver reCAPTCHA na SEFAZ)

---

## 🔐 Variáveis de ambiente (`.env`)

```ini
TELEGRAM_TOKEN=seu_token_telegram
GROCY_URL=http://192.168.0.10/grocy
GROCY_API_KEY=suachavegrocy
OPENAI_API_KEY=sua_chave_openai
ANTICAPTCHA_KEY=sua_chave_anticaptcha
DEFAULT_LOCATION_ID=1
```

---

## 📦 Instalação via Docker

Crie um `docker-compose.yml` com:

```yaml
version: "3"

services:
  grocybot:
    build: .
    volumes:
      - .:/app
    environment:
      - TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
      - GROCY_URL=${GROCY_URL}
      - GROCY_API_KEY=${GROCY_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTICAPTCHA_KEY=${ANTICAPTCHA_KEY}
      - DEFAULT_LOCATION_ID=1
```

---

## 📸 Uso

1. Inicie o bot:
   ```bash
   python3 bot.py
   ```

2. No Telegram, envie uma foto da **nota fiscal com QR Code**.

3. O bot irá:
   - Extrair os itens
   - Perguntar o nome do mercado
   - Exibir os itens com valores
   - Perguntar se algum item teve desconto (por número)

4. Após confirmação, envia ao Grocy!

---

## 🧠 IA utilizada

- **OpenAI GPT-4o** para:
  - Corrigir OCR e parser
  - Estimar validade dos produtos
  - Padronizar nomes dos itens
