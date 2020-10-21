import sys
import requests
import json
import time
from cred import app_id, app_key


def get_ipa(word, test=False):
    try:
        langs = ['en-us']  # 'en-gb' does not work

        spellings = []
        for lang in langs:
            url = "https://od-api.oxforddictionaries.com:443/api/v2/entries/" + lang + "/" + word.lower()
            reply_json = requests.get(url, headers={"app_id": app_id, "app_key": app_key}).json()

            reply_str = json.dumps(reply_json, indent=2)
            reply_dict = json.loads(reply_str)
            spellings.append(
                reply_dict['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][1]['phoneticSpelling']
            )

        # ret =  f'uk[{spellings[0]}] us[{spellings[1]}]'
        ret =  f'us[{spellings[0]}]'
        if not test:
            time.sleep(2.1)  # limit utilization of Hits per minute: 30/60
    except:
        ret = ''

    return ret

if __name__ == "__main__":
    query = sys.argv[1]
    print(get_ipa(query, test=True))
