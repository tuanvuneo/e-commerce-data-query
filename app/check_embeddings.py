from importlib.metadata import version

import numpy as np

from app.config import EmbeddingSettings
from app.embeddings.client import LocalEmbedder


def main() -> None:
    packages = (
        "sentence-transformers",
        "transformers",
        "torch",
        "numpy",
    )

    print(
        "Package versions:",
        {package: version(package) for package in packages},
    )

    settings = EmbeddingSettings()

    print("Model:", settings.embedding_model)
    print("Device:", settings.embedding_device)

    embedder = LocalEmbedder(settings)

    documents = [
        {
            "id": "example:net_sales",
            "text": (
                "Net sales is the money earned from completed orders "
                "after subtracting line discounts."
            ),
        },
        {
            "id": "example:shipping_state",
            "text": (
                "Shipping state identifies the state containing "
                "the city where an order was shipped."
            ),
        },
        {
            "id": "example:customer_gender",
            "text": (
                "Customer gender is recorded as male, female, "
                "or not-specified."
            ),
        },
    ]

    queries = [
        "How much revenue did completed orders earn after discounts?",
        "Which state received the shipment?",
    ]

    query_vectors = embedder.encode_queries(queries)
    document_vectors = embedder.encode_documents(
        [document["text"] for document in documents]
    )

    scores = query_vectors @ document_vectors.T

    if scores.shape != (len(queries), len(documents)):
        raise AssertionError("Unexpected score matrix shape.")

    if not np.isfinite(scores).all():
        raise AssertionError("Similarity scores are not finite.")

    if np.any(scores < -1.0001) or np.any(scores > 1.0001):
        raise AssertionError("Cosine scores are outside their range.")

    print("Query shape:", query_vectors.shape)
    print("Document shape:", document_vectors.shape)
    print("Score shape:", scores.shape)
    print(
        "Query vector lengths:",
        np.linalg.norm(query_vectors, axis=1),
    )
    print(
        "Document vector lengths:",
        np.linalg.norm(document_vectors, axis=1),
    )

    for row, query in enumerate(queries):
        print(f"\nQuestion: {query}")

        indices = np.argsort(-scores[row], kind="stable")

        for rank, index in enumerate(indices, start=1):
            document = documents[int(index)]

            print(
                f"{rank}. {document['id']} "
                f"score={float(scores[row, index]):.4f}"
            )
            print(f"   {document['text']}")

    print(
        "\nAll shape, finite-value, "
        "and normalization checks passed."
    )


if __name__ == "__main__":
    main()