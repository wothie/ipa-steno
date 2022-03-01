from vowels_and_consonants import vowels, consonants, diphthongs, triphthongs
from eng_stems_to_ipa_dict import stems, compounds
import sys


def replace_clusters(word):
    # Try triphthongs first
    # Just bruteforce it, since I don't have a clever way to find true diphthongs
    for triphthong, simple in triphthongs.items():
        word = word.replace(triphthong, simple)

    for diphthong, simple in diphthongs.items():
        word = word.replace(diphthong, simple)

    return word


def replace(c):
    if c == 'ˈ':
        return ''
    elif c == 'ˌ':
        return ''
    elif c in vowels:
        return vowels[c]
    elif c in consonants:
        return consonants[c]
    else:
        return c


if __name__=='__main__':
    out_file = open('eng_to_simp_ipa_dict.py', 'w')

    out_file.write('stems = {\n')
    for english, ipa in stems.items():
        ipa = replace_clusters(ipa)
        ipa = ''.join(map(replace, ipa))
        out_file.write('{}: {},\n'.format(repr(english), repr(ipa)))
    out_file.write('}\n')
    out_file.write('compounds = {\n')
    for english, ipa_list in compounds.items():
        result = []
        for english_part, ipa_part in ipa_list:
            ipa_part = replace_clusters(ipa_part)
            ipa_part = ''.join(map(replace, ipa_part))
            result += [(english_part, ipa_part)]
        out_file.write('{}: {},\n'.format(repr(english), repr(result)))
    out_file.write('}')

    out_file.close()
