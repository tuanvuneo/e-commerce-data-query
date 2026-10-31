# E-commerce Data Query

An English-language AI assistant for querying e-commerce data.

Users will ask business questions in English. The application will
retrieve relevant metadata, generate and validate SQL, query a
read-only warehouse connection, and display the results.

Example questions:

- What were total sales by region in March 2026?
- Which five products generated the most revenue?
- How many orders were cancelled?
- What was the average order value by customer segment?
- How did monthly sales change over time?

Planned stack:

- Python and uv
- FastAPI
- OpenRouter for chat models
- Qwen/Qwen3-Embedding-0.6B for local embeddings
- MySQL
- Qdrant
- Elasticsearch
- LangGraph
- React and Vite

Week 1 milestone:

- A working FastAPI application
- A health endpoint
- A standalone OpenRouter connection check
- Private configuration excluded from Git

Start the API:

`uv run uvicorn main:app --reload`

Check OpenRouter:

`uv run python -m app.check_openrouter`