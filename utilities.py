import os
import sys
from contextlib import contextmanager
from nltk.corpus import wordnet as wn
from colorama import Style, Fore
from tqdm import tqdm
tqdm.pandas()


@contextmanager
def silence_output(stdout=True, stderr=True):
    # Save the original stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        # Redirect stdout and stderr to a null device
        null_device = open(os.devnull, 'w')
        if stdout:
            sys.stdout = null_device
        if stderr:
            sys.stderr = null_device

        yield
    finally:
        # Restore stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def get_def(synset):
    if synset is None:
        return ''
    lexname_map = {
        'noun': 'n. ',
        'verb': 'v. ',
        'adj': 'adj. ',
        'adv': 'adv. '
    }
    definition = synset.definition()
    lexname = lexname_map[synset.lexname().split('.')[0]]
    return f'{lexname}{definition}'


def predict_def(sent, ambiguous):
    with silence_output():
        from pywsd.lesk import simple_lesk  # import here to avoid printing
    try:
        return simple_lesk(sent, ambiguous)
    except Exception as e:
        print(e)
        return None


def get_def_manual(vocabs, report_incorrect=False):
    incorrect_count = 0
    for vocab in vocabs.itertuples():
        synsets = wn.synsets(vocab.word)
        if len(synsets) == 1:
            vocabs.loc[vocab.Index, 'definition'] = get_def(synsets[0])
        elif len(synsets) == 0:
            vocabs.loc[vocab.Index, 'definition'] = ''
        else:
            word_r = f'{Fore.RED}{vocab.word}{Style.RESET_ALL}'
            print(f'What does {word_r} mean in this context?\n"{vocab.usage.replace(vocab.word, word_r)}"')
            synset_pred = predict_def(vocab.usage, vocab.stem)

            # print all definitions
            correct_idx = None
            for i, synset in enumerate(synsets):
                if synset == synset_pred:
                    correct_idx = i
                    print(Fore.GREEN, end='')
                print(f'{str(i).ljust(4)}{get_def(synset)}{Style.RESET_ALL}')

            user_input = input(f'({vocab.Index + 1}/{len(vocabs)}) Type number: ')
            if user_input == '':  # choose predicted definition
                vocabs.loc[vocab.Index, 'definition'] = get_def(synset_pred)
            else:
                idx = int(user_input)
                if idx != correct_idx:
                    incorrect_count += 1
                vocabs.loc[vocab.Index, 'definition'] = get_def(synsets[idx])
    if report_incorrect:
        print(f'WSD accuracy is {round(1 - incorrect_count / len(vocabs), 4) * 100}%')
    return vocabs


def get_def_auto(vocabs):
    vocabs['definition'] = vocabs[['stem', 'usage']].progress_apply(
        lambda x: get_def(predict_def(x['usage'], x['stem'])), axis=1
    )
    vocabs['usage'] = vocabs[['word', 'usage']].apply(
        lambda x: x['usage'].replace(x['word'], '<b><i>' + x['word'] + '</i></b>'), axis=1
    )
    return vocabs
