import requests
import json

# Login
login = requests.post("http://127.0.0.1:8000/auth/login", json={
    "email": "test@securescan.com",
    "password": "test123"
})
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Login successful.")

# Scan the forged document
with open("fake_document.pdf", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/scan/upload",
        headers=headers,
        files={"file": ("fake_document.pdf", f, "application/pdf")}
    )

result = response.json()
scan_id = result["scan_id"]
print(f"Scan complete. Verdict: {result['risk_verdict']}")
print(f"Scan ID: {scan_id}")

# Download the report
report_response = requests.get(
    f"http://127.0.0.1:8000/scan/{scan_id}/report",
    headers=headers
)

if report_response.status_code == 200:
    with open("forensic_report.pdf", "wb") as f:
        f.write(report_response.content)
    print("Report downloaded successfully — check forensic_report.pdf in your backend folder!")
else:
    print(f"Report error: {report_response.text}")