
# 🛒 Grocy Bot Telegram

Bot do Telegram para leitura de notas fiscais (via QR Code, imagem, PDF ou XML) e envio automático dos itens para o Grocy.

## 🚀 Funcionalidades
- 📸 Lê notas fiscais via QR Code
- 🧾 Extrai dados de PDFs de notas
- 📂 Lê diretamente arquivos XML de NF-e
- 🔍 Faz OCR de imagens
- 🤖 Usa IA (OpenAI) para:
  - Padronizar nomes de produtos
  - Estimar validade dos produtos
- 🔗 Envia os itens automaticamente para o Grocy via API
- 🧠 Cria cache local para nomes de produtos (alias) e validades, reduzindo custo
- 🧠 Se detecta descontos na nota via QRCode, consulta automaticamente a nota completa na SEFAZ-RS resolvendo o CAPTCHA com Anti-Captcha

## 🔧 Instalação
1. Clone este repositório
2. Instale as dependências:
```
pip install -r requirements.txt
```
3. Crie um arquivo `.env` com base no `.env.example`:
```
cp .env.example .env
```
4. Execute:
```
python bot.py
```

## 📜 .env (Exemplo)
```
TELEGRAM_TOKEN=seu_token_aqui
GROCY_URL=http://ip_ou_dominio_do_seu_grocy
GROCY_API_KEY=sua_api_key_do_grocy
OPENAI_API_KEY=sua_api_key_da_openai
ANTICAPTCHA_API_KEY=sua_api_key_do_anticaptcha
DEFAULT_LOCATION_ID=1
```

## 🗒️ Observações
- O cache de alias é salvo em `alias_cache.json`.
- Arquivos de debug HTML ficam no diretório raiz.
- O arquivo `.env` não vai para o git, use o `.env.example` como base.

## 📜 Licença
MIT
