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

    # tokens = process("delete the first two words from the next line") # j 2dw

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

