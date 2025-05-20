import logging
import os
import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CommandHandler,
)
from dotenv import load_dotenv
from qr_reader import extrair_link_qrcode
from selenium_parser import extrair_itens_nfe_via_selenium
from grocy_api import send_items_to_grocy, summarize_items

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

ESPERANDO_ESTABELECIMENTO = 1

LOCAIS_CONHECIDOS = [
    ["Carrefour", "Extra", "Amazon"],
    ["Mercado Livre", "Nacional SB", "Guanabara"],
    ["Stok Center", "Nosso mercado SB", "Outro"]
]

notas_pendentes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envie uma foto da nota fiscal com o QR Code visível.")
    return ConversationHandler.END

async def handle_foto_qrcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    caminho_imagem = f"nota_qr_{update.message.chat_id}.jpg"
    await file.download_to_drive(caminho_imagem)

    await update.message.reply_text("🔎 Lendo QR Code...")

    url = extrair_link_qrcode(caminho_imagem)
    if not url or "p=" not in url:
        await update.message.reply_text("❌ QR Code inválido ou não detectado.")
        return ConversationHandler.END

    chave_match = re.search(r"p=(.*)", url)
    if not chave_match:
        await update.message.reply_text("❌ Não foi possível extrair o código da nota.")
        return ConversationHandler.END

    codigo_completo = chave_match.group(1)
    notas_pendentes[update.message.chat_id] = {"codigo": codigo_completo}

    reply_markup = ReplyKeyboardMarkup(LOCAIS_CONHECIDOS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(f"✅ Código capturado com sucesso!\nQual o nome do estabelecimento?", reply_markup=reply_markup)
    return ESPERANDO_ESTABELECIMENTO

async def receber_estabelecimento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loja = update.message.text.strip()
    chat_id = update.message.chat_id
    if chat_id not in notas_pendentes:
        await update.message.reply_text("❌ Nenhuma nota aguardando. Envie uma nova.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    codigo = notas_pendentes[chat_id]["codigo"]
    await update.message.reply_text("📦 Processando nota fiscal com navegador automático...")

    try:
        itens, data = extrair_itens_nfe_via_selenium(codigo)
        if not itens:
            raise Exception("Nenhum item encontrado.")
        if not data:
            raise Exception("Data da compra não encontrada na nota.")
        erros = send_items_to_grocy(itens, loja, data)
        resumo = summarize_items(itens)
        resposta = resumo
        if erros:
            resposta += "\n⚠️ Ocorreram erros:\n" + "\n".join(erros)
        await update.message.reply_text(resposta[:4096])
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao processar nota:\n{str(e)}")

    notas_pendentes.pop(chat_id, None)
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operação cancelada.", reply_markup=ReplyKeyboardRemove())
    notas_pendentes.pop(update.message.chat_id, None)
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, handle_foto_qrcode)],
        states={
            ESPERANDO_ESTABELECIMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_estabelecimento)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_polling()
