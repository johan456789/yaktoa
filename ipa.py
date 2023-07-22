import sys
import requests
from cred import app_key
import eng_to_ipa


def get_ipa_from_api(word):
    if not app_key:
        return ''

    try:
        url = "https://dictionaryapi.com/api/v3/references/learners/json/{}?key={}".format(word.lower(), app_key)
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()
        res_json = response.json()
        ret = f'us[{res_json[0]["hwi"]["prs"][0]["ipa"]}]'  # API Doc: 3.2 IPA AND WORD-OF-THE-DAY PRONUNCIATIONS
        # time.sleep(2.1)  # limit utilization of Hits per minute: 30/60  # TODO: implement a rate limiter
    except requests.HTTPError:
        ret = ''
    except KeyError:
        # TODO: log the error with the word and the response
        ret = ''
    except TypeError:
        # TODO: log the error with the word and the response
        ret = ''

    return ret


def get_ipa(word):
    if eng_to_ipa.isin_cmu(word):
        return f'us[{eng_to_ipa.convert(word)}]'
    return get_ipa_from_api(word)


if __name__ == "__main__":
    query = sys.argv[1]
    print(get_ipa(query))
