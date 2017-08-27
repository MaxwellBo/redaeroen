from nlp import process, print_table, get_token_by_pos, expand_label, expand_pos
from voicerec import voice_command_generator

# GENERAL IDEA:
#   Example: Delete the first five words from the next line
#    1) Find a verb in the action verb lookup table
#    2) Find the subject the verb is acting upon
#           - there should be either:
#               a) an adposition ADP ('from', 'to') which can then be linked to the subject (e.g. 'line', 'paragraph')
#               b) an adverb ('up', 'down') which can be linked to the subject
#   3) The object the verb refers to
#           - E.g. 'word'
#   4) Direction:
#

from google.cloud.language import enums

known_verbs = [
    "delete",
    "yank",
    "select",
    "go"
]

known_nouns = [
    "word",
    "words",
    "line",
    "lines",
    "paragraph",
    "paragraphs"
]

def extract_command(string: str):
    l = enums.DependencyEdge.Label
    tokens = process(string)

    # Find the command's verb
    line_verbs = get_token_by_pos(tokens, enums.PartOfSpeech.Tag.VERB)
    candidate_verbs = [v for v in line_verbs if v.text.content.lower() in known_verbs]

    if len(candidate_verbs) == 0:
        print("ERROR: No relevant verbs found")
        return None

    verb = candidate_verbs[0]

    def get_possessive(token):
        x = token.get_dependant(l.PREP)
        y = x.get_dependant(l.POBJ)
        z = token.get_dependant(l.DOBJ)
        return y or x or z

    def get_num(token):
        x = token.get_dependant(l.AMOD)
        y = token.get_dependant(l.NUM)
        return y or x 

    pos = get_possessive(verb)

    print("NUMBER", get_num(pos).text.content)
    print("VERB", verb.text.content)
    print("TARGET", pos.text.content)


# extract_command("go down a line")
# extract_command("delete the next two words")
extract_command("delete in the current word")
# extract_command("go to the first line the file")
# extract_command("go to the first word of the line")
# extract_command("go to the first line")
# extract_command("Delete the last five words from the previous line")
# extract_command("Hey google, please delete the first five words from this line")