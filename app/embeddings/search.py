from dataclasses import dataclass

import numpy as np

from app.embeddings.client import LocalEmbedder
from app.embeddings.documents import CatalogDocument


@dataclass(frozen=True)
class SearchHit:
    document: CatalogDocument
    score: float


class InMemoryCatalog:
    def __init__(
        self,
        documents: list[CatalogDocument],
        embedder: LocalEmbedder,
    ) -> None:
        if not documents:
            raise ValueError("Cannot index an empty document list.")

        document_ids = [
            document.document_id
            for document in documents
        ]

        if len(document_ids) != len(set(document_ids)):
            raise ValueError("Document IDs must be unique.")

        self.documents = tuple(documents)
        self.embedder = embedder

        self.vectors = embedder.encode_documents(
            [document.text for document in self.documents]
        )

    def search(
        self,
        question: str,
        *,
        top_k: int = 5,
    ) -> list[SearchHit]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_vector = self.embedder.encode_queries([question])

        scores = (query_vector @ self.vectors.T)[0]

        indices = np.argsort(
            -scores,
            kind="stable",
        )[:top_k]

        return [
            SearchHit(
                document=self.documents[int(index)],
                score=float(scores[index]),
            )
            for index in indices
        ]