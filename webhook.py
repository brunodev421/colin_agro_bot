from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
import os

from llm_client import gerar_resposta
from rag import gerar_resposta_com_rag

router = APIRouter()

USE_RAG_WHATSAPP = os.getenv("RAG_ENABLED", "false").lower() == "true"


def extrair_texto_whatsapp(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extrai o texto da mensagem do payload do WhatsApp Cloud (formato genérico).
    """
    try:
        return payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
    except (KeyError, IndexError, TypeError):
        return None


def extrair_remetente(payload: Dict[str, Any]) -> Optional[str]:
    """
    Retorna o número de origem (campo 'from') para usar na resposta.
    """
    try:
        return payload["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
    except (KeyError, IndexError, TypeError):
        return None


@router.post("/webhook")
async def whatsapp_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Webhook que recebe mensagens do WhatsApp (Meta Sandbox ou similar).
    - Extrai o texto do usuário.
    - Chama o LLM (com ou sem RAG).
    - Retorna um JSON simulando o payload de envio de volta ao WhatsApp.
    """
    texto = extrair_texto_whatsapp(payload)
    remetente = extrair_remetente(payload)

    if not texto or not remetente:
        raise HTTPException(
            status_code=400,
            detail="Payload inválido: não foi possível extrair texto ou remetente.",
        )

    if USE_RAG_WHATSAPP:
        resultado = gerar_resposta_com_rag(texto)
    else:
        resultado = gerar_resposta(texto)

    resposta_texto = resultado.get("resposta_modelo", "")

    resposta_whatsapp = {
        "messaging_product": "whatsapp",
        "to": remetente,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": resposta_texto,
        },
    }

    return {
        "saida_whatsapp": resposta_whatsapp,
        "meta_modelo": {
            "modelo": resultado.get("modelo"),
            "tokens_usados": resultado.get("tokens_usados"),
            "origem_contexto": resultado.get("origem_contexto"),
        },
    }
