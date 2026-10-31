import argparse
import asyncio
from collections import Counter

from app.config import EmbeddingSettings, MetadataSettings
from app.database import create_metadata_engine
from app.embeddings.client import LocalEmbedder
from app.embeddings.documents import (
    CatalogDocument,
    load_catalog_documents,
)
from app.embeddings.search import InMemoryCatalog


async def read_documents() -> list[CatalogDocument]:
    engine = create_metadata_engine(MetadataSettings())

    try:
        return await load_catalog_documents(engine)
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search the English metadata catalog locally."
    )

    parser.add_argument(
        "question",
        nargs="?",
        default=(
            "How much revenue did completed orders "
            "earn after discounts?"
        ),
    )

    parser.add_argument("--top-k", type=int, default=5)

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print catalog documents without loading the model.",
    )

    args = parser.parse_args()

    if args.top_k < 1:
        parser.error("--top-k must be at least 1")

    documents = asyncio.run(read_documents())

    print("Document count:", len(documents))
    print(
        "Document kinds:",
        dict(Counter(document.kind for document in documents)),
    )

    if args.preview:
        for document in documents:
            print(f"\n[{document.document_id}]")
            print(document.text)

        return

    settings = EmbeddingSettings()

    print("Model:", settings.embedding_model)
    print("Device:", settings.embedding_device)

    embedder = LocalEmbedder(settings)
    index = InMemoryCatalog(documents, embedder)

    print("Document vector shape:", index.vectors.shape)
    print(f"\nQuestion: {args.question}")

    hits = index.search(
        args.question,
        top_k=args.top_k,
    )

    for rank, hit in enumerate(hits, start=1):
        document = hit.document

        print(
            f"\n{rank}. {document.document_id} "
            f"score={hit.score:.4f}"
        )
        print("Catalog ID:", document.catalog_id)
        print(document.text)

    print("\nSearch completed.")


if __name__ == "__main__":
    main()