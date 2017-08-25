from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud.language.syntax import PartOfSpeech
from beautifultable import BeautifulTable

def process(text):
    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    return client.analyze_syntax(document).tokens

def render_tokens(tokens):

    def align(content, part_of_speech):
        return [ content, part_of_speech ]

    def parse(token):
        pos_tag = ('UNKNOWN', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM',
                'PRON', 'PRT', 'PUNCT', 'VERB', 'X', 'AFFIX')

        verbose_tag = PartOfSpeech.reverse(pos_tag[ token.part_of_speech.tag ])

        return align(content=i.text.content, part_of_speech=verbose_tag)

    table = BeautifulTable()
    table.column_headers = align(content="content", part_of_speech="part of speech")

    for i in tokens: table.append_row(parse(i))
    print(table)

render_tokens(process("delete the first two words from the next line"))
