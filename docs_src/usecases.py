"""
# Common Use Cases

Practical integration patterns for the most frequent TextSpitter deployment
scenarios.

---

## Web API (FastAPI)

<details open>
<summary><strong>File-upload endpoint</strong></summary>

```python
from fastapi import FastAPI, UploadFile, HTTPException
from io import BytesIO
from TextSpitter import TextSpitter

app = FastAPI()

ALLOWED = {".pdf", ".docx", ".txt", ".csv"}

@app.post("/extract")
async def extract_text(file: UploadFile) -> dict:
    suffix = "." + file.filename.rsplit(".", 1)[-1].lower()
    if suffix not in ALLOWED:
        raise HTTPException(400, f"Unsupported file type: {suffix}")

    data = await file.read()
    text = TextSpitter(file_obj=BytesIO(data), filename=file.filename)
    return {"filename": file.filename, "characters": len(text), "text": text}
```

</details>

<details>
<summary><strong>Django / DRF file upload</strong></summary>

```python
from io import BytesIO
from rest_framework.decorators import api_view
from rest_framework.response import Response
from TextSpitter import TextSpitter

@api_view(["POST"])
def extract(request):
    uploaded = request.FILES.get("file")
    if not uploaded:
        return Response({"error": "No file provided"}, status=400)

    data = uploaded.read()
    text = TextSpitter(file_obj=BytesIO(data), filename=uploaded.name)
    return Response({"text": text})
```

</details>

---

## Cloud Storage (AWS S3)

<details open>
<summary><strong>Extract directly from S3 without writing to disk</strong></summary>

```python
import boto3
from io import BytesIO
from TextSpitter import TextSpitter

s3 = boto3.client("s3")

def extract_from_s3(bucket: str, key: str) -> str:
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj["Body"].read()
    filename = key.split("/")[-1]          # preserve original filename
    return TextSpitter(file_obj=BytesIO(data), filename=filename)

text = extract_from_s3("my-bucket", "documents/report.pdf")
```

</details>

<details>
<summary><strong>Batch-process an entire S3 prefix</strong></summary>

```python
import boto3
from io import BytesIO
from TextSpitter import TextSpitter

s3 = boto3.client("s3")

def extract_prefix(bucket: str, prefix: str) -> dict[str, str]:
    results = {}
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            data = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
            filename = key.rsplit("/", 1)[-1]
            try:
                results[key] = TextSpitter(
                    file_obj=BytesIO(data), filename=filename
                )
            except Exception as exc:
                results[key] = f"[ERROR: {exc}]"
    return results
```

</details>

---

## LLM / RAG Pipelines

<details open>
<summary><strong>LangChain document loader</strong></summary>

```python
from langchain.schema import Document
from TextSpitter import TextSpitter

def load_documents(paths: list[str]) -> list[Document]:
    docs = []
    for path in paths:
        text = TextSpitter(filename=path)
        if text:
            docs.append(Document(page_content=text, metadata={"source": path}))
    return docs
```

</details>

<details>
<summary><strong>OpenAI embedding pipeline</strong></summary>

```python
import openai
from TextSpitter import TextSpitter

def embed_file(path: str) -> list[float]:
    text = TextSpitter(filename=path)
    # Truncate to token limit if needed
    text = text[:8000]
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding
```

</details>

---

## Batch Processing

<details open>
<summary><strong>Process a directory tree</strong></summary>

```python
from pathlib import Path
from TextSpitter import TextSpitter

def extract_all(root: str, extensions: set[str] | None = None) -> dict[str, str]:
    \"""Extract text from every supported file under *root*.\"""
    supported = extensions or {".pdf", ".docx", ".txt", ".csv"}
    results: dict[str, str] = {}

    for path in Path(root).rglob("*"):
        if path.suffix.lower() in supported:
            try:
                results[str(path)] = TextSpitter(filename=str(path))
            except Exception as exc:
                results[str(path)] = f"[ERROR: {exc}]"

    return results
```

</details>

<details>
<summary><strong>Parallel extraction with ThreadPoolExecutor</strong></summary>

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from TextSpitter import TextSpitter

def extract_parallel(paths: list[str], workers: int = 8) -> dict[str, str]:
    results: dict[str, str] = {}

    def _extract(p: str) -> tuple[str, str]:
        try:
            return p, TextSpitter(filename=p)
        except Exception as exc:
            return p, f"[ERROR: {exc}]"

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_extract, p): p for p in paths}
        for future in as_completed(futures):
            path, text = future.result()
            results[path] = text

    return results
```

</details>

---

## Logging Integration

<details open>
<summary><strong>Enable loguru logging</strong></summary>

```sh
pip install "textspitter[logging]"
```

```python
from loguru import logger

# Sink to a file with rotation
logger.add("textspitter.log", rotation="10 MB", level="WARNING")

from TextSpitter import TextSpitter
text = TextSpitter(filename="document.pdf")
# PDF fallback warnings etc. now appear in textspitter.log
```

</details>

<details>
<summary><strong>Stdlib logging (no loguru)</strong></summary>

```python
import logging

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("textspitter")
log.setLevel(logging.DEBUG)

from TextSpitter import TextSpitter
text = TextSpitter(filename="document.pdf")
```

</details>
"""
