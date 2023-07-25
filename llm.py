import os
from typing import List
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def wsd(sent: str, word: str, definitions: List[str], model='chatgpt') -> int:
    prompt = get_wsd_prompt(sent, word, definitions)
    if model == 'chatgpt':
        predicted_def_idx = get_completion(prompt)
    else:
        raise ValueError(f'Unknown model: {model}')

    return int(predicted_def_idx)


def get_wsd_prompt(sent: str, word: str, definitions: List[str]) -> str:
    formatted_definitions = ''.join([f'{i}. {d}\n' for i, d in enumerate(definitions)])
    prompt = f'''
Which definition of "{word}" fits the following sentence best?

Sentence: "{sent}"

Definitions of {word}:
{formatted_definitions}

Answer with the number of the definition in this format: "1".
If you think the definition is not in the list, answer with "-1".
The answer should contain a number only and nothing else.

    '''
    print(prompt)
    return prompt


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    message = response.choices[0].message["content"]  # type: ignore
    return message.strip()


if __name__ == '__main__':
    from utilities import get_all_defs, predict_def
    word = 'observe'
    sentence = 'Flag day is observed on June 14 and commemorates the adoption of the Stars and Stripes as the official flag of the United States.'
    definitions = get_all_defs(word)

    predicted_def_idx = wsd(sentence, word, definitions)
    print(predicted_def_idx)
    if predicted_def_idx < len(definitions):
        print(definitions[predicted_def_idx])
    else:
        print('error definition')

    print(predict_def(sentence, word, mode='simple_lesk'))
