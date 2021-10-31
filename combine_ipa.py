from eng_to_ipa_dict import eng_to_ipa_dict


def remove_number(english):
    position = english.find('(')
    position = position if position >= 0 else len(english)
    return english[:position]


if __name__=='__main__':
    result = {}
    for key, val in eng_to_ipa_dict.items():
        key = remove_number(key)
        if key in result:
            result[key].add(val)
        else:
            result[key] = {val}

    out_file = open('eng_to_ipa_dict.py', 'w')
    out_file.write('eng_to_ipa_dict = {\n')
    for key, val in result.items():
        out_file.write('\"{}\": {},\n'.format(key, list(val)))
    out_file.write('}')
