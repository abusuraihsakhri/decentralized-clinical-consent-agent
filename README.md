# Decentralized Clinical Consent Agent

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

**Decentralized Clinical Consent Agent** is an analytical and computational platform implementing smart contract dynamic patient data use authorization and signature verification. It provides multi-worker evaluation of clinical tasks with tamper-evident audit logging and zero-PHI outbound protection.

---

## Key Capabilities

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Zero-PHI Outbound Interceptor**: Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation and state transition.
- **FastAPI REST API**: Exposes OpenAPI 3.1 REST endpoints and operational metrics.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/decentralized-clinical-consent-agent.git
cd decentralized-clinical-consent-agent

# Install dependencies
pip install -e .

# Or install with test dependencies
pip install -e ".[test]"
```

---

## CLI Usage

### 1. Run Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameters
- `--task-id`: Unique task / case identifier
- `--target`: Entity, patient key, or genomic/cryptographic target
- `--primary`: Primary domain measurement or score (float)
- `--secondary`: Secondary kinetic or confidence score (float)
- `--critical`: Emergency escalation flag
- `--status`: Status code or phenotype descriptor

---

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health and metadata check |
| GET | `/metrics` | Operational metrics |
| POST | `/api/audit` | Dispatch task payload across specialized workers |
| POST | `/api/chat` | Air-gapped supervisory conversational assistant |
| GET | `/api/audit/logs` | Retrieve and verify HMAC audit trail |

---

## Testing

```bash
# Run the full test suite
pytest -v

# Run with coverage
pytest -v --cov=agents --cov=consent_ledger
```

---

## Simulation Benchmark

```bash
# Run high-throughput simulation (default 100 tasks)
python simulator.py 1000
```

---

## Security Configuration

### Audit Secret Key
Set the `AUDIT_SECRET_KEY` environment variable for persistent cryptographic signing:
```bash
export AUDIT_SECRET_KEY="your-secure-random-key"
```

If not set, a random key is generated per session (logs will not persist across restarts).

### Docker Deployment
```bash
docker build -t decentralized-clinical-consent-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-key" decentralized-clinical-consent-agent
```

Or using docker-compose:
```bash
docker-compose up -d
```

---

## Project Structure

```
decentralized-clinical-consent-agent/
├── agents/                  # Core agent modules
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data schemas
│   ├── supervisor.py       # Multi-worker orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   ├── llm_factory.py      # LLM provider factory
│   ├── learning.py         # Bayesian calibration engine
│   ├── metrics.py          # Prometheus metrics collector
│   └── streamer.py         # WebSocket telemetry broadcaster
├── consent_ledger/          # ConsentLedger module
│   ├── agents.py           # Consent validation agents
│   ├── engine.py           # Core algorithmic engine
│   ├── models.py           # Data models
│   ├── cli.py              # CLI for consent ledger
│   └── server.py           # FastAPI server factory
├── tests/                   # Test suite
├── web/index.html           # Operations console UI
├── cli.py                   # Main CLI entry point
├── simulator.py             # High-throughput simulator
├── enrichment.py            # Enrichment feature engines
├── pyproject.toml           # Project configuration
└── Dockerfile               # Container build config
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
