# yaktoa
### Yet Another Kindle to Anki 

This program generates `.apkg` deck directly from `vocab.db` located in your Kindle device. English support only.

![demo_screenshot](https://i.imgur.com/ZzWgKVN.jpg)

## Features
- Definitions are automatically filled in with (maybe) correct sense

  The word sense disambiguation (WSD) is powered by [pywsd](https://github.com/alvations/pywsd) and [WordNet](https://wordnet.princeton.edu/).
  Though WSD is not perfect, it is good enough in my opinion and you can just edit the file when reviewing if you see an incorrect definition.

- Manual mode

  You can use manual mode and select the correct word sense one by one if you want absolute accuracy.

- IPA (en-us) are automatically added

  This is powered mostly by [English-to-IPA](https://github.com/mphilli/English-to-IPA), and [Oxford Dictionaries API](https://developer.oxforddictionaries.com/) as well. You have to provide your own API key (it's free).

- Source book of the word is added to the card

  So you can recall where did you see the word. It is currently not used in the card template, edit it as you like.

## Installation

1. Clone this project

    ```
    git clone https://github.com/johan456789/yaktoa.git
    ```
    
2. Install dependencies

    ````
    pip install -r requirements.txt
    ````

3. Copy `/Volumes/Kindle/system/vocabulary/vocab.db` to `yaktoa`.

4. Get a INTRODUCTORY [Oxford Dictionaries API](https://developer.oxforddictionaries.com/), use your credentials and edit `cred.py` accordingly.
   
   ![api](https://user-images.githubusercontent.com/14802181/168453805-57a2b31c-49fe-4694-8626-37ec335bad57.png)


## Usage

```
usage: python main.py [-h] [-i INPUT] [-o OUTPUT] [--no_ipa] [-p] [-m]
optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input filename
  -o OUTPUT, --output OUTPUT
                        Output filename
  --no_ipa              Leave IPA field empty
  -p, --print           Print first 5 vocabularies
  -m, --manual          Manually select definition
```

### Auto mode (default)

1. Run script and type the index of the book interested.

    ```
    python main.py -i vocab.db -o output.apkg
    ```

    ![screenshot](https://i.imgur.com/b24cDMk.jpg)

2. Wait and voilà! The deck is saved as `output.apkg`.

    The free API plan has some limitations and I have to sleep for 2 seconds for another request, so it takes some time.

### Manual mode

Run script with `-m` or `--manual` tag.

```
python main.py -i vocab.db -o output.apkg -m
```

1. Type the number of the book you want:

    ![screenshot](https://i.imgur.com/b24cDMk.jpg)

2. Select correct word senses (the green one is what `pywsd` predicts):

    - Type the number with correct word sense and press enter:

    ![](https://i.imgur.com/iZcBQ1c.jpg)

    - Simply press enter if the predicted sense is correct:

    ![](https://i.imgur.com/6HpMYhc.jpg)
  
    Lower left numbers (2/14) tell you the current progress. There are a total of 14 vocabularies and it's the 2nd one.

3. Wait for IPA queries and it's done!

## Credits

Without them this project would have been much harder.

[genanki](https://github.com/kerrickstaley/genanki), [pywsd](https://github.com/alvations/pywsd), [English-to-IPA](https://github.com/mphilli/English-to-IPA)
[WordNet](https://wordnet.princeton.edu/), [Oxford Dictionaries](https://developer.oxforddictionaries.com/)
