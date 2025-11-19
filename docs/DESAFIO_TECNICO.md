DESAFIO TÉCNICO – Engenheiro de Prompt & IA Conversacional
Solução – Colin Agro Bot (Versão Simples e Objetiva)

Este documento apresenta a solução desenvolvida para o agente Colin, voltado ao atendimento de produtores rurais via WhatsApp, utilizando LLM e um RAG simplificado.

Arquitetura da solução

Fluxo principal:

O produtor rural envia uma mensagem pelo WhatsApp.

A WhatsApp Cloud API envia o payload para o servidor via webhook (POST /webhook).

O webhook identifica o texto e chama a API interna.

O RAG lê os arquivos .txt, busca trechos relevantes e retorna um contexto.

O llm_client.py monta o SYSTEM PROMPT, inclui o contexto e envia tudo ao modelo LLM.

A resposta é devolvida ao webhook, que a formata no padrão do WhatsApp Cloud API.

O produtor recebe a mensagem processada pelo Colin.

Representação simples:

WhatsApp → Webhook → API → RAG → LLM → Webhook → WhatsApp

Decisões de projeto
Prompt do Colin

O prompt foi estruturado para funcionar bem no WhatsApp e atender produtores rurais de forma direta:

Linguagem simples e objetiva.

Foco em produtos, preço, estoque e políticas.

Uso obrigatório do contexto retornado pelo RAG.

Regras de segurança para evitar invenções e informações imprecisas.

O prompt ficou bem completo, o que melhora a qualidade da resposta, mas como consequência ele consome mais tokens por requisição.

RAG Simplificado

O RAG foi implementado com arquivos .txt fáceis de editar e substituir.
Inclui:

Leitura dos documentos;

Indexação em memória;

Busca por similaridade;

Retorno dos trechos relevantes para o modelo.

Apesar de simples, cumpre bem o papel de fornecer contexto estável e previsível ao agente.

API e Webhook

Construído com FastAPI para manter tipagem, clareza e documentação.

/mensagem permite testar a inteligência do Colin diretamente.

/webhook simula o comportamento da WhatsApp Cloud API.

Logging em JSON registra mensagens, respostas e tokens usados.

Fluxo conversacional rural

O Colin responde de forma curta, clara e direta, solicitando apenas as informações mínimas (região, quantidade, etc.).
As respostas seguem o estilo usado no campo: objetivas, sem formalidade exagerada e sem criar expectativas que não existem.

Limitações reconhecidas

O RAG funciona apenas em memória e não escala para grandes volumes de dados.

A função de embeddings é simples, criando um índice básico para demonstração.

O webhook não valida assinaturas do WhatsApp (apenas simula).

Os logs são locais, sem integração com ferramenta de observabilidade.

O system prompt, por ser detalhado, aumenta o custo de tokens por chamada.