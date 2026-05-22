# audit_extraction_engine

A small RAG pipeline for querying the sample contract in `../data/Fuel Supply Agreement.pdf`.

This module does four things:

1. loads the PDF
2. splits it into chunks
3. stores chunks in ChromaDB with embeddings
4. answers questions using retrieved context

## End-to-End Flow

```text
PDF file
  |
  v
Extract text with PyMuPDF
  |
  v
Split text into chunks
  |
  v
Create embeddings
  |
  v
Store chunks in ChromaDB

User question
  |
  v
Embed question
  |
  v
Search ChromaDB
  |
  v
Retrieve top chunks
  |
  v
Add retrieved chunks to prompt
  |
  v
Generate answer
```

## Tech Stack

- PDF loader: `PyMuPDF`
- Text splitter: `RecursiveCharacterTextSplitter`
- Vector DB: `ChromaDB`
- Embeddings:
  - `text-embedding-3-small` when `OPENAI_API_KEY` is set
  - local fallback embedding otherwise
- Answer model: `gpt-4o-mini`

## Folder Structure

```text
audit_extraction_engine/
├── artifacts/
├── scripts/
│   ├── ask_contract.py
│   └── run_ingest.py
├── src/
│   └── audit_extraction_engine/
│       ├── config.py
│       ├── embedding_provider.py
│       ├── generator.py
│       ├── pdf_loader.py
│       ├── pipeline.py
│       ├── query.py
│       ├── schemas.py
│       ├── text_splitter.py
│       └── vector_store.py
└── storage/
    └── chroma/
```

## How Ingestion Works

```text
run_ingest.py
  |
  v
Read PDF
  |
  v
Extract page-wise text
  |
  v
Normalize text
  |
  v
Create overlapping chunks
  |
  v
Generate embeddings
  |
  v
Store chunks in ChromaDB
  |
  v
Write artifacts
```

When you run:

```bash
python3 scripts/run_ingest.py
```

the system:

- reads the PDF from `../data/`
- extracts text page by page
- chunks the text with overlap
- generates embeddings
- stores chunk text, metadata, and vectors in ChromaDB
- writes debugging artifacts to `artifacts/`

## How Question Answering Works

```text
ask_contract.py
  |
  v
Take user question
  |
  v
Generate question embedding
  |
  v
Search ChromaDB
  |
  v
Return top chunks
  |
  v
Build prompt with retrieved context
  |
  v
Generate answer with LLM
  |
  v
Write last_query.json
```

When you run:

```bash
python3 scripts/ask_contract.py "What is the lock-in period?"
```

the system:

- embeds the question
- retrieves the most relevant chunks
- sends those chunks to the LLM as context
- returns an answer grounded in the document

## Artifacts

The `artifacts/` folder is there to make the RAG pipeline visible and easy to debug.

### What gets generated

- `raw_text.json`
  Generated during ingestion after PDF extraction.
- `chunks.json`
  Generated during ingestion after chunking.
- `ingest_report.json`
  Generated at the end of ingestion.
- `last_query.json`
  Generated each time you ask a question.

### What each file contains

- `raw_text.json`
  page-by-page extracted text
- `chunks.json`
  chunk text plus metadata like page number and chunk id
- `ingest_report.json`
  summary of the latest indexing run, including embedding provider and model
- `last_query.json`
  latest question, retrieved chunks, and generated answer

## Run It

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Free local mode

```bash
python3 scripts/run_ingest.py
python3 scripts/ask_contract.py "What is the lock-in period?"
```

### 3. OpenAI mode

```bash
source ~/.zshrc
python3 scripts/run_ingest.py
python3 scripts/ask_contract.py "Within how many days must compensation for the Failed Quantity be paid?"
```

## Try Your Own Questions

You only need to change the question string:

```bash
python3 scripts/ask_contract.py "Your question here"
```

Examples:

- `What is the lock-in period?`
- `When can the seller invoke the Performance Security?`
- `How much notice is required after the lock-in period?`
- `What happens if the purchaser terminates before the lock-in period expires?`

## Important Files

- `scripts/run_ingest.py`
  entry point for indexing the PDF
- `scripts/ask_contract.py`
  entry point for asking questions
- `src/audit_extraction_engine/pipeline.py`
  ingestion pipeline
- `src/audit_extraction_engine/vector_store.py`
  ChromaDB indexing and retrieval
- `src/audit_extraction_engine/generator.py`
  final answer generation

## Important Note

Re-run ingestion whenever you change the embedding model or provider:

```bash
python3 scripts/run_ingest.py
```

Otherwise the stored document vectors and query vectors may not match.
