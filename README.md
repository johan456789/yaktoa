# yaktoa
### Yet Another Kindle to Anki 

This program generates `.apkg` deck directly from `vocab.db` located in your Kindle device. English support only.

![demo_screenshot](https://i.imgur.com/kgsoZZw.jpg)

## Features
- Definitions are automatically filled in with (probably) correct sense

  The word sense disambiguation (WSD) is powered by [pywsd](https://github.com/alvations/pywsd) and [WordNet](https://wordnet.princeton.edu/).
Though WSD is not perfect, it is good enough in my opinion and you can just edit the file when reviewing if you see an incorrect definition.

- IPA (en-us) are automatically added

  This is powered by [Oxford Dictionaries API](https://developer.oxforddictionaries.com/). 

- Source book of the word is added to the card

  So you can recall where did you see the word. It is currently not used in the card template, edit it as you like.

## Usage

1. Clone this project

    ```
    git clone https://github.com/johan456789/yaktoa.git
    ```
    
2. Install dependencies

    ````
    pip install -r requirements.txt
    ````

3. Copy `/Volumes/Kindle/system/vocabulary/vocab.db` to `yaktoa`.

4. Get a PROTOTYPE [Oxford Dictionaries API](https://developer.oxforddictionaries.com/), use your credentials and edit `cred.py` accordingly.

   ![prototype](https://i.imgur.com/yK8y4kx.jpg)

5. Run script and type the index of the book interested.

    ```
    python main.py
    ```

    ![screenshot](https://i.imgur.com/b24cDMk.jpg)

6. Wait and voilà! The deck is saved as `output.apkg`.

    The free API plan has some limitations and I have to sleep for 2 seconds for another request, so it takes some time.

## Credits

Without them this project would have been much harder.

[genanki](https://github.com/kerrickstaley/genanki), [pywsd](https://github.com/alvations/pywsd), 
[WordNet](https://wordnet.princeton.edu/), [Oxford Dictionaries](https://developer.oxforddictionaries.com/)
