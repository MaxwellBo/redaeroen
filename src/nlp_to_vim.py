from nlp import process, print_table, get_token_by_pos
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
    tokens = process(string)

    # Render what was retrieved
    print_table(tokens)

    # Find the command's verb
    line_verbs = get_token_by_pos(tokens, enums.PartOfSpeech.Tag.VERB)
    candidate_verbs = [v for v in line_verbs if v.text.content.lower() in known_verbs]

    if len(candidate_verbs) == 0:
        print("ERROR: No relevant verbs found")
        return None

    verb = candidate_verbs[0]

    # Find out wha
    dep = get_token_by_pos(verb.get_children(), enums.PartOfSpeech.Tag.ADP)[0]
    dep_nouns = get_token_by_pos(dep.get_children(), enums.PartOfSpeech.Tag.NOUN)
    candidate_dep_nouns = [v for v in dep_nouns if v.text.content.lower() in known_nouns]
    if len(candidate_dep_nouns) == 0:
        print("ERROR: No dependant nouns relevant to" + verb.text.content + " ->" + dep.text.content + "found")
        return None
    
    dep_noun = candidate_dep_nouns[0]

    # Find the object associated with that verb
    line_nouns = get_token_by_pos(verb.get_children(), enums.PartOfSpeech.Tag.NOUN)
    candidate_nouns = [v for v in line_nouns if v.text.content.lower() in known_nouns]
    if len(candidate_nouns) == 0:
        print("ERROR: No nouns relevant to " + verb.text.content + "found")
        return None

    noun = candidate_nouns[0]

    # Find how many there are
    candidate_nums = get_token_by_pos(noun.get_children(), enums.PartOfSpeech.Tag.NUM)
    if len(candidate_nums) == 0:
        num = None
    else:
        num = candidate_nums[0]


    print("Action: " + verb.text.content)
    print("Dependant: " + dep_noun.text.content)
    print("Object: " + noun.text.content)
    print("Number of times: " + num.text.content if num is not None else "one")

# extract_command("go down a line")
extract_command("go to the first line")
# extract_command("Delete the last five words from the previous line")
# extract_command("Hey google, please delete the first five words from this line")