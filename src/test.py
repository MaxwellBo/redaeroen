from nlp import process, render_tokens, to_ir
from voicerec import voice_command_generator

for command in voice_command_generator('hey google'):
    tokens = process(command)

    render_tokens(tokens)

    print(to_ir(tokens))
