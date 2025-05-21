
# 🛒 Grocy Bot Telegram

Bot do Telegram para leitura de notas fiscais (via QR Code, imagem ou PDF) e envio automático dos itens para o Grocy.

## 🚀 Funcionalidades
- 📸 Lê notas fiscais via QR Code
- 🧾 Extrai dados de PDFs de notas
- 🔍 Faz OCR de imagens
- 🤖 Usa IA (OpenAI) para:
  - Padronizar nomes de produtos
  - Estimar validade dos produtos
- 🔗 Envia os itens automaticamente para o Grocy via API
- 🗂️ Cria cache local para nomes de produtos (alias) e validades, reduzindo custo e aumentando velocidade

## 🔧 Instalação
1. Clone este repositório
2. Instale as dependências:
```
pip install -r requirements.txt
```
3. Crie um arquivo `.env` com:
```
TELEGRAM_TOKEN=seu_token
GROCY_URL=http://ip_do_seu_grocy
GROCY_API_KEY=sua_api_key
OPENAI_API_KEY=sua_api_key_openai
DEFAULT_LOCATION_ID=1
```
4. Execute:
```
python bot.py
```

## 🗒️ Observações
- O cache de alias é salvo em `alias_cache.json`.
- Arquivos de debug HTML ficam no diretório raiz.

## 📜 Licença
MIT
