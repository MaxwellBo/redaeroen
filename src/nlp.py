import argparse
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud.language.syntax import PartOfSpeech
from beautifultable import BeautifulTable
import networkx as nx
import matplotlib.pyplot as plt
import subprocess
from voicerec import voice_recognition_generator

from typing import Optional, Dict


def expand_pos(x):
    POS_LOOKUP = {v: k for k, v in enums.PartOfSpeech.Tag.__dict__.items()}
    return POS_LOOKUP[x]

# https://github.com/GoogleCloudPlatform/google-cloud-python/blob/master/language/google/cloud/gapic/language/v1/enums.py
def expand_label(x):
    LABEL_LOOKUP = {v: k for k, v in enums.DependencyEdge.Label.__dict__.items()}
    return LABEL_LOOKUP[x]

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
            , part_of_speech
            , parent_content
            , edge_label
        #    , begin
            , children_content
        #    , edge_index
            ]

class Null(object):
    def __getattribute__(self, name):
        return lambda x: Null()

    def __nonzero__(self): 
        return False
    
    __bool__ = __nonzero__
            
def bind_tokens(tokens):
    def get_dependant(self, label) -> Optional[types.Token]:
        try:
            return self.get_dependants()[label]
        except Exception as e:
            return Null()

    def pretty(token):
        verbose_tag = PartOfSpeech.reverse(expand_pos(token.part_of_speech.tag))

        return align( content=token.text.content
                    , begin=token.text.begin_offset
                    , part_of_speech=verbose_tag
                    , parent_content=token.get_parent().text.content
                    , children_content=str([i.text.content for i in token.get_children() ])
                    , edge_label=expand_label(token.dependency_edge.label)
                    , lemma=token.lemma
                    , )

    def get_dependants(self) -> Dict[enums.DependencyEdge.Label, types.Token]:
        return { i.dependency_edge.label: i for i in self.get_children() }

    types.Token.get_children = lambda self: [ i for i in tokens if i.get_parent() is self ]  
    types.Token.get_parent = lambda self: tokens[self.dependency_edge.head_token_index]
    types.Token.get_dependant = get_dependant
    types.Token.get_dependants = get_dependants
    types.Token.pretty = pretty
    types.Token.__str__ = lambda self: str(self.pretty())

    for (i, v) in enumerate(tokens):
        v.text.begin_offset = i

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

def print_table(tokens):

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

    for i in tokens: table.append_row(i.pretty())
    print(table)


def print_tree(tokens):
    G = nx.DiGraph()

    root = [ i for i in tokens if enums.DependencyEdge.Label.ROOT in i.get_dependants() ][0]

    edge_map = {}
    label_map = {}

    for i in tokens:
        short_tag = expand_pos( i.part_of_speech.tag )
        label_map[i.text.begin_offset] =  f"{i.text.content}\n{short_tag}"
        for j in i.get_children():
            if i is not j:
                G.add_edge(i.text.begin_offset, j.text.begin_offset)
                edge_map[(i.text.begin_offset, j.text.begin_offset)] = expand_label(j.dependency_edge.label)


    depth_map = {}
    def recur(level, tok):
        depth_map[tok.text.begin_offset] = (tok.text.begin_offset, -level)
        list(map(lambda t: recur(level + 1, t), [ i for i in tok.get_children() if i is not tok ]))

    list(map(lambda t: recur(0, t), [ root ] ))
    
    # nx.draw_networkx(G, pos=depth_map)
    nx.draw_networkx_labels(G, pos=depth_map, font_color='w', font_size=8, labels=label_map)
    nx.draw_networkx_edges(G, pos=depth_map)
    nx.draw_networkx_edge_labels(G, pos=depth_map, edge_labels=edge_map, font_size=6)
    
    plt.axis('off')
    plt.savefig("g.png", transparent=True, dpi=150)

    subprocess.run(["imgcat", "g.png"])

def pretty_print_text(text, view="tree"):
    tokens = process(text)

    if view == "tree":
        print_tree(tokens)
    else:
        print_table(tokens)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extended Play: the CLI NLP tool')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--text', dest='text', default = "", type=str, nargs=1,
                    help='text to analyse')
    source.add_argument('--listen', dest='listen', action='store_true', default=False, help="use microphone (default: false)")

    view = parser.add_mutually_exclusive_group(required=False)
    view.add_argument('--table', dest='view', action='store_const', const="table", default=True, help="view as table (default: true)")
    view.add_argument('--tree', dest='view', action='store_const', const="tree", help="view as tree")
    
    args = parser.parse_args()

    if args.listen:
        print("Listening")
        for (text, _) in voice_recognition_generator():
            pretty_print_text(text, view=args.view)
    else:
        pretty_print_text(text=args.text[0], view=args.view)