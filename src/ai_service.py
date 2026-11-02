import json
import requests
from typing import Dict, Any
from .config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL

SYSTEM_PROMPT = """Você é um assistente de automação corporativa.
Analise a mensagem ou evento recebido e retorne estritamente um JSON no seguinte formato:
{
  "categoria": "SUPORTE_CLIENTE | INCIDENTE_URGENTE | QUALIFICACAO_LEAD | AUTOMACAO_TAREFA | GERAL",
  "urgencia": "BAIXA | MEDIA | ALTA | CRITICA",
  "resumo": "Resumo de uma frase sobre o evento",
  "resposta_sugerida": "Resposta contextual pronta para o cliente ou equipe",
  "acao_recomendada": "notificar_telegram | registrar_chamado | responder_email | arquivar"
}
Não inclua explicações ou markdown fora do JSON."""

def _fallback_analise(texto: str) -> Dict[str, Any]:
    # Fallback local simples caso não haja chave de API configurada
    texto_lower = texto.lower()
    
    if any(p in texto_lower for p in ["erro", "fora do ar", "urgente", "bug", "queda", "parou", "crash"]):
        categoria = "INCIDENTE_URGENTE"
        urgencia = "CRITICA"
        acao = "notificar_telegram"
        resposta = "Identificamos um incidente operacional crítico. A equipe técnica já foi notificada para averiguação imediata."
    elif any(p in texto_lower for p in ["orçamento", "preço", "comprar", "plano", "contratar", "demonstração"]):
        categoria = "QUALIFICACAO_LEAD"
        urgencia = "MEDIA"
        acao = "responder_email"
        resposta = "Olá! Agradecemos o interesse em nossas soluções. Nosso time comercial entrará em contato em breve."
    elif any(p in texto_lower for p in ["dúvida", "ajuda", "como faço", "login", "senha", "acesso"]):
        categoria = "SUPORTE_CLIENTE"
        urgencia = "BAIXA"
        acao = "responder_email"
        resposta = "Olá! Recebemos sua solicitação de suporte. Para redefinir seu acesso ou tirar dúvidas, confira nossa base de conhecimento ou aguarde nosso retorno."
    else:
        categoria = "GERAL"
        urgencia = "BAIXA"
        acao = "arquivar"
        resposta = "Mensagem recebida e registrada no fluxo de automação."

    return {
        "categoria": categoria,
        "urgencia": urgencia,
        "resumo": texto[:120] + ("..." if len(texto) > 120 else ""),
        "resposta_sugerida": resposta,
        "acao_recomendada": acao
    }

def processar_evento_com_ia(texto: str) -> Dict[str, Any]:
    # Se não tiver chave de API, usa o fallback inteligente sem quebrar o sistema
    if not OPENAI_API_KEY:
        return _fallback_analise(texto)

    try:
        base_url = OPENAI_BASE_URL or "https://api.openai.com/v1"
        endpoint = f"{base_url.rstrip('/')}/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texto}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        res = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        if res.status_code == 200:
            data = res.json()
            conteudo = data["choices"][0]["message"]["content"]
            return json.loads(conteudo)
        else:
            print(f"Aviso: Falha na API OpenAI ({res.status_code}). Usando fallback.")
            return _fallback_analise(texto)

    except Exception as e:
        print(f"Erro ao consultar modelo de IA: {e}")
        return _fallback_analise(texto)
