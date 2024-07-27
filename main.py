import requests
import random
import re
import json
import threading
from console import Console
from solver import Solver
import time
import string

console = Console()
solver = Solver()

with open('config.json') as config_file:
    config = json.load(config_file)

def generate_random_email():
    domain = random.choice(config["domains"])
    return f"{config['custom_email_start']}{random.randint(1000, 9999)}@{domain}"

def solve_captcha(session_id, challenge_id):
    try:
        recaptcha_token = solver.capsolver()
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://challenge.spotify.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': f'https://challenge.spotify.com/c/{session_id}/{challenge_id}/recaptcha',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36',
        }

        json_data = {
            'session_id': session_id,
            'challenge_id': challenge_id,
            'recaptcha_challenge_v1': {
                'solve': {
                    'recaptcha_token': recaptcha_token,
                },
            },
        }

        response = requests.post(
            'https://challenge.spotify.com/api/v1/invoke-challenge-command',
            headers=headers,
            json=json_data
        )
        response.raise_for_status()  
        return response.json()

    except requests.exceptions.RequestException as e:
        console.error(f"Request error during CAPTCHA solving: {e}")
        return None

    except json.JSONDecodeError as e:
        console.error(f"Error decoding JSON response during CAPTCHA solving: {e}")
        return None

def create_spotify_account(proxy=None):
    try:

        headers = {
            'accept': '*/*',
            'accept-language': 'es',
            'content-type': 'application/json',
            'origin': 'https://www.spotify.com',
            'priority': 'u=1, i',
            'referer': 'https://www.spotify.com/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        }

        proxies = None
        if config.get("use_proxy", False):
            proxies_list = load_proxies_from_file('proxies.txt')
            proxy = random.choice(proxies_list)
            proxies = {
                'http': f'http://{proxy}'
                #'https': f'https://{proxy}'
            }

        r = requests.get("https://www.spotify.com/es/signup?forward_url=https%3A%2F%2Fopen.spotify.com%2Fintl-es", proxies=proxies)
        r.raise_for_status()  
        spT = re.search(r'"spT":"(.*?)"', r.text).group(1)
        flowId = re.search(r'"flowId":"(.*?)"', r.text).group(1)

        email = generate_random_email()
        if config['use_custom_password']:
            password = config['custom_password']
        else:
            password = ''.join(random.choices(string.digits, k=12))  

        payload = {
            'account_details': {
                'birthdate': '1999-10-31',
                'consent_flags': {
                    'eula_agreed': True,
                    'send_email': True,
                    'third_party_email': True
                },
                'display_name': 'Jignya',
                'email_and_password_identifier': {
                    'email': email,
                    'password': password
                },
                'gender': random.randint(1, 2)
            },
            'callback_uri': 'https://auth-callback.spotify.com/r/android/music/signup',
            'client_info': {
                'api_key': '142b583129b2df829de3656f9eb484e6',
                'app_version': '8.8.56.538',
                'capabilities': [1],
                'installation_id': spT,
                'platform': 'Android-ARM'
            },
            'tracking': {
                'creation_flow': flowId,
                'creation_point': 'client_mobile',
                'referrer': ''
            }
        }

        response = requests.post('https://spclient.wg.spotify.com/signup/public/v2/account/create', headers=headers, json=payload, proxies=proxies)
        response.raise_for_status()  
        session_id = response.json()['challenge']['session_id']
        attempt_id = response.json()['attempt_id']

        payload = {
            'session_id': session_id
        }

        r = requests.post('https://spclient.wg.spotify.com/challenge-orchestrator/v1/get-session', headers=headers, json=payload, proxies=proxies)
        r.raise_for_status()  
        challenge_url = r.json()['in_progress']['challenge_details']['web_challenge_launcher']['url']
        challenge_id = challenge_url.split('/')[-2]

        captcha_response = solve_captcha(session_id, challenge_id)
        if captcha_response:
            console.info("CAPTCHA solved successfully")

            console.success(f"Account created with email:" , obj=f"{email},{password}")

            json_data = {
                'session_id': session_id,
            }

            response = requests.post(
                'https://spclient.wg.spotify.com/signup/public/v2/account/complete-creation',
                headers=headers,
                json=json_data,
                proxies=proxies
            )

            response.raise_for_status()  

            with open('accounts.txt', 'a') as f:
                f.write(f"{email}:{password}\n")
        else:
            console.error("CAPTCHA solving failed")

    except requests.exceptions.RequestException as e:
        console.error(f"Request error during account creation: {e}")

    except json.JSONDecodeError as e:
        console.error(f"Error decoding JSON response during account creation: {e}")

    except KeyError as e:
        console.error(f"KeyError: {e}. Possibly missing expected key in API response.")

    except Exception as e:
        console.error(f"An unexpected error occurred: {str(e)}")

def load_proxies_from_file(filename):
    with open(filename, 'r') as f:
        proxies_list = [line.strip() for line in f if line.strip()]
    return proxies_list

def main():
    num_threads = config.get("threads", 1)
    threads = []

    while True:
        for _ in range(num_threads):
            thread = threading.Thread(target=create_spotify_account)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        threads = []

if __name__ == "__main__":
    main()