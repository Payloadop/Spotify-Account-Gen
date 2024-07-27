import requests
import time
import json

class Solver:
    def __init__(self):
        self.load_config()

    def load_config(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)

    def capsolver(self):
        captcha_key = self.config.get('captchakey', '')  # Updated to match your config.json key
        if not captcha_key:
            raise ValueError("CAPTCHA key not found in config.json")

        task_payload = {
            "clientKey": captcha_key,
            "appId": "C10FB33E-8CED-4F6D-990C-356E42F5E318",
            "task": {
                "type": "ReCaptchaV2EnterpriseTaskProxyLess",
                "websiteURL": "https://challenge.spotify.com",
                "websiteKey": "6LeO36obAAAAALSBZrY6RYM1hcAY7RLvpDDcJLy3",
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            }
        }

        r1 = requests.post("https://api.capsolver.com/createTask", json=task_payload)
        #print(r1.text)
        if r1.status_code == 200:
            task_id = r1.json()["taskId"]
        else:
            raise RuntimeError(f"Failed to create CAPTCHA solving task: Status Code {r1.status_code}")

        solution_payload = {
            "clientKey": captcha_key,
            "taskId": task_id
        }

        while True:
            r2 = requests.post("https://api.capsolver.com/getTaskResult", json=solution_payload)
            #print(r2.text)
            if r2.status_code == 200:
                result_json = r2.json()
                if "ready" in result_json.get("status", "").lower():
                    g_recaptcha_response = result_json.get("solution", {}).get("gRecaptchaResponse", "")
                    if g_recaptcha_response:
                        return g_recaptcha_response
                    else:
                        raise RuntimeError("CAPTCHA solution not found in response")
                elif "processing" in result_json.get("status", "").lower():
                    time.sleep(1)
                    continue
                else:
                    error_message = result_json.get("error", {}).get("errorDetails", {}).get("title", "Unknown error")
                    raise RuntimeError(f"Failed to solve CAPTCHA: {error_message}")
            else:
                raise RuntimeError(f"Failed to get CAPTCHA solving result: Status Code {r2.status_code}")
