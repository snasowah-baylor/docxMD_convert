# docx-to-md Converter — Spec v1.0

## Purpose
A FastAPI web service that accepts a .docx file upload, converts it to Markdown,
and returns a downloadable .md file with the same base filename.

## Endpoints
- POST /convert
  - Input: multipart form-data, field name `file`, accepts .docx only
  - Output: .md file download, filename mirrors input (e.g. report.docx → report.md)
  - Errors: 400 if wrong file type, 500 on conversion failure

## Conversion rules
- Use mammoth library for docx → markdown
- Preserve headings, bold, italic, lists, and hyperlinks
- Strip comments and tracked changes
- Output UTF-8

## UI
- Single HTML page at GET /
- Drag-and-drop or browse to upload a .docx
- Download link appears after conversion
- No JavaScript frameworks — plain HTML + Fetch API

## Deployment target
- AWS Elastic Beanstalk, Python 3.11 platform
- Free tier (t3.micro)

## Docker

### Local Development
- Dockerfile base image: python:3.11-slim
- Working directory: /app
- Expose port 8000
- Run with uvicorn, hot reload enabled via docker-compose volume mount

### docker-compose
- Service name: web
- Mount project root as volume for live reload during development
- Command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

### .dockerignore
- Exclude: __pycache__/, *.pyc, .env, .git, .ebignore, Procfile

### Production (AWS EC2)
- Same Dockerfile used for both local and production
- No compose in production — plain docker run
- Port mapping: 8000:8000

## Security
- Secrets managed via environment variables only
- .env file never committed — use .env.example as template
- AWS credentials sourced from instance IAM role in production, never hardcoded