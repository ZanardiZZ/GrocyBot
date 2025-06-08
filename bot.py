import logging
import os
import re
import asyncio
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
DESCONTOS_MANUAIS = 2

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
        resultado = await asyncio.to_thread(extrair_itens_nfe_via_selenium, codigo)
        print(f"[DEBUG] Resultado do parser: {type(resultado)} → {resultado}")

        if not isinstance(resultado, (list, tuple)) or len(resultado) != 2:
            raise Exception(f"Retorno inesperado do parser de nota: {resultado}")


        itens, data = resultado
        if not itens:
            raise Exception("Nenhum item encontrado.")
        if not data:
            raise Exception("Data da compra não encontrada na nota.")

        notas_pendentes[chat_id].update({
            "itens": itens,
            "data": data,
            "loja": loja
        })

        resumo = summarize_items(itens)
        linhas = resumo.splitlines()
        linhas_numeradas = []
        contador = 1
        for linha in linhas:
            if linha.startswith("- "):
               linhas_numeradas.append(f"{contador}. {linha[2:]}")
               contador += 1
            else:
                linhas_numeradas.append(linha)

        resumo_numerado = "\n".join(linhas_numeradas)
        texto = resumo_numerado + "\n\nAlgum item teve desconto?\nSe sim, envie assim: número:valor (ex: 2:2.00,3:1.00)\nSe nenhum teve desconto, envie 0."

        await update.message.reply_text(texto[:4096])
        return DESCONTOS_MANUAIS

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao processar nota:\n{str(e)}")
        notas_pendentes.pop(chat_id, None)
        return ConversationHandler.END

async def aplicar_descontos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    entrada = update.message.text.strip()

    if chat_id not in notas_pendentes or "itens" not in notas_pendentes[chat_id]:
        await update.message.reply_text("❌ Nenhuma nota válida encontrada. Por favor, envie novamente.")
        return ConversationHandler.END

    dados = notas_pendentes[chat_id]

    if entrada != "0":
        descontos = entrada.split(",")
        try:
            for d in descontos:
                partes = d.split(":")
                if len(partes) != 2:
                    raise ValueError(f"Formato inválido em '{d}', use número:valor")
                idx = int(partes[0].strip()) - 1
                val = float(partes[1].strip().replace(",", "."))
                if idx < 0 or idx >= len(dados["itens"]):
                    raise IndexError(f"Número do item inválido: {idx + 1}")
                item = dados["itens"][idx]
                item["valor_total"] = max(0, item["valor_total"] - val)
                item["valor_unitario"] = round(item["valor_total"] / item["quantidade"], 2) if item["quantidade"] > 0 else 0.0
        except Exception as e:
            await update.message.reply_text(f"⚠️ Erro na entrada: {e}\nPor favor, envie novamente no formato correto: número:valor, separados por vírgula. Ex: 1:1.00,2:0.50")
            return DESCONTOS_MANUAIS

    erros = send_items_to_grocy(dados["itens"], dados["loja"], dados["data"])
    resumo = summarize_items(dados["itens"])
    resposta = resumo
    if erros:
        resposta += "\n⚠️ Ocorreram erros:\n" + "\n".join(erros)
    await update.message.reply_text(resposta[:4096])

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
            DESCONTOS_MANUAIS: [MessageHandler(filters.TEXT & ~filters.COMMAND, aplicar_descontos)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_polling()
