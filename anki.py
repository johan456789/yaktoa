import genanki
from template import front_template, back_template, style_template


def add_notes(deck, model, notes):
    def note_constructor(fields):
        # Note
        return genanki.Note(
            model=my_model,
            fields=fields
        )
    for note in notes:
        my_note = note_constructor(note)
        deck.add_note(my_note)


def save_apkg(deck, filename):
    genanki.Package(deck).write_to_file(filename)


# Model (Note type)
my_model = genanki.Model(
    1261022550,
    'Basic (lang)',
    fields=[
        {'name': 'Expression'},
        {'name': 'IPA'},
        {'name': 'Audio'},
        {'name': 'Definition'},
        {'name': 'Image'},
        {'name': 'Collocation'},
        {'name': 'Example sentence'},
        {'name': 'Source'}
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': front_template,
            'afmt': back_template,
        },
    ],
    css=style_template
)

# Deck
my_deck = genanki.Deck(
    1547962859,
    'English🇺🇸::Kindle'
)

if __name__ == "__main__":
    notes = [
        ['expr_test1', 'no_ipa', 'no_audio',
            'no_def', 'no_image', 'no_collocation', 'no_example', 'no_source'],
        ['expr_test2', 'no_ipa', 'no_audio',
            'no_def', 'no_image', 'no_collocation', 'no_example', 'no_source'],
        ['expr_test3', 'no_ipa', 'no_audio',
            'no_def', 'no_image', 'no_collocation', 'no_example', 'no_source']
    ]

    add_notes(my_deck, my_model, notes)
    save_apkg(my_deck, 'output.apkg')
