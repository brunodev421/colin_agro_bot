import os
import json
import pathlib
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from llm_client import gerar_resposta
from rag import gerar_resposta_com_rag
from webhook import router as whatsapp_router

load_dotenv()

app = FastAPI(
    title="Colin API – Atendimento Agro",
    version="0.1.0",
    description="API simples para o agente Colin (WhatsApp + RAG + LLM).",
)

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/app.log")
RAG_ENABLED = os.getenv("RAG_ENABLED", "false").lower() == "true"

pathlib.Path(LOG_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)


class MensagemRequest(BaseModel):
    mensagem: str


class MensagemResponse(BaseModel):
    resposta: Optional[str]
    modelo: Optional[str]
    tokens_usados: Optional[int] = None
    origem_contexto: str


def _truncate(text: Optional[str], max_len: int = 300) -> Optional[str]:
    if text is None:
        return None
    return text if len(text) <= max_len else text[:max_len] + "...[truncate]"


def log_interacao(
    mensagem_usuario: str,
    resposta_modelo: Optional[str],
    modelo: Optional[str],
    tokens_usados: Optional[int],
    origem_contexto: str,
    status: str,
    erro: Optional[str] = None,
) -> None:
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mensagem_usuario": _truncate(mensagem_usuario),
        "resposta_modelo": _truncate(resposta_modelo),
        "modelo": modelo,
        "tokens_usados": tokens_usados,
        "origem_contexto": origem_contexto,
        "status": status,
        "erro": erro,
    }

    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


@app.post("/mensagem", response_model=MensagemResponse)
async def post_mensagem(payload: MensagemRequest) -> MensagemResponse:
    mensagem = payload.mensagem

    try:
        if RAG_ENABLED:
            resultado = gerar_resposta_com_rag(mensagem)
        else:
            resultado = gerar_resposta(mensagem)

        resposta_modelo = resultado.get("resposta_modelo")
        modelo = resultado.get("modelo")
        tokens_usados = resultado.get("tokens_usados")
        origem_contexto = resultado.get("origem_contexto", "sem_contexto")

        log_interacao(
            mensagem_usuario=mensagem,
            resposta_modelo=resposta_modelo,
            modelo=modelo,
            tokens_usados=tokens_usados,
            origem_contexto=origem_contexto,
            status="sucesso",
        )

        return MensagemResponse(
            resposta=resposta_modelo,
            modelo=modelo,
            tokens_usados=tokens_usados,
            origem_contexto=origem_contexto,
        )

    except Exception as exc:
        log_interacao(
            mensagem_usuario=mensagem,
            resposta_modelo=None,
            modelo=None,
            tokens_usados=None,
            origem_contexto="desconhecido",
            status="erro",
            erro=str(exc),
        )
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a mensagem."
        ) from exc


app.include_router(whatsapp_router)


@app.get("/health")
async def healthcheck():
    return JSONResponse({"status": "ok", "rag_enabled": RAG_ENABLED})
