# AI-Powered Medical Report Analysis & Prescription Understanding System

## Backend Service

An educational prototype engineered with FastAPI, SQLAlchemy 2.x, Alembic, OCR (PyMuPDF & Tesseract), and Retrieval-Augmented Generation (RAG).

> **IMPORTANT MEDICAL DISCLAIMER**: This system is designed solely for educational and research prototyping. It must not be used to replace professional medical judgment, provide clinical diagnoses, or independently prescribe or alter medications.

---

## 1. System Architecture

The backend adopts a modular, domain-driven structure with strict separation of concerns:

```
backend/
├── app/
│   ├── main.py                     # FastAPI application entrypoint, CORS, exception handlers
│   ├── core/
│   │   ├── config.py               # Settings management via Pydantic Settings & .env
│   │   ├── security.py             # Bcrypt hashing & PyJWT token management
│   │   ├── logging.py              # Privacy-preserving logging
│   │   └── exceptions.py           # Domain exceptions
│   ├── db/
│   │   ├── base.py                 # DeclarativeBase, UUID generators
│   │   └── session.py              # SQLAlchemy 2.0 Engine and get_db session dependency
│   ├── models/                     # SQLAlchemy 2.0 Database Models
│   │   ├── user.py                 # User authentication and status
│   │   ├── document.py             # Uploaded medical document records
│   │   ├── ocr_result.py           # Text extraction results and confidence metadata
│   │   ├── report_analysis.py      # Structured report explanations
│   │   ├── laboratory_value.py     # Parsed test parameters, ranges, flags
│   │   ├── prescription_item.py    # Extracted medications and confirmation state
│   │   ├── reference_document.py   # RAG medical knowledge chunks
│   │   └── audit_event.py          # Secure audit trail (no sensitive data)
│   ├── schemas/                    # Pydantic v2 schemas for request/response validation
│   ├── services/
│   │   ├── document_storage.py     # Magic byte verification, safe UUID storage
│   │   ├── document_extraction.py  # PyMuPDF digital PDF & OCR orchestrator
│   │   ├── ocr_service.py          # Image OCR engine with Tesseract fallback
│   │   ├── report_parser.py        # Laboratory report parsing and status flags
│   │   ├── llm_service.py          # Provider-agnostic LLM interface (Mock + OpenAI)
│   │   ├── rag_service.py          # Reference corpus ingestion, TF-IDF vector retrieval
│   │   ├── prescription_parser.py  # Medication extraction with uncertainty flags
│   │   └── audit_service.py        # Privacy-conscious audit recording
│   └── api/
│       ├── dependencies.py         # JWT auth, user resolution, IDOR checks
│       └── v1/
│           ├── auth.py             # /auth/register, /auth/login, /auth/me, /auth/logout
│           ├── documents.py        # /documents/upload, list, get, text review/edit, delete
│           ├── analyses.py         # /documents/{id}/analyze, /analyses/{id}, /values, /sources
│           ├── prescriptions.py    # /process-prescription, /prescription, /confirm
│           └── explanations.py     # /explanations, /reference-sources
├── alembic/                        # Alembic migration scripts
├── data/
│   ├── sample_reports/             # Synthetic test PDFs and PNG images
│   ├── uploads/                    # Local document storage
│   └── references/                 # Trusted medical reference docs
├── scripts/
│   ├── generate_sample_data.py     # Generates synthetic sample reports
│   ├── ingest_references.py        # Ingests trusted reference documents into RAG
│   └── demo_workflow.py            # End-to-end 10-step demonstration runner
├── tests/                          # Automated pytest suite (31 tests)
├── alembic.ini                     # Alembic configuration
├── Dockerfile                      # Production container image
├── docker-compose.yml              # PostgreSQL + Backend stack
├── requirements.txt                # Python dependencies
└── .env.example                    # Environment variable template
```

---

## 2. Prerequisites & Environment Setup

### Prerequisites
- Python 3.11, 3.12, 3.13, or 3.14
- Git
- (Optional) Docker and Docker Compose

### Step 1: Create Virtual Environment
```bash
cd backend
python -m venv venv
```

Activate the virtual environment:
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt)**:
  ```cmd
  .\venv\Scripts\activate.bat
  ```
- **Linux / macOS**:
  ```bash
  source venv/bin/activate
  ```

### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*Note: The default `.env` is configured with `LLM_PROVIDER=mock` and SQLite database, enabling immediate zero-configuration startup without requiring paid API keys or external services.*

---

## 3. Database Initialization & Migrations

Run database migrations using Alembic:
```bash
alembic upgrade head
```

Generate synthetic demonstration documents:
```bash
python scripts/generate_sample_data.py
```

Ingest initial trusted medical reference documents for RAG:
```bash
python scripts/ingest_references.py
```

---

## 4. Running the Development Server

Start the FastAPI application with Uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once started:
- **API Base URL**: `http://localhost:8000`
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check Probe**: `http://localhost:8000/health`
- **Readiness Probe**: `http://localhost:8000/ready`

---

## 5. Running Automated Tests

Run the full automated test suite with pytest:
```bash
pytest -v
```

To run with coverage:
```bash
pytest --cov=app tests/
```

All 31 tests run completely offline using in-memory databases and synthetic test documents.

---

## 6. Running the End-to-End Demonstration Workflow

Execute the comprehensive 10-step automated demonstration:
```bash
python scripts/demo_workflow.py
```

This script automatically executes:
1. User registration & JWT authentication
2. Uploading a synthetic CBC laboratory report
3. Extracting text directly from PDF
4. Reviewing extracted OCR text
5. Parsing laboratory values (Hemoglobin, WBC Count, Platelets, etc.)
6. Generating patient-friendly plain-language explanation via Mock LLM
7. Evaluating normal vs. abnormal flags against the report's reference intervals
8. Grounding explanations in trusted RAG medical reference sources
9. Strict citation validation (no hallucinated sources)
10. Prescription processing with uncertainty detection and human confirmation

---

## 7. Running with Docker Compose (PostgreSQL)

To run the complete stack with PostgreSQL in Docker:
```bash
docker-compose up --build
```
This automatically boots PostgreSQL, applies database migrations, seeds reference documents, and starts the FastAPI backend at `http://localhost:8000`.

To stop the containers:
```bash
docker-compose down
```

---

## 8. API Endpoint Reference

### Authentication
- `POST /api/v1/auth/register` - Create user account
- `POST /api/v1/auth/login` - Authenticate and obtain JWT Bearer token
- `GET /api/v1/auth/me` - View current user profile
- `POST /api/v1/auth/logout` - Invalidate current session token

### Document Management
- `POST /api/v1/documents/upload` - Secure document upload (PDF, PNG, JPEG) with signature verification
- `GET /api/v1/documents` - List authenticated user's documents
- `GET /api/v1/documents/{id}` - Retrieve single document details
- `GET /api/v1/documents/{id}/status` - Check document processing status
- `GET /api/v1/documents/{id}/text` - View extracted OCR text for user review
- `PATCH /api/v1/documents/{id}/text` - Correct or edit OCR text before analysis
- `DELETE /api/v1/documents/{id}` - Delete document and purge file from disk

### Medical Report Analysis & Values
- `POST /api/v1/documents/{id}/analyze` - Parse lab values and generate plain-language explanation
- `GET /api/v1/analyses/{id}` - Retrieve analysis results and explanations
- `GET /api/v1/documents/{id}/values` - Get structured laboratory values
- `GET /api/v1/analyses/{id}/sources` - Get verified RAG reference citations

### Prescription Understanding
- `POST /api/v1/documents/{id}/process-prescription` - Extract medications and flag uncertain items
- `GET /api/v1/documents/{id}/prescription` - Get extracted prescription items
- `PATCH /api/v1/prescriptions/{id}/confirm` - Human review and confirmation of medication details

### RAG & Medical Explanations
- `POST /api/v1/explanations` - Query plain-language explanations grounded in reference sources
- `GET /api/v1/reference-sources` - View ingested medical reference documents
- `GET /health` - System health probe
- `GET /ready` - Container readiness probe

---

## 9. Key Safety & Security Features

1. **Anti-Hallucination Citation Guard**: The LLM engine only cites reference sources that were genuinely retrieved and passed in context.
2. **Missing Range Preservation**: If a lab report does not provide reference ranges, they remain `null` / unavailable; the system never invents reference ranges.
3. **No Unilateral Prescription Alterations**: Uncertain medicine names or doses are flagged for explicit human confirmation.
4. **Strict IDOR Protection**: Users cannot access, view, edit, or delete another user's documents or analyses.
5. **Privacy Safeguards**: Uploaded files use non-guessable random UUID keys; passwords, tokens, and raw patient data are excluded from audit logs.
