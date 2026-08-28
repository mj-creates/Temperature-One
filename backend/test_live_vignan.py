"""
Diagnostic script for Vignan ERP Portal live endpoints
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

# 1. Fetch initial cookies
try:
    r0 = session.get("https://erp.vignan.ac.in/student/signin.jsp", timeout=10)
    print("GET signin.jsp status:", r0.status_code)
    print("Initial cookies:", session.cookies.get_dict())
except Exception as e:
    print("Error fetching signin.jsp:", e)

# 2. Test login with dummy / test credentials
payload = {
    "user": "241FA04424",
    "pwd": "testpassword",
    "usertype": "Parent"
}

try:
    r1 = session.post("https://erp.vignan.ac.in/student/login1.jsp", data=payload, timeout=10, allow_redirects=True)
    print("POST login1.jsp status:", r1.status_code)
    print("Final URL:", r1.url)
    print("Cookies after login:", session.cookies.get_dict())
    print("Response snippet (first 500 chars):")
    print(r1.text[:500])
except Exception as e:
    print("Error during POST login1.jsp:", e)
