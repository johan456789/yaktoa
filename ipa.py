import sys
import requests
import json
import time
from cred import app_key
import eng_to_ipa as ipa


def get_oed_ipa(word):
    try:    
        url = "https://dictionaryapi.com/api/v3/references/learners/json/{}?key={}".format(word.lower(), app_key)
        response = requests.get(url)
        if response.ok:
            resp_json = response.json()
        ret = resp_json[0]['hwi']['prs'][0]['ipa']       
        # time.sleep(2.1)  # limit utilization of Hits per minute: 30/60
    except:
        ret = ''

    return ret

def get_ipa(word):
    if ipa.isin_cmu(word):
        return f'us[{ipa.convert(word)}]'
    elif app_key:
            return get_oed_ipa(word)


if __name__ == "__main__":
    query = sys.argv[1]
    print(get_ipa(query))
