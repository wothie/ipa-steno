from counts import counts
from notation_to_eng_dict import notation_to_eng_dict
from vowels_and_consonants import vowels, consonants, diphthong_to_vowel
"""
Assuming a regular qwerty layout for iris
+---------------------------------------+                 +---------------------------------------+
| Esc   | 1  | 2  | 3  | 4      | 5     |                 | 6      | 7    | 8  | 9  | 0  | Back   |
+---------------------------------------+                 +---------------------------------------+
| Tab   | Q  | W  | E  | R      | T     |                 | Y      | U    | I  | O  | P  | Del    |
+---------------------------------------+                 +---------------------------------------+
| Ctrl  | A  | S  | D  | F      | G     |                 | H      | J    | K  | L  | :  | "      |
+-----------------------------------------------+ +-----------------------------------------------+
| Shift | Z  | X  | C  | V      | B     | Home  | | End   | N      | M    | <  | >  | ?  |  Shift |
+-----------------------------------------------+ +-----------------------------------------------+
                       | Super  | Lower | Enter | | Space | Higher | Alt  |
                       +------------------------+ +-----------------------+

The following keys are defined
+---------------------------------------+                 +---------------------------------------+
| ????? | ?? | ?? | ?? | ?????? | ????? |                 | ?????? | ???? | ?? | ?? | ?? | ?????? |
+---------------------------------------+                 +---------------------------------------+
| LeftS | C2 | C1 | C2 | C1     | Dis1  |                 | Dis2   | C1   | C2 | C1 | C2 | RightS |
+---------------------------------------+                 +---------------------------------------+
| LeftS | C3 | C4 | C3 | C4     | Dis1  |                 | Dis2   | C4   | C3 | C4 | C3 | RightS |
+-----------------------------------------------+ +-----------------------------------------------+
| ????? | ?? | ?? | ?? | ?????? | ????? | ????? | | ????? | ?????? | ???? | ?? | ?? | ?? | ?????? |
+-----------------------------------------------+ +-----------------------------------------------+
                       | Diphth | V1    | ????? | | ????? | V2     | V3   |
                       +------------------------+ +-----------------------+
"""


def get_consonant_mapping(consonant_counts):
    """
    returns a dict mapping each consonant to a list of {'C1', 'C2', 'C3', 'C4'}
    I try to put more load on C1 and C4 as those are the ring and index finger, not the pinky
    for multiple-key consonants, I'll prefer using pressing two keys with one finger over using two fingers.
    With two keys, I prefer them on the same row
    With three, one will be in the middle, so the fingers don't have to go far apart.
    """
    consonants = list(consonant_counts.keys())
    return {
        consonants[0]: ['C1'],
        consonants[1]: ['C4'],
        consonants[2]: ['C2'],
        consonants[3]: ['C3'],
        consonants[4]: ['C1', 'C4'],
        consonants[5]: ['C2', 'C3'],
        consonants[6]: ['C1', 'C2'],
        consonants[7]: ['C3', 'C4'],
        consonants[8]: ['C1', 'C4', 'C2'],
        consonants[9]: ['C1', 'C4', 'C3'],
        consonants[10]: ['C1', 'C2', 'C3'],
        consonants[11]: ['C2', 'C3', 'C4'],
        consonants[12]: ['C1', 'C3'],
        consonants[13]: ['C2', 'C4'],
    }


def get_vowel_mapping(vowel_counts):
    """
    returns a dict mapping each vowel to a list of {'V1', 'V2', 'V3'}
    because V3 is somewhat far in, I prefer V1 and V2
    """
    vowels = list(vowel_counts.keys())
    return {
        vowels[0]: ['V1'],
        vowels[1]: ['V2'],
        vowels[2]: ['V3'],
        vowels[3]: ['V1', 'V2'],
        vowels[4]: ['V1', 'V3'],
        vowels[5]: ['V2', 'V3'],
        vowels[6]: ['V1', 'V2', 'V3'],
    }


disambiguation_mapping = {
        '1': ['Dis2'],
        '2': ['Dis1'],
        '3': ['Dis1', 'Dis2'],
    }


def consonant_symbol_to_key(consonant, position):
    """
    consonant is one of 'Ci' for i in [1234]
    position is i when consonant is for the ith consonant in a word
    """
    return {
        'C1': ['W', 'R', 'U', 'O'][position],
        'C2': ['Q', 'E', 'I', 'P'][position],
        'C3': ['A', 'D', 'K', ':'][position],
        'C4': ['S', 'F', 'J', 'L'][position],
    }[consonant]


vowel_symbol_to_key = {'V1': 'Lower', 'V2': 'Higher', 'V3': 'Alt', 'Diphth': 'Super'}


disambiguation_symbol_to_keys = {'Dis1': ['T', 'G'], 'Dis2': ['Y', 'H']}


syllable_marker_symbol_to_keys = {'LeftS': ['Tab', 'Ctrl'], 'RightS': ['Del', '"']}


def symbols_to_keys(word):
    """
    Returns a sequence of keys based on the qwerty layout above
    assumes the input is a single word (no '-') in symbols
    position == i if symbol is for the ith (0 based) consonant of a full word.
    for a word with fewer than 4 consonants we go from the middel (1/2) out
    so for tbavk: t: 0, b: 1, v: 2, k: 3
    """
    result = []
    position = 2
    # find position of the first consonant
    for i in range(2):
        if word[i][0][0] == 'C':
            position -= 1
        else:
            break
    # Now we can just iterate through
    for symbols in word:
        for symbol in symbols:
            if symbol[0] == 'C':
                result += [consonant_symbol_to_key(symbol, position)]
            elif symbol[0] == 'V' or symbol == 'Diphth':
                result += [vowel_symbol_to_key[symbol]]
            elif len(symbol) == 4 and symbol[:3] == 'Dis':
                # dis == 1 if Dis1 else dis == 2
                # this is valid, because all consonants have been handled at this point
                dis = int(symbol[-1])
                indices = {1} if consonant_symbol_to_key('C4', dis) in result else {0}
                if consonant_symbol_to_key('C1', dis) in result:
                    indices = indices.union({0})
                result += [disambiguation_symbol_to_keys[symbol][index] for index in indices]
            elif symbol[-1] == 'S':
                # dis == 0 if LeftS else 3
                # this is valid, because all consonants have been handled at this point
                dis = 0 if symbol[:-1] == 'Left' else 3
                indices = {1} if consonant_symbol_to_key('C3', dis) in result else {0}
                if consonant_symbol_to_key('C2', dis) in result:
                    indices.union({0})
                result += [syllable_marker_symbol_to_keys[symbol][index] for index in indices]
        if symbols[0][0] == 'C':
            # we just handled a consonant, so move one position over
            position += 1

    return result


qwerty_order = dict([(y, x) for x, y in enumerate([
    'Tab',
    'Ctrl',
    'W',
    'Q',
    'A',
    'S',
    'R',
    'E',
    'D',
    'F',
    'T',
    'G',
    'Super',
    'Lower',
    'Higher',
    'Alt',
    'Y',
    'H',
    'I',
    'U',
    'J',
    'K',
    'P',
    'O',
    'L',
    ':',
    'Del',
    '"',
])])


if __name__=='__main__':
    # sort the phonemes by frequency.
    # divide by the max frequency of words for numerical stuff
    phoneme_count = {}
    max_count_words = next(iter(counts.items()))[1]
    for notation, english in notation_to_eng_dict.items():
        for phoneme in notation:
            if phoneme in diphthong_to_vowel:
                # diphthongs don't get their own keys, but affect the count of their vowel counterparts.
                phoneme = diphthong_to_vowel[phoneme]
            if phoneme not in phoneme_count:
                phoneme_count[phoneme] = counts[english]/max_count_words
            else:
                phoneme_count[phoneme] += counts[english]/max_count_words

    result = sorted(phoneme_count.items(), key=lambda x: x[1], reverse=True)
    consonant_mapping = get_consonant_mapping({phoneme: count for phoneme, count in result
                                               if phoneme in consonants.values()})
    vowel_mapping = get_vowel_mapping({phoneme: count for phoneme, count in result
                                       if phoneme in vowels.values()})
    # overwrite diphthongs to include 'Diphth' key
    vowel_mapping = dict(vowel_mapping, **{phoneme: ['Diphth'] + vowel_mapping[diphthong_to_vowel[phoneme]]
                                           for phoneme in diphthong_to_vowel})
    # combine everything and add the missing keys
    total_mapping = dict(consonant_mapping, **vowel_mapping)
    total_mapping = dict(total_mapping, **disambiguation_mapping)
    total_mapping = dict(total_mapping, **{
        # left _ has to be handled extra
        '_': ['RightS'],
    })
    to_symbols = []
    for notation, english in notation_to_eng_dict.items():
        result = []
        stems = notation.split('-')
        for stem in stems:
            add_to_end = []
            if stem[0] == '_':
                add_to_end = [['LeftS']]
                stem = stem[1:]
            result += [[total_mapping[phoneme] for phoneme in stem] + add_to_end]
        to_symbols += [(result, english)]

    # now convert symbols to keys
    to_keys = [([symbols_to_keys(symbols) for symbols in words], english)
               for words, english in to_symbols]

    # turn into string and print
    to_string = {' '.join(['-'.join(sorted(stroke, key=lambda x: qwerty_order[x])) for stroke in word]): english
                 for word, english in to_keys}


    # also write a little helper dict to remember what the keys mean
    # consonants first
    consonant_clusters = {}
    for i in range(4):
        # one version for each square
        for ipa, symbols in consonant_mapping.items():
            surrounding_string = '{}'
            if i < 2:
                # the consonant is before the vowel
                surrounding_string = surrounding_string + '.'
            else:
                surrounding_string = '.' + surrounding_string
            surrounding_string = '.'*i + surrounding_string + '.'*(3-i)
            key_sequence = '-'.join(sorted([consonant_symbol_to_key(symbol, i) for symbol in symbols],
                                           key=lambda x: qwerty_order[x]))
            consonant_clusters[key_sequence] = surrounding_string.format(ipa)
    consonant_clusters = dict(sorted(consonant_clusters.items(), key=lambda x: len(x[0]), reverse=True))
    # vowels
    vowel_clusters = {}
    for ipa, symbols in vowel_mapping.items():
        key_sequence = '-'.join(sorted([vowel_symbol_to_key[symbol] for symbol in symbols],
                                       key=lambda x: qwerty_order[x]))
        vowel_clusters[key_sequence] = '..{}..'.format(ipa)
    vowel_clusters = dict(sorted(vowel_clusters.items(), key=lambda x: len(x[0]), reverse=True))
    # disambiguation stuff
    disambiguation_keys_clusters = {}
    for symbol, keys in disambiguation_symbol_to_keys.items():
        result = [[]]
        for key in keys:
            result = [key_sequence + maybe_key for key_sequence in result for maybe_key in [[], [key]]]
        # first one is empty
        result = result[1:]
        disambiguation_keys_clusters[symbol] = result
    disambiguation_clusters = {}
    for number, symbols in disambiguation_mapping.items():
        key_clusters = [disambiguation_keys_clusters[symbol] for symbol in symbols]
        # join left and right side into all possible combinations
        combinations = [[]]
        for cluster in key_clusters:
            combinations = [combination + keys for combination in combinations for keys in cluster]
        for keys in combinations:
            key_sequence = '-'.join(sorted(keys, key=lambda x: qwerty_order[x]))
            disambiguation_clusters[key_sequence] = '......' + number
    disambiguation_clusters = dict(sorted(disambiguation_clusters.items(),
                                          key=lambda x: len(x[0]), reverse=True))

    cheatsheet = dict(consonant_clusters, **vowel_clusters)
    cheatsheet = dict(cheatsheet, **disambiguation_clusters)
    cheatsheet = dict(cheatsheet, **{
        'Tab-Ctrl': '_.....',
        'Tab': '_.....',
        'Ctrl': '_.....',
        'Del-"': '....._',
        'Del': '....._',
        '"': '....._',
    })

    out_file = open('keys_to_eng_dict.py', 'w')
    out_file.write('keys_to_eng_dict = {\n')
    for keys_string, english in to_string.items():
        out_file.write('{}: {},\n'.format(repr(keys_string), repr(english)))
    out_file.write('}\n')
    out_file.write('cheatsheet = {\n')
    for key_sequence, meaning in cheatsheet.items():
        out_file.write('{}: {},\n'.format(repr(key_sequence), repr(meaning)))
    out_file.write('}')

    out_file.close()
