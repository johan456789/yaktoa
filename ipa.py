import sys
import requests
import eng_to_ipa
import os
from dotenv import load_dotenv
from utilities import call_mw_api

load_dotenv()
app_key = os.getenv('MERRIAM_WEBSTER_API_KEY')


def get_ipa_from_api(word):
    if not app_key:
        return ''
    try:
        res_json = call_mw_api(word)
        ret = f'us[{res_json[0]["hwi"]["prs"][0]["ipa"]}]'  # API Doc: 3.2 IPA AND WORD-OF-THE-DAY PRONUNCIATIONS
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
