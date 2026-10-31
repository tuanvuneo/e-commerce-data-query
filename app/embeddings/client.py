import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from app.config import EmbeddingSettings


def validate_embeddings(
    vectors: np.ndarray,
    *,
    expected_rows: int,
    dimension: int,
) -> None:
    expected_shape = (expected_rows, dimension)

    if vectors.shape != expected_shape:
        raise ValueError(
            f"Expected embedding shape {expected_shape}, "
            f"received {vectors.shape}."
        )

    if not np.isfinite(vectors).all():
        raise ValueError("Embeddings contain NaN or infinite values.")

    lengths = np.linalg.norm(vectors, axis=1)

    if not np.allclose(lengths, 1.0, atol=1e-4, rtol=0):
        raise ValueError(
            "Expected normalized embeddings with length close to 1."
        )


class LocalEmbedder:
    def __init__(self, settings: EmbeddingSettings) -> None:
        self.dimension = settings.embedding_dimension
        self.batch_size = settings.embedding_batch_size

        self.model = SentenceTransformer(
            settings.embedding_model,
            device=settings.embedding_device,
            model_kwargs={"dtype": torch.float32},
        )

        self.model.max_seq_length = settings.embedding_max_length

        actual_dimension = self.model.get_embedding_dimension()

        if actual_dimension != self.dimension:
            raise ValueError(
                f"Configured dimension is {self.dimension}, "
                f"but the model produces {actual_dimension}."
            )

        if "query" not in self.model.prompts:
            raise ValueError("The model has no saved query prompt.")

        if self.model.prompts.get("document") != "":
            raise ValueError(
                "This lesson expects an empty document prompt."
            )

    def encode_queries(self, texts: list[str]) -> np.ndarray:
        return self._encode(texts, query=True)

    def encode_documents(self, texts: list[str]) -> np.ndarray:
        return self._encode(texts, query=False)

    def _encode(
        self,
        texts: list[str],
        *,
        query: bool,
    ) -> np.ndarray:
        if not texts:
            raise ValueError("Provide at least one text.")

        if any(
            not isinstance(text, str) or not text.strip()
            for text in texts
        ):
            raise ValueError("Every text must be a nonempty string.")

        encoder = (
            self.model.encode_query
            if query
            else self.model.encode_document
        )

        result = encoder(
            texts,
            prompt_name="query" if query else "document",
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        vectors = np.asarray(result, dtype=np.float32)

        validate_embeddings(
            vectors,
            expected_rows=len(texts),
            dimension=self.dimension,
        )

        return vectors