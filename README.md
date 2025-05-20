# 🛒 Grocy Telegram Bot

Um bot de Telegram para automatizar o lançamento de notas fiscais no [Grocy](https://grocy.info), usando QR Code, OCR, OpenAI e scraping da NFC-e.

---

## ✨ Funcionalidades

- 📸 Envie uma **foto ou PDF** da nota fiscal via Telegram
- 🤖 O bot:
  - Extrai o link da nota via QR Code
  - Acessa o conteúdo completo da NFC-e com Selenium
  - Lê todos os itens, valores, unidade e data
  - Estima validade com IA (OpenAI)
  - Inferência automática do local de armazenamento (Freezer, Geladeira, etc)
  - Cria produtos e locais de compra no Grocy automaticamente
  - Registra os itens com preço, validade e local corretamente
- 📦 Retorna o resumo direto no Telegram com valor total

---

## 🧰 Requisitos

- Python 3.10+
- Conta e API key da OpenAI, somente para a estimativa de validade dos produtos
- Instância do Grocy com API habilitada
- Bot do Telegram com token

---

## ⚙️ Variáveis `.env`

Crie um arquivo `.env` com o seguinte conteúdo:

```env
GROCY_URL=https://seu-endereco-do-grocy
GROCY_API_KEY=sua_chave_da_api
TELEGRAM_TOKEN=seu_token_do_bot
OPENAI_API_KEY=sua_api_key_openai
```

---

## ▶️ Como usar

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Execute o bot:

```bash
python bot.py
```

3. No Telegram, envie uma **foto da nota com QR Code** visível.

---

## 📁 Estrutura

- `bot.py` — Bot Telegram principal
- `grocy_api.py` — Comunicação com a API do Grocy
- `ocr.py`, `pdf_parser.py`, `qr_reader.py` — Leitura de imagens, PDF e QR code
- `openai_parser.py`, `validade_util_ia.py` — Uso de OpenAI para interpretação e validade
- `selenium_parser.py` — Coleta direta da NFC-e da SEFAZ-RS
- `requirements.txt` — Dependências

---

## 📜 Licença

MIT — sinta-se livre para usar, modificar e compartilhar!

---

## 🙏 Créditos

Desenvolvido por um entusiasta de automações pessoais, com apoio da OpenAI.
