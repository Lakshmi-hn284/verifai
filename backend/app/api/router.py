"""
VERIFAI - API Router Aggregation
Mounts all v1 sub-routers.
"""
from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    documents,
    credentials,
    graph,
    opportunities,
    eligibility,
    disclosures,
    career,
    audit
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(documents.router)
api_router.include_router(credentials.router)
api_router.include_router(graph.router)
api_router.include_router(opportunities.router)
api_router.include_router(eligibility.router)
api_router.include_router(disclosures.router)
api_router.include_router(career.router)
api_router.include_router(audit.router)
