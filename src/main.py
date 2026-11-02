from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uvicorn

from .config import PORT, HOST
from .database import init_db, salvar_evento, listar_eventos
from .ai_service import processar_evento_com_ia
from .telegram_service import enviar_alerta_telegram

app = FastAPI(
    title="Hub de Automações com IA",
    description="Pipeline de ingestão, roteamento semântico com LLM e despacho para Telegram e serviços externos.",
    version="1.0.0"
)

# Inicializa o banco de dados SQLite na subida da API
@app.on_event("startup")
def startup_event():
    init_db()

class WebhookPayload(BaseModel):
    origem: str = Field(default="sistema_externo", description="Identificador da origem do evento (ex: n8n, typeform, suporte)")
    mensagem: str = Field(..., description="Texto ou descrição do evento para processamento com IA")
    metadados: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados extras opcionais")

class EventoResponse(BaseModel):
    id: int
    origem: str
    categoria: str
    urgencia: str
    resumo: str
    resposta_sugerida: str
    acao_recomendada: str
    notificado_telegram: bool

@app.get("/")
def raiz():
    return {
        "status": "online",
        "servico": "Hub de Automações com IA",
        "docs": "/docs"
    }

@app.get("/health")
def healthcheck():
    return {"status": "healthy"}

@app.post("/webhook", response_model=EventoResponse)
def receber_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    try:
        # 1. Processa a mensagem usando LLM (ou fallback inteligente)
        analise = processar_evento_com_ia(payload.mensagem)

        # 2. Decide se dispara notificação no Telegram
        categoria = analise.get("categoria", "GERAL")
        urgencia = analise.get("urgencia", "BAIXA")
        deve_notificar = urgencia in ["ALTA", "CRITICA"] or analise.get("acao_recomendada") == "notificar_telegram"

        notificado = False
        if deve_notificar:
            # Envia em background para responder rápido ao webhook
            background_tasks.add_task(enviar_alerta_telegram, payload.origem, analise)
            notificado = True

        # 3. Salva no banco de dados local
        evento_id = salvar_evento(
            origem=payload.origem,
            categoria=categoria,
            urgencia=urgencia,
            conteudo=payload.mensagem,
            resposta_ia=analise.get("resposta_sugerida"),
            notificado=notificado
        )

        return EventoResponse(
            id=evento_id,
            origem=payload.origem,
            categoria=categoria,
            urgencia=urgencia,
            resumo=analise.get("resumo", ""),
            resposta_sugerida=analise.get("resposta_sugerida", ""),
            acao_recomendada=analise.get("acao_recomendada", ""),
            notificado_telegram=notificado
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento: {str(e)}")

@app.get("/eventos")
def historico_eventos(limite: int = 15):
    return {"total": len(listar_eventos(limite)), "eventos": listar_eventos(limite)}

@app.post("/simular")
def simular_teste(tipo: str = "incidente"):
    exemplos = {
        "incidente": "Alerta do Datadog: Servidor de banco de dados PostgreSQL atingiu 98% de uso de CPU e está com lentidão crítica.",
        "lead": "Olá, me chamo Marina da TechCorp e temos 150 colaboradores. Gostaria de solicitar um orçamento para automação de atendimento com IA.",
        "suporte": "Não estou conseguindo redefinir minha senha pelo aplicativo, a página dá erro 403.",
        "tarefa": "Lembrete: agendar reunião semanal de alinhamento com a equipe de engenharia para sexta-feira às 14h."
    }

    mensagem = exemplos.get(tipo, exemplos["incidente"])
    analise = processar_evento_com_ia(mensagem)
    return {
        "tipo_simulado": tipo,
        "mensagem_entrada": mensagem,
        "analise_ia": analise
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
