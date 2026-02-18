"""
# Common Use Cases

Real-world integration patterns.

---

## Web API

<details open>
<summary><strong>FastAPI file-upload endpoint</strong></summary>

```python
from fastapi import FastAPI, UploadFile, HTTPException
from io import BytesIO
from TextSpitter import TextSpitter

app = FastAPI()
ALLOWED = {".pdf", ".docx", ".txt", ".csv"}

@app.post("/extract")
async def extract_text(file: UploadFile) -> dict:
    ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED:
        raise HTTPException(400, f"Unsupported type: {ext}")
    data = await file.read()
    text = TextSpitter(file_obj=BytesIO(data), filename=file.filename)
    return {"filename": file.filename, "chars": len(text), "text": text}
```

</details>

<details>
<summary><strong>Django / DRF</strong></summary>

```python
from io import BytesIO
from rest_framework.decorators import api_view
from rest_framework.response import Response
from TextSpitter import TextSpitter

@api_view(["POST"])
def extract(request):
    f = request.FILES.get("file")
    if not f:
        return Response({"error": "No file"}, status=400)
    text = TextSpitter(file_obj=BytesIO(f.read()), filename=f.name)
    return Response({"text": text})
```

</details>

---

## Cloud storage (AWS S3)

<details open>
<summary><strong>Extract directly from S3</strong></summary>

```python
import boto3
from io import BytesIO
from TextSpitter import TextSpitter

s3 = boto3.client("s3")

def extract_from_s3(bucket: str, key: str) -> str:
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj["Body"].read()
    return TextSpitter(file_obj=BytesIO(data), filename=key.split("/")[-1])
```

</details>

<details>
<summary><strong>Batch-process an S3 prefix</strong></summary>

```python
import boto3
from io import BytesIO
from TextSpitter import TextSpitter

s3 = boto3.client("s3")

def extract_prefix(bucket: str, prefix: str) -> dict:
    results = {}
    pager = s3.get_paginator("list_objects_v2")
    for page in pager.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            data = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
            try:
                results[key] = TextSpitter(
                    file_obj=BytesIO(data), filename=key.rsplit("/", 1)[-1]
                )
            except Exception as exc:
                results[key] = f"[ERROR: {exc}]"
    return results
```

</details>

---

## LLM / RAG pipelines

<details open>
<summary><strong>LangChain document loader</strong></summary>

```python
from langchain.schema import Document
from TextSpitter import TextSpitter

def load_documents(paths: list) -> list:
    return [
        Document(page_content=TextSpitter(filename=p), metadata={"source": p})
        for p in paths
        if TextSpitter(filename=p)
    ]
```

</details>

<details>
<summary><strong>OpenAI embedding pipeline</strong></summary>

```python
import openai
from TextSpitter import TextSpitter

def embed_file(path: str) -> list:
    text = TextSpitter(filename=path)[:8000]   # respect token limit
    resp = openai.embeddings.create(input=text, model="text-embedding-3-small")
    return resp.data[0].embedding
```

</details>

---

## Batch processing

<details open>
<summary><strong>Directory tree</strong></summary>

```python
from pathlib import Path
from TextSpitter import TextSpitter

def extract_all(root: str, exts: set = None) -> dict:
    exts = exts or {".pdf", ".docx", ".txt", ".csv"}
    out = {}
    for p in Path(root).rglob("*"):
        if p.suffix.lower() in exts:
            try:
                out[str(p)] = TextSpitter(filename=str(p))
            except Exception as e:
                out[str(p)] = f"[ERROR: {e}]"
    return out
```

</details>

<details>
<summary><strong>Parallel with ThreadPoolExecutor</strong></summary>

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from TextSpitter import TextSpitter

def extract_parallel(paths: list, workers: int = 8) -> dict:
    def _one(p):
        try:
            return p, TextSpitter(filename=p)
        except Exception as e:
            return p, f"[ERROR: {e}]"

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(f.result() for f in as_completed(pool.submit(_one, p) for p in paths))
```

</details>

---

## Logging

<details open>
<summary><strong>Enable loguru</strong></summary>

```sh
pip install "textspitter[logging]"
```

```python
from loguru import logger
logger.add("textspitter.log", rotation="10 MB", level="WARNING")

from TextSpitter import TextSpitter
text = TextSpitter(filename="document.pdf")
```

</details>

<details>
<summary><strong>Stdlib logging (no loguru)</strong></summary>

```python
import logging
logging.getLogger("textspitter").setLevel(logging.DEBUG)

from TextSpitter import TextSpitter
text = TextSpitter(filename="document.pdf")
```

</details>
"""
