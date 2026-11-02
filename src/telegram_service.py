import requests
from typing import Dict, Any
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

EMOJIS = {
    "INCIDENTE_URGENTE": "🚨",
    "QUALIFICACAO_LEAD": "💼",
    "SUPORTE_CLIENTE": "🎧",
    "AUTOMACAO_TAREFA": "⚙️",
    "GERAL": "📌"
}

def enviar_alerta_telegram(origem: str, analise: Dict[str, Any]) -> bool:
    # Se o token não estiver configurado, loga no console e segue em frente sem quebrar
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[Telegram Simulado] Alerta para {origem}: {analise.get('resumo')}")
        return False

    categoria = analise.get("categoria", "GERAL")
    urgencia = analise.get("urgencia", "BAIXA")
    resumo = analise.get("resumo", "Sem resumo")
    resposta = analise.get("resposta_sugerida", "N/A")
    acao = analise.get("acao_recomendada", "arquivar")

    emoji = EMOJIS.get(categoria, "📌")

    texto = (
        f"{emoji} *Novo Evento Automatizado via IA*\n\n"
        f"📍 *Origem:* `{origem}`\n"
        f"🏷️ *Categoria:* `{categoria}`\n"
        f"⚡ *Urgência:* `{urgencia}`\n"
        f"🎯 *Ação:* `{acao}`\n\n"
        f"📝 *Resumo:*\n{resumo}\n\n"
        f"💬 *Resposta Sugerida:*\n_{resposta}_"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem no Telegram: {e}")
        return False
