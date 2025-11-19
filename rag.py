import os
import pathlib
import hashlib
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

import numpy as np

from llm_client import gerar_resposta


BASE_DIR = pathlib.Path(__file__).resolve().parent
DADOS_DIR = BASE_DIR / "dados"
EMBEDDING_DIM = 256


@dataclass
class Documento:
    id: str
    titulo: str
    conteudo: str
    fonte: str 


DOCUMENTOS: List[Documento] = []
VETORES: List[np.ndarray] = []
INDEXADO: bool = False


def carregar_documentos() -> List[Documento]:
    """
    Lê os arquivos .txt da pasta dados/ e retorna uma lista de Documento.
    """
    docs: List[Documento] = []
    if not DADOS_DIR.exists():
        return docs

    for path in DADOS_DIR.glob("*.txt"):
        try:
            texto = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            texto = path.read_text(encoding="latin-1")

        titulo = path.stem.replace("_", " ").title()
        doc = Documento(
            id=str(len(docs) + 1),
            titulo=titulo,
            conteudo=texto,
            fonte=path.name,
        )
        docs.append(doc)

    return docs


def gerar_embeddings(texto: str) -> np.ndarray:
    """
    Gera um vetor numérico simples a partir do texto.
    IMPLEMENTAÇÃO SIMPLIFICADA (HASHING):
      - Para ambiente real, substituir por chamada ao endpoint de embeddings
        do provedor de LLM (ex: modelo equivalente ao text-embedding-3-small).
    """
    vec = np.zeros(EMBEDDING_DIM, dtype=float)
    tokens = texto.lower().split()

    for token in tokens:
        h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
        idx = h % EMBEDDING_DIM
        vec[idx] += 1.0

    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def indexar_documentos() -> None:
    """
    Constrói os vetores (embeddings) de todos os documentos e guarda em memória.
    """
    global DOCUMENTOS, VETORES, INDEXADO

    if INDEXADO:
        return

    DOCUMENTOS = carregar_documentos()
    VETORES = [gerar_embeddings(doc.conteudo) for doc in DOCUMENTOS]
    INDEXADO = True


def _similaridade_cosseno(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
    return float(np.dot(a, b) / denom)


def buscar_contexto(consulta: str, top_k: int = 3) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Retorna um texto de contexto concatenado com os trechos mais relevantes
    e metadados dos documentos selecionados.

    - Gera embedding da consulta.
    - Calcula similaridade com cada documento.
    - Retorna os top_k mais similares.
    """
    if not INDEXADO:
        indexar_documentos()

    if not DOCUMENTOS:
        return "", []

    consulta_vec = gerar_embeddings(consulta)
    scores: List[Tuple[int, float]] = []

    for idx, doc_vec in enumerate(VETORES):
        score = _similaridade_cosseno(consulta_vec, doc_vec)
        scores.append((idx, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    selecionados = scores[:top_k]

    blocos = []
    detalhes: List[Dict[str, Any]] = []
    for idx, score in selecionados:
        doc = DOCUMENTOS[idx]
        blocos.append(
            f"[Fonte: {doc.fonte} | Score: {score:.3f}]\n{doc.conteudo.strip()}\n"
        )
        detalhes.append(
            {
                "id": doc.id,
                "titulo": doc.titulo,
                "fonte": doc.fonte,
                "score": score,
            }
        )

    contexto = "\n\n".join(blocos)
    return contexto, detalhes


def gerar_resposta_com_rag(consulta: str) -> Dict[str, Any]:
    """
    Conecta o RAG com o LLM:
    - Busca contexto relevante nos documentos.
    - Envia a consulta + contexto para o modelo.
    - Retorna o dicionário padronizado da função gerar_resposta().

    Esta função é chamada pela API (app.py) quando RAG_ENABLED=true.
    """
    contexto, detalhes = buscar_contexto(consulta)

    resultado = gerar_resposta(
        mensagem=consulta,
        contexto=contexto,
        origem_contexto="rag",
    )

    resultado["documentos_usados"] = detalhes
    return resultado
