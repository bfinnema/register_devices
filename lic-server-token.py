import requests
import urllib3
import json
import sys

urllib3.disable_warnings()

client_id = "CMWk9L0mJ6Ynn8SwEnjd32-f_IqlNXWczjV6nC74ve7tFR--1c0LW8qp18N5_y1G"
client_secret = "7vtLXBnNzDXJ7wu5j9YsmV0cb24YEBKoZFvVihrbbt7yt677fAfZuwsUrKOi8Lvv"
host = "10.101.1.107"
port = "8443"
smartAccountName = "InternalTestDemoAccount9.cisco.com"
virtualAccountName = "Default"
accessCodeOk = True

print("********** GET AN ACCESS_TOKEN *********")
url = f'https://{host}:{port}/oauth/token'
print("url: {}".format(url))

payload = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}
headers = {
  'Content-Type': 'application/json'
}

try:
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload), verify = False)
    status_code = response.status_code
    print(f'status_code: {status_code}')
    if (status_code == 200):
        jsonResponse = response.json()
        print("Entire JSON response")
        print(jsonResponse)
        access_token = jsonResponse["access_token"]
        print("access_token: ", access_token)
    else:
        print(f'Something went wrong: {status_code}')
        accessCodeOk = False
except requests.exceptions.HTTPError as err:
    print ("Error in connection --> "+str(err))
    accessCodeOk = False
    sys.exit()

print("*******************")
print("********** GET ALL VALID EXISTING TOKENS *********")
print("*******************")

if (accessCodeOk):
    # url = "https://10.101.1.107:8443/api/v1/accounts/CISCO%20Danish%20LAB/virtual-accounts/Default/tokens"
    url = f'https://{host}:{port}/api/v1/accounts/{smartAccountName}/virtual-accounts/{virtualAccountName}/tokens'
    print(f"url: {url}")

    payload = {}
    headers = {
    'Authorization': 'Bearer '+access_token
    }

    try:
        response = requests.request("GET", url, headers=headers, data = payload, verify = False)
        status_code = response.status_code
        print(f'status_code: {status_code}')
        if (status_code == 200):
            jsonResponse = response.json()
            print("Entire JSON response")
            print(jsonResponse)
            print("Length of Token List: ", len(jsonResponse["tokens"]))
            numTokens = len(jsonResponse["tokens"])
            if numTokens>0:
                register_token = jsonResponse["tokens"][0]["token"]
                print("First token: ", register_token)
                regTokenOK = True
            else:
                regTokenOK = False
        else:
            print(f'Something went wrong: {status_code}')
            regTokenOK = False
    except requests.exceptions.HTTPError as err:
        print ("Error in connection --> "+str(err))
        regTokenOK = False
        sys.exit()

print("*******************")
print("********** GENERATE A NEW TOKEN *********")
print("*******************")

if (regTokenOK == False):
    # url = "https://10.101.1.107:8443/api/v1/accounts/CISCO%20Danish%20LAB/virtual-accounts/Default/tokens"
    url = f'https://{host}:{port}/api/v1/accounts/{smartAccountName}/virtual-accounts/{virtualAccountName}/tokens'
    print("url: " ,url)

    payload = {
        "expiresAfterDays": 1,
        "description": "Test VA Creation",
        "exportControlled": "Allowed"
    }

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+access_token
    }

    try:
        response = requests.request("POST", url, headers=headers, data = json.dumps(payload), verify = False)
        status_code = response.status_code
        print(f'status_code: {status_code}')
        if (status_code == 200):
            jsonResponse = response.json()
            print("Entire JSON response")
            print(jsonResponse)
            register_token = jsonResponse["tokenInfo"]["token"]
            print("Token: ", register_token)
            print("*******************")
        else:
            print(f'Something went wrong: {status_code}')
            accessCodeOk = False
    except requests.exceptions.HTTPError as err:
        print ("Error in connection --> "+str(err))
        regTokenOK = False
        sys.exit()
    finally:
        if response : response.close()
