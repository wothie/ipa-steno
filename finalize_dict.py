from counted_english import counted_english
from eng_to_notation_dict import eng_to_notation_dict

if __name__=='__main__':
    result = {}
    # Save those were 4 levels of disambiguation didn't suffice
    rejected = {}

    out_file = open('notation_to_eng_dict.py', 'w')
    out_file.write('notation_to_eng_dict = {\n')
    for english, number in counted_english:
        notation = eng_to_notation_dict.get(english, '')
        if not notation:
            continue
        if notation not in result:
            out_file.write('"{}": "{}",\n'.format(notation, english))
            result[notation] = english
            continue
        # notation in result. Try disambiguation
        for disambiguation in '234n':
            if disambiguation == 'n':
                # We have exhausted out disambiguations
                rejected[notation] = english
            elif notation + disambiguation not in result:
                out_file.write('"{}": "{}",\n'.format(notation + disambiguation, english))
                result[notation + disambiguation] = english
                break
    out_file.write('}\n')
    # Now write the rejected ones
    out_file.write('rejected = {\n')
    for notation, english in rejected.items():
        out_file.write('{}: {},\n'.format(repr(notation), repr(english)))
    out_file.write('}')
