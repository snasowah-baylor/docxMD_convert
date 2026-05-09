# docx → md Converter

A lightweight FastAPI web service that converts `.docx` files to clean Markdown (`.md`) — instantly, in the browser. Upload a Word document, download the Markdown equivalent with the same filename.

Built as part of the [nasowah.com](https://nasowah.com) AWS portfolio.

---

## Features

- **Drag-and-drop UI** — no JavaScript frameworks, plain HTML + Fetch API
- **Accurate conversion** — powered by [mammoth](https://github.com/mwilliamson/python-mammoth), preserving headings, bold, italic, lists, and hyperlinks
- **Filename mirroring** — `quarterly-report.docx` → `quarterly-report.md`
- **Auto API docs** — FastAPI serves Swagger UI at `/docs` out of the box
- **Docker-ready** — single `docker compose up` for local dev; same image deploys to AWS
- **Free tier deployable** — targets AWS Elastic Beanstalk / EC2 t3.micro

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ASGI server | [Uvicorn](https://www.uvicorn.org/) |
| Conversion engine | [mammoth](https://github.com/mwilliamson/python-mammoth) |
| Containerization | Docker + Docker Compose |
| Deployment | AWS Elastic Beanstalk / EC2 |

---

## Project Structure

```
docx-converter/
├── main.py                  # FastAPI app — /, /health, /convert
├── requirements.txt
├── templates/
│   └── index.html           # Drag-and-drop UI
├── Dockerfile               # Production image
├── docker-compose.yml       # Local dev with hot reload
├── .dockerignore
├── .gitignore
├── .env.example             # Safe env template — copy to .env
├── Procfile                 # AWS Elastic Beanstalk entry point
└── SPEC.md                  # Spec-driven development source of truth
```

---

## Quickstart

### Option 1 — Docker (Recommended)

```bash
git clone https://github.com/YOUR_USERNAME/docx-converter.git
cd docx-converter
docker compose up
```

Open [http://localhost:8000](http://localhost:8000)

### Option 2 — Plain Python

```bash
git clone https://github.com/YOUR_USERNAME/docx-converter.git
cd docx-converter

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000)

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Drag-and-drop upload UI |
| `GET` | `/health` | Health check → `{"status": "ok"}` |
| `POST` | `/convert` | Upload `.docx`, receive `.md` download |
| `GET` | `/docs` | Swagger UI — interactive API documentation |

### Convert via curl

```bash
curl -X POST http://localhost:8000/convert \
  -F "file=@your-document.docx" \
  -o your-document.md
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in values as needed.

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `development` or `production` |
| `AWS_REGION` | `us-east-1` | AWS region (local dev only) |

> In production on AWS EC2 or Elastic Beanstalk, credentials are sourced from the **IAM instance role** — never hardcoded or committed.

---

## Docker Hub

The production image is published at:

```
docker pull YOUR_DOCKERHUB_USERNAME/docx-converter:latest
```

To run from Docker Hub directly:

```bash
docker run -p 8000:8000 YOUR_DOCKERHUB_USERNAME/docx-converter:latest
```

---

## Deployment — AWS

### Elastic Beanstalk

```bash
pip install awsebcli
eb init -p python-3.11 docx-converter --region us-east-1
eb create docx-converter-env
eb deploy
eb open
```

### EC2 with Docker

```bash
# SSH into your instance, then:
docker pull YOUR_DOCKERHUB_USERNAME/docx-converter:latest
docker run -d -p 8000:8000 YOUR_DOCKERHUB_USERNAME/docx-converter:latest
```

---

## Development Workflow

This project uses **spec-driven development**. `SPEC.md` is the source of truth — update it before making any code changes, then use [Gemini Code Assist](https://cloud.google.com/products/gemini/code-assist) in VS Code to generate the implementation:

```
Update SPEC.md → Prompt Gemini with @workspace → Review → Commit
```

---

## Roadmap

- [ ] File size limit (10MB max, return 413)
- [ ] Batch conversion (multiple `.docx` in one upload)
- [ ] Preview pane — rendered Markdown alongside download
- [ ] Auth layer — API key protection for production use
- [ ] S3 integration — store converted files for later retrieval

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Stephen Sowah**
M.S. Information Systems (Cybersecurity) — Baylor University, Hankamer School of Business
[nasowah.com](https://nasowah.com) · [GitHub](https://github.com/snasowah-baylor) · [LinkedIn](https://linkedin.com/in/nasowah)
