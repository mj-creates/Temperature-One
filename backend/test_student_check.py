"""
Direct diagnosis for student registration number 241FA04E95
"""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://erp.vignan.ac.in/student/signin.jsp",
})

# 1. Establish session
r0 = session.get("https://erp.vignan.ac.in/student/signin.jsp", timeout=10)
print("Initial signin.jsp:", r0.status_code)

# 2. Test Parent mode with dummy DOB / password
reg_no = "241FA04E95"

for mode in ["Parent", "Student"]:
    payload = {
        "user": reg_no,
        "pwd": "dummy_password_for_probe",
        "usertype": mode
    }
    r = session.post("https://erp.vignan.ac.in/student/login1.jsp", data=payload, timeout=10, allow_redirects=True)
    print(f"\n--- Testing mode: {mode} with {reg_no} ---")
    print("Status code:", r.status_code)
    print("Final URL:", r.url)
    print("Response text snippet:")
    print(r.text.strip()[:600])
