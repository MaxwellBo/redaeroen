from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud.language.syntax import PartOfSpeech
from beautifultable import BeautifulTable

POS_LOOKUP = {v: k for k, v in enums.PartOfSpeech.Tag.__dict__.items()}
LABEL_LOOKUP = {v: k for k, v in enums.DependencyEdge.Label.__dict__.items()}

def process(text):
    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    return client.analyze_syntax(document).tokens

def render_tokens(tokens):

    def align( content=""
             , begin=""
             , part_of_speech=""
             , parent_content=""
             , edge_index=""
             , edge_label=""
             , lemma=""
             ):
        return [ content
            #    , begin
               , part_of_speech
               , parent_content
            #    , edge_index
               , edge_label
               , lemma 
               ]

    def parse(token):
        verbose_tag = PartOfSpeech.reverse(POS_LOOKUP[ token.part_of_speech.tag ])

        parent = tokens[token.dependency_edge.head_token_index].text
        
        return align( content=token.text.content
                    , begin=token.text.begin_offset
                    , part_of_speech=verbose_tag
                    , edge_index=token.dependency_edge.head_token_index
                    , parent_content=parent.content
                    , edge_label=LABEL_LOOKUP[token.dependency_edge.label]
                    , lemma=token.lemma
                    , )

    table = BeautifulTable()
    table.column_headers = align( content="content" 
                                , begin="begin offset"
                                , part_of_speech="part of speech"
                                , parent_content="parent content"
                                , edge_index="edge index"
                                , edge_label="edge label"
                                , lemma="lemma"
                                )

    for i in tokens: table.append_row(parse(i))
    print(table)

render_tokens(process("delete the first two words from the next line"))
