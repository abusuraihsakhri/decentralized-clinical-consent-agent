# Decentralized Clinical Consent Agent

### [Open the Live Application →](https://abusuraihsakhri.github.io/decentralized-clinical-consent-agent/)

Prototype rule-based evaluation and audit tooling, implemented in Python with an offline browser preview. **This repository does not implement a clinical consent authorization system:** it does not validate FHIR Consent resources, W3C decentralized identifiers, patient signatures, revocation state, or smart contracts.

## What works

- Three Python evaluation workers apply demonstration thresholds: primary metric **> 25**, secondary metric **> 12** or an explicit critical flag, and anomaly keywords in the descriptor. Thresholds are illustrative, **not clinically validated**.
- A supervisor produces a JSON dossier with alerts and an in-memory, chained HMAC-SHA256 audit entry.
- A FastAPI server exposes health, metrics, evaluation, mock chat, and audit-log retrieval endpoints. All endpoints except `/health` require a configured bearer token.
- A CLI supports a single evaluation, CSV batch processing, mock chat, and integrity checks. The separate `consent_ledger` module has an older rule set and command-line entry point.
- `web/index.html` runs an **offline, local JavaScript preview** of the three current worker rules, with JSON export. It does not call the Python API and does not generate an HMAC audit trail.

## Browser preview

Open `web/index.html` in a modern browser, enter **synthetic** identifiers and metrics, select **Evaluate locally**, and optionally **Export JSON**. The browser does not send data to a server. GitHub Pages publishes this static preview through `.github/workflows/pages.yml`.

The preview is not a production clinical tool. It deliberately labels its output `LOCAL_RULES_PREVIEW`.

## Install and run

Requires Python 3.9 or later.

```bash
git clone https://github.com/abusuraihsakhri/decentralized-clinical-consent-agent.git
cd decentralized-clinical-consent-agent
python -m pip install -e ".[test]"
python cli.py audit --task-id DEMO-001 --target SYNTH-001 --primary 28.5 --secondary 14.2 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python -m pytest -q
```

Boolean CSV values for `is_critical_flag` accept `true/false`, `1/0`, `yes/no`, or `y/n` (case-insensitive); ambiguous values are rejected. `verify-audit` checks only the **current process's** in-memory audit chain; the CLI does not persist audit logs between invocations.

The older module can be used with `python consent_ledger_app.py audit` and `python consent_ledger_app.py batch -i sample.csv`. Its numerical thresholds are different.

## Authenticated REST API

Set **both** environment variables before starting the server:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export API_AUTH_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
python cli.py serve --host 127.0.0.1 --port 8000
```

```bash
curl http://127.0.0.1:8000/health
curl -H "Authorization: Bearer $API_AUTH_TOKEN" http://127.0.0.1:8000/metrics
curl -H "Authorization: Bearer $API_AUTH_TOKEN" -H "Content-Type: application/json" \
  -d '{"task_id":"DEMO-001","target_identifier":"SYNTH-001","primary_metric":28.5,"secondary_metric":14.2,"status_descriptor":"NOMINAL","is_critical_flag":false}' \
  http://127.0.0.1:8000/api/audit
```

Interactive API docs: `http://127.0.0.1:8000/docs`. The supported endpoints are `GET /health`, `GET /metrics`, `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`.

Docker uses the same environment variables:

```bash
docker compose up --build
```

Compose refuses to start without both variables; never commit their values. Expose the server only behind HTTPS, authentication, and appropriate operational access controls.

## Security and scope limitations

**Do not enter or transmit real patient data.** The server uses pattern-based identifier detection, not reliable PHI detection, de-identification, HIPAA compliance, or anonymization. The audit ledger and evaluation dossiers are stored **in memory** and are not durable, replicated, or blockchain-backed. The audit key must remain stable to verify logs within an application session; no persistent ledger is provided.

The `/api/chat` path uses a deterministic mock responder, not an external LLM or validated clinical expert system. Descriptive references to CAP, CLSI, FHIR, DID, and other standards do **not** establish standards conformance. The static preview and Python evaluator are independent implementations; server-side validation and HMAC controls do not run in the browser.

## Development and checks

```bash
python -m compileall -q agents consent_ledger cli.py simulator.py enrichment.py
python -m pytest -q
python simulator.py 100
```

CI installs the project on Python 3.9–3.12, runs tests, and checks the browser's inline JavaScript syntax. The implementation uses Python, Pydantic, FastAPI, and plain HTML/CSS/JavaScript; no runtime browser-Python dependency is needed.

## License

MIT. See [LICENSE](LICENSE).
