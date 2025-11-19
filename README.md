# Colin Agro Bot — Solução Conversacional com RAG + LLM

Este projeto implementa um agente conversacional para atendimento de produtores rurais via WhatsApp, integrando:

- FastAPI (API principal)
- Webhook compatível com WhatsApp Cloud API
- Mecanismo RAG simplificado baseado em arquivos `.txt`
- Cliente LLM com system prompt especializado
- Logs estruturados
- Arquitetura modular e clara para demonstração técnica

O objetivo é fornecer um protótipo funcional capaz de responder dúvidas sobre insumos agrícolas, preços, disponibilidade, políticas e logística, simulando o comportamento de um atendente rural.

## Arquitetura

Fluxo da informação:

```
WhatsApp → Webhook (/webhook) → API (/mensagem)
     → RAG (dados/*.txt) → LLM → Webhook → WhatsApp
```

### Componentes principais

| Arquivo | Função |
|--------|--------|
| `app.py` | API FastAPI |
| `webhook.py` | Webhook WhatsApp |
| `llm_client.py` | Cliente LLM |
| `rag.py` | RAG simplificado |
| `dados/*.txt` | Base de conhecimento |
| `prompts/colin_system_prompt.txt` | System Prompt |
| `docs/DESAFIO_TECNICO.md` | Documento técnico |
| `logs/` | Logs |

## ▶️ Como executar o projeto

### 1) Ambiente virtual

```
python -m venv venv
source venv/Scripts/activate
```

### 2) Instalar dependências

```
pip install -r requirements.txt
```

### 3) Criar `.env`

```
OPENAI_API_KEY=SEU_TOKEN
OPENAI_MODEL_NAME=gpt-4o-mini
```

### 4) Rodar servidor

```
uvicorn app:app --reload
```


### `/mensagem`

```
POST /mensagem
{"mensagem": "Vocês têm semente TMG 7062?"}
```

### `/webhook`

```json
{
  "entry": [
    { "changes": [ { "value": { "messages": [
      { "from": "5511999999999", "text": { "body": "Preço da semente?" } }
    ]}}]}
  ]
}
```

## Estrutura

```
colin_agro_bot/
├── app.py
├── webhook.py
├── llm_client.py
├── rag.py
├── dados/
├── prompts/
├── docs/
├── logs/
├── requirements.txt
└── .env.example
```

