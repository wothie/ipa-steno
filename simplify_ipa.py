from vowels_and_consonants import vowels, consonants, diphthongs, triphthongs
from eng_composition import eng_composition
from counts import counts
from eng_to_ipa_dict import eng_to_ipa_dict
from affix_rules import prefixes, suffixes
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
    stems = {}
    compounds = {}
    prefix_ipas = {rule[0][0]: [] for rule in prefixes}
    suffix_ipas = {rule[0][0]: [] for rule in suffixes}
    for rule in prefixes:
        for english, ipa, _ in rule:
            prefix_ipas[english] += [ipa]
    for rule in suffixes:
        for english, ipa, _ in rule:
            suffix_ipas[english] += [ipa]

    eng_composition_sorted = dict(sorted(eng_composition, key=lambda x: counts[x[0]], reverse=True))

    for english, splits in eng_composition_sorted.items():
        # eng_composition_sorted will include some affixes
        for split in splits:
            for part in split:
                # eng_composition_sorted has affixes as well, so we assume that every stem is in one of them
                if part not in eng_to_ipa_dict and part not in prefix_ipas:
                    eng_to_ipa_dict[part] = suffix_ipas[part]
                elif part not in eng_to_ipa_dict and part not in suffix_ipas:
                    eng_to_ipa_dict[part] = prefix_ipas[part]

        for split in splits:
            result = [[]]
            for part in split:
                result = [subresult + [''.join(map(replace, replace_clusters(ipa)))]
                          for subresult in result for ipa in eng_to_ipa_dict[part]]

        if any([len(split) == 1 for split in result]):
            stems[english] = result
        else:
            compounds[english] = result
    out_file = open('eng_to_simp_ipa_dict.py', 'w')
    out_file.write('stems = {\n')
    for english, splits in stems.items():
        out_file.write('{}: {},\n'.format(repr(english), repr([split[0] for split in splits])))
    out_file.write('}\n')
    out_file.write('compounds = {\n')
    for english, splits in compounds.items():
        out_file.write('{}: {},\n'.format(repr(english), repr(splits)))
    out_file.write('}')

    out_file.close()
