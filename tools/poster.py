import requests

def make():
    r = requests.get(
        ''
    )
    print(r.status_code)
    print(r.text)
    return r