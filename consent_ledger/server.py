"""
FastAPI REST API Server for ConsentLedger: Smart Contract Dynamic Patient Data Use Authorization Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import ConsentLedgerCoordinator
from agents.auth import require_api_token
from agents.base import SecurityException

coordinator = ConsentLedgerCoordinator()


def create_app():
    try:
        from fastapi import Depends, FastAPI, HTTPException
        from pydantic import BaseModel

        app = FastAPI(
            title="ConsentLedger: Smart Contract Dynamic Patient Data Use Authorization Agent",
            description="Evaluates patient granular consent directives (IRB protocol ID, data category, commercial vs non-profit) and verifies cryptographic signatures.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = 28.5
            secondary_metric: float = 14.2
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = {}

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "decentralized-clinical-consent-agent", "domain": "Privacy-Preserving Federated Healthcare & FHE", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit", dependencies=[Depends(require_api_token)])
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            try:
                return coordinator.process(payload)
            except SecurityException:
                raise HTTPException(status_code=422, detail="Input contains a prohibited identifier") from None

        @app.post("/api/chat", dependencies=[Depends(require_api_token)])
        def api_chat(req: ChatRequest):
            try:
                return {"response": coordinator.query_supervisory_chat(req.query)}
            except SecurityException:
                raise HTTPException(status_code=422, detail="Input contains a prohibited identifier") from None

        return app
    except ImportError:
        return None
