"""
External Courses Route
======================
Proxies Coursera's public catalog search API to avoid browser CORS restrictions.
Coursera's courses.v1 endpoint is publicly accessible (no OAuth required for reads).
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import logging

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger("external_courses")

router = APIRouter(prefix="/api/external-courses", tags=["External Courses"])

COURSERA_API = "https://api.coursera.org/api/courses.v1"

COURSERA_FIELDS = "name,slug,description,photoUrl,partnerIds"


@router.get(
    "/search",
    summary="Search Coursera courses by keyword",
    description="Proxies Coursera's public catalog API. No auth required. Returns real course data."
)
def search_coursera_courses(
    query: str = Query(..., description="Search keyword, e.g. 'machine learning', 'ethical hacking'"),
    limit: int = Query(default=5, ge=1, le=20, description="Number of results to return (max 20)")
):
    """
    Search Coursera's public catalog for courses matching the query.
    Proxied server-side to avoid CORS issues from the browser.
    """
    if not requests:
        raise HTTPException(status_code=500, detail="requests library not available")

    params = {
        "q": "search",
        "query": query,
        "fields": COURSERA_FIELDS,
        "limit": limit,
    }

    try:
        resp = requests.get(COURSERA_API, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Coursera API timed out")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Could not connect to Coursera API")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Coursera API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    elements = data.get("elements", [])

    courses = [
        {
            "title": c.get("name", ""),
            "slug": c.get("slug", ""),
            "url": f"https://www.coursera.org/learn/{c.get('slug', '')}",
            "description": (c.get("description") or "")[:200],
            "platform": "Coursera",
        }
        for c in elements
        if c.get("slug") and c.get("name")
    ]

    return {
        "query": query,
        "total_found": data.get("paging", {}).get("total", len(courses)),
        "courses": courses,
    }


@router.post(
    "/auto-enroll",
    summary="Legacy mock enrollment endpoint (kept for compatibility)"
)
def auto_enroll_student(req: dict):
    """Legacy endpoint — kept for backward compatibility."""
    skill = req.get("missing_skill", "the subject")
    return {
        "status": "success",
        "message": f"Search Coursera for '{skill}' to find relevant courses.",
        "platform": "Coursera",
    }
