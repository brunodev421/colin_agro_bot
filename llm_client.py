import os
from typing import Optional, Dict, Any, Sequence, TYPE_CHECKING
from dotenv import load_dotenv

if TYPE_CHECKING:
    from openai.types.chat import (
        ChatCompletionMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
    )
else:
    ChatCompletionMessageParam = Any
    ChatCompletionSystemMessageParam = Any
    ChatCompletionUserMessageParam = Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv()

DEFAULT_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")


def get_system_prompt() -> str:
    base_path = os.path.dirname(__file__)
    prompt_path = os.path.join(base_path, "prompts", "colin_system_prompt.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Você é COLIN, assistente rural. (System prompt externo não encontrado.)"


def _build_messages(
    system_prompt: str,
    user_message: str,
    contexto: Optional[str],
) -> Sequence["ChatCompletionMessageParam"]:

    system_msg: "ChatCompletionSystemMessageParam" = {
        "role": "system",
        "content": system_prompt,
    }

    if contexto:
        content = (
            f"CONTEXTOS INTERNOS DA EMPRESA:\n{contexto}\n\n"
            f"MENSAGEM DO PRODUTOR:\n{user_message}"
        )
    else:
        content = user_message

    user_msg: "ChatCompletionUserMessageParam" = {
        "role": "user",
        "content": content,
    }

    messages: Sequence["ChatCompletionMessageParam"] = [system_msg, user_msg]
    return messages


def chamar_modelo(
    user_message: str,
    contexto: Optional[str] = None,
    modelo: Optional[str] = None,
) -> Dict[str, Any]:

    system_prompt = get_system_prompt()
    modelo_final = modelo or DEFAULT_MODEL_NAME

    if OpenAI is None or os.getenv("OPENAI_API_KEY") is None:
        return {
            "resposta_modelo": (
                "[MODO DEMO] "
                f"Sua mensagem foi: {user_message[:120]}"
            ),
            "tokens_usados": None,
            "modelo": f"{modelo_final}-fake",
        }

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = _build_messages(system_prompt, user_message, contexto)

    completion = client.chat.completions.create(
        model=modelo_final,
        messages=messages,
        temperature=0.2,
    )

    resposta_texto = completion.choices[0].message.content
    usage = getattr(completion, "usage", None)
    tokens = usage.total_tokens if usage else None

    return {
        "resposta_modelo": resposta_texto,
        "tokens_usados": tokens,
        "modelo": modelo_final,
    }


def gerar_resposta(
    mensagem: str,
    contexto: Optional[str] = None,
    origem_contexto: str = "sem_contexto",
) -> Dict[str, Any]:

    resultado = chamar_modelo(mensagem, contexto=contexto)

    return {
        "resposta_modelo": resultado["resposta_modelo"],
        "tokens_usados": resultado.get("tokens_usados"),
        "modelo": resultado.get("modelo"),
        "origem_contexto": origem_contexto,
    }
