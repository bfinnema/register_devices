import requests
import urllib3
import json

urllib3.disable_warnings()
url = "https://10.101.1.107:8443/oauth/token"

payload = {
    "client_id": "efcce99b38b5ea24afff161a3940231e9fa8f8eaffe1e911edec82b0989a1517",
    "client_secret": "dd15ea6a89f7032e3bf117f4e48fb3a73d2234f57151be3100a036659e153aa7",
    "grant_type": "client_credentials"
}

headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data = json.dumps(payload), verify = False)
jsonResponse = response.json()
print("Entire JSON response")
print(jsonResponse)
access_token = jsonResponse["access_token"]
print("access_token: ", access_token)
print("*******************")

url = "https://10.101.1.107:8443/api/v1/accounts/CISCO%20Danish%20LAB/virtual-accounts/Default/tokens"

payload = {
    "expiresAfterDays": 1,
    "description": "Test VA Creation",
    "exportControlled": "Allowed"
}

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer '+access_token
}

response = requests.request("POST", url, headers=headers, data = json.dumps(payload), verify = False)
jsonResponse = response.json()
print("Entire JSON response")
print(jsonResponse)
token = jsonResponse["tokenInfo"]["token"]
print("Token: ", token)
print("*******************")
