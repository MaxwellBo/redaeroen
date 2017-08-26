from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud.language.syntax import PartOfSpeech
from beautifultable import BeautifulTable

from typing import Optional, Dict

POS_LOOKUP = {v: k for k, v in enums.PartOfSpeech.Tag.__dict__.items()}

# https://github.com/GoogleCloudPlatform/google-cloud-python/blob/master/language/google/cloud/gapic/language/v1/enums.py
LABEL_LOOKUP = {v: k for k, v in enums.DependencyEdge.Label.__dict__.items()}

def bind_tokens(tokens):
    def get_dependant(self, label) -> Optional[types.Token]:
        try:
            self.get_dependants()[label]
        except Exception as e:
            return None


    def get_dependants(self) -> Dict[enums.DependencyEdge.Label, types.Token]:
        return { i.dependency_edge.label: i for i in self.get_children() }

    types.Token.get_children = lambda self: [ i for i in tokens if i.get_parent() is self ]  
    types.Token.get_parent = lambda self: tokens[self.dependency_edge.head_token_index]
    types.Token.get_dependant = get_dependant

def process(text):
    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    tokens = client.analyze_syntax(document).tokens
    bind_tokens(tokens)
    return tokens

def get_token_by_pos(tokens, tag):
    return [ i for i in tokens if i.part_of_speech.tag == tag ]

def render_tokens(tokens):

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
                    , parent_content=token.get_parent().text.content
                    , children_content=str([i.text.content for i in token.get_children() ])
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

def to_ir(tokens):
    verb = get_token_by_pos(tokens, enums.PartOfSpeech.Tag.VERB)[0]
    prep = verb.get_dependant(enums.DependencyEdge.Label.PREP)

    return [ verb, prep ]

if __name__ == "__main__":
    # render_tokens(process("go down a line")) # j
    # render_tokens(process("go to the next line"))  # j
    # render_tokens(process("go down one line")) # j
    # render_tokens(process("go down two lines")) # 2j

    # render_tokens(process("go to line 0")) # :0

    # tokens = process("go to the first line") # gg
    # render_tokens(process("go to the start of the file")) # gg
    # render_tokens(process("go to the last line")) # G
    # render_tokens(process("go to the end of the file")) # G


    # render_tokens(process("go to the start of the line")) # $
    # render_tokens(process("go to the first word of the line")) # ^
    # render_tokens(process("go the the third word of the line")) # ^2w (careful of the number)

    # render_tokens(process("go to the opening square bracket")) # f[
    # render_tokens(process("go to the closing curly brace")) # f}
    # tokens = process("select the next two words, and delete them")

    tokens = process("delete the first two words from the next line") # j 2dw

    # render_tokens(process("delete the next word")) # dw
    # render_tokens(process("delete the next two words")) # 2dw 

    # render_tokens(process("delete the current word")) # diw
    # render_tokens(process("delete in the current word")) # diw
    # render_tokens(process("delete around the current word")) # daw
    # render_tokens(process("delete in the current parentheses")) # di(

    # render_tokens(process("delete the current line")) # dd
    # render_tokens(process("delete the next two lines")) # j v j d
    # render_tokens(process("delete the last line")) # G dd

    # render_tokens(process("change the brackets surrounding the current word from square brackets to curly braces")) # cs[{
    # render_tokens(process("surround the current word with parentheses")) # ys(

    # render_tokens(process("comment out the current line")) # V gc


    render_tokens(tokens)
    print(to_ir(tokens))


