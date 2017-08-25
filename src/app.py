from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

def syntax_text(text):
    client = language.LanguageServiceClient()

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects syntax in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    tokens = client.analyze_syntax(document).tokens

    # part-of-speech tags from enums.PartOfSpeech.Tag
    pos_tag = ('UNKNOWN', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM',
               'PRON', 'PRT', 'PUNCT', 'VERB', 'X', 'AFFIX')

    for token in tokens:
        print(u'{}: {}'.format(pos_tag[token.part_of_speech.tag],
                               token.text.content))

syntax_text("Hello world!")
