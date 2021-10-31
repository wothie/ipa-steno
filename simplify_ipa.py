from vowels_and_consonants import vowels, consonants, diphthongs, triphthongs
from eng_stems_to_ipa_dict import eng_stems_to_ipa_dict
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

    out_file.write('eng_to_simp_ipa_dict = {\n')
    for english, ipa_list in eng_stems_to_ipa_dict.items():
        result = []
        for ipa in ipa_list:
            ipa = replace_clusters(ipa)
            ipa = ''.join(map(replace, ipa))
            result += [ipa]
        out_file.write('\"{}\": {},\n'.format(english, result))
    out_file.write('}')

    out_file.close()
