from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud.language.syntax import PartOfSpeech
from beautifultable import BeautifulTable

POS_LOOKUP = {v: k for k, v in enums.PartOfSpeech.Tag.__dict__.items()}

# https://github.com/GoogleCloudPlatform/google-cloud-python/blob/master/language/google/cloud/gapic/language/v1/enums.py
LABEL_LOOKUP = {v: k for k, v in enums.DependencyEdge.Label.__dict__.items()}

def process(text):
    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    return client.analyze_syntax(document).tokens

def render_tokens(tokens):
    def get_children(token):
        return [ i for i in tokens if get_parent(i) is token ] 

    def get_parent(token):
        return tokens[token.dependency_edge.head_token_index]

    def align( content=""
             , begin=""
             , part_of_speech=""
             , parent_content=""
             , children_content=""
             , edge_index=""
             , edge_label=""
             , lemma=""
             ):
        return [ content
            #    , begin
               , part_of_speech
               , parent_content
               , children_content
            #    , edge_index
               , edge_label
               , lemma 
               ]

    def parse(token):
        verbose_tag = PartOfSpeech.reverse(POS_LOOKUP[ token.part_of_speech.tag ])

        return align( content=token.text.content
                    , begin=token.text.begin_offset
                    , part_of_speech=verbose_tag
                    , parent_content=get_parent(token).text.content
                    , children_content=str([i.text.content for i in get_children(token) ])
                    , edge_label=LABEL_LOOKUP[token.dependency_edge.label]
                    , lemma=token.lemma
                    , )

    table = BeautifulTable(max_width=120)
    table.column_headers = align( content="content" 
                                , begin="begin offset"
                                , part_of_speech="part of speech"
                                , parent_content="parent content"
                                , children_content="children content"
                                , edge_index="edge index"
                                , edge_label="edge label"
                                , lemma="lemma"
                                )

    for i in tokens: table.append_row(parse(i))
    print(table)

render_tokens(process("delete the first two words from the next line"))
