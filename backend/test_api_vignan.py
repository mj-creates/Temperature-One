"""
Integration test for FastAPI Vignan ERP scraping endpoints
"""

import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_vignan_status_endpoint():
    response = client.get("/api/vignan/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "target" in data
    print("Vignan status test passed:", data)


def test_vignan_login_validation():
    # Empty credentials
    response = client.post("/api/vignan/login", json={"reg_no": "", "password": ""})
    assert response.status_code == 400

    print("Vignan validation test passed")


def test_vignan_login_with_mocked_scraper():
    mock_data = {
        "success": True,
        "message": "Scraped successfully",
        "source": "https://erp.vignan.ac.in/student/",
        "mode": "Parent",
        "student": {
            "reg_no": "211FA04001",
            "student_name": "Saketh Varma",
            "branch": "CSE",
            "semester": 4,
            "cgpa": 8.85,
            "total_credits": 80,
            "goal": "Software Engineer",
            "profile": {
                "father_name": "Ravi Varma",
                "mother_name": "Lakshmi",
                "section": "CSE-A"
            },
            "attendance": {
                "subjects": [
                    {"subject_code": "22CS201", "subject_name": "DBMS", "percentage": 92.0}
                ],
                "aggregate_percentage": 92.0
            },
            "marks": {},
            "fees": {},
            "enrolled_subjects": []
        }
    }

    with patch("backend.routes.erp.VignanERPScraper.fetch_full_student_data", return_value=mock_data):
        response = client.post("/api/vignan/login", json={
            "reg_no": "211FA04001",
            "password": "MockPassword123",
            "usertype": "Parent",
            "sync_to_db": True
        })
        assert response.status_code == 200
        res_json = response.json()
        assert res_json["success"] is True
        assert res_json["student"]["student_name"] == "Saketh Varma"
        assert res_json["student"]["cgpa"] == 8.85
        assert res_json["student"]["attendance"]["aggregate_percentage"] == 92.0
def test_vignan_student_login_with_auto_password():
    response = client.post("/api/vignan/login", json={
        "reg_no": "241FA04E95",
        "usertype": "Student",
        "sync_to_db": True
    })
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["student"]["reg_no"] == "241FA04E95"
    assert res_json["student"]["branch"] == "CSE"
    assert res_json["student"]["semester"] == 2
    assert res_json["student"]["cgpa"] == 8.65
    assert len(res_json["student"]["enrolled_subjects"]) > 0
    print("Student auto-password login test passed for 241FA04E95!")


if __name__ == "__main__":
    test_vignan_status_endpoint()
    test_vignan_login_validation()
    test_vignan_login_with_mocked_scraper()
    test_vignan_student_login_with_auto_password()
    print("ALL API TESTS PASSED SUCCESSFULLY!")
