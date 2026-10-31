# Local embeddings

The project uses Qwen/Qwen3-Embedding-0.6B through Sentence Transformers.

The baseline device is CPU with float32 model weights.

## Configuration

- EMBEDDING_MODEL: Qwen/Qwen3-Embedding-0.6B
- EMBEDDING_DIMENSION: 1024
- EMBEDDING_DEVICE: cpu
- EMBEDDING_BATCH_SIZE: 2
- EMBEDDING_MAX_LENGTH: 512

The dimension setting checks the model output width. It does not resize vectors.

## Encoding

Questions use the model's saved query prompt.

Catalog documents use the model's empty document prompt.

All returned vectors are normalized to unit length.

## Catalog documents

There is one document per column and one document per metric.

The intended teaching catalog produces 31 documents.

Document IDs preserve the original catalog identifiers with column: or metric:
prefixes.

Metric documents retain SQL expressions, required filters, and column references.

## Search

Documents and vectors are held in memory.

Similarity is calculated with a dot product between normalized vectors.

Higher scores indicate greater similarity under the embedding model.
Scores are not probabilities.

Each command starts a new process and rebuilds the in-memory index.

## Commands

Run these commands from the project root:

- uv run python -m app.check_catalog
- uv run python -m app.check_embeddings
- uv run python -m app.search_catalog --preview
- uv run python -m app.search_catalog "Which field describes shipping state?"

## Observations

Record package versions, questions, retrieved IDs, and any relevance problems here.

Do not treat exact similarity scores or rankings as fixed expected outputs.