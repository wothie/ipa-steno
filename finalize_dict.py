from eng_to_notation_dict import eng_to_notation_dict


def attach(word, number):
    return word + str(number) if number > 0 else word


def smallest_disambiguation(notation, dictionary):
    """
    computes the smallest number i for which notation+'i' is not in dictionary
    """
    i = 0
    while attach(notation, i) in dictionary:
        i = i+1
    return i


if __name__=='__main__':
    result = {}
    # Save those were 4 levels of disambiguation didn't suffice
    rejected = {}

    # For now use word length as preference
    for english, options in sorted(eng_to_notation_dict.items(), key=lambda x: len(x[0])):
        uniqueness = [smallest_disambiguation(option, result) for option in options]
        # Get index of smallest value, i.e. most unique notation
        notation, disambiguation = sorted(zip(options, uniqueness), key=lambda x: x[1])[0]
        if disambiguation > 3:
            rejected[attach(notation, disambiguation)] = english
        else:
            result[attach(notation, disambiguation)] = english

    out_file = open('notation_to_eng_dict.py', 'w')
    out_file.write('notation_to_eng_dict = {\n')
    for notation, english in result.items():
        out_file.write('{}: {},\n'.format(repr(notation), repr(english)))
    out_file.write('}\n')
    # Now write the rejected ones
    out_file.write('rejected = {\n')
    for notation, english in rejected.items():
        out_file.write('{}: {},\n'.format(repr(notation), repr(english)))
    out_file.write('}')
