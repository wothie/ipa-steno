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
        consonants[0] = ['C1'],
        consonants[1] = ['C4'],
        consonants[2] = ['C2'],
        consonants[3] = ['C3'],
        consonants[4] = ['C1', 'C4'],
        consonants[5] = ['C2', 'C3'],
        consonants[6] = ['C1', 'C2'],
        consonants[7] = ['C3', 'C4'],
        consonants[8] = ['C1', 'C4', 'C2'],
        consonants[9] = ['C1', 'C4', 'C3'],
        consonants[10] = ['C1', 'C2', 'C3'],
        consonants[11] = ['C2', 'C3', 'C4'],
        consonants[12] = ['C1', 'C3'],
        consonants[13] = ['C2', 'C4'],
    }


def get_vowel_mapping(vowel_counts):
    """
    returns a dict mapping each vowel to a list of {'V1', 'V2', 'V3'}
    because V3 is somewhat far in, I prefer V1 and V2
    """
    vowels = list(vowel_counts.keys())
    return {
        vowels[0] = ['V1'],
        vowels[1] = ['V2'],
        vowels[2] = ['V3'],
        vowels[3] = ['V1', 'V2'],
        vowels[4] = ['V1', 'V3'],
        vowels[5] = ['V2', 'V3'],
        vowels[6] = ['V1', 'V2', 'V3'],
    }


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

    result = list(sorted(phoneme_count.items(), key=lambda x: x[1], reverse=True))
    consonant_mapping = get_consonant_mapping({phoneme: count for phoneme, count in result.items()
                                               if phoneme in consonants.values()})
    vowel_mapping = get_vowel_mapping({phoneme: count for phoneme, count in result.items()
                                       if phoneme in vowels.values()})
    # add diphthongs
    vowel_mapping = dict(vowel_mapping, **{phoneme: ['Diphth'] + vowel_mapping[diphthong_to_vowel[phoneme]]
                                           if phoneme in diphthong_to_vowel})
    # combine everything and add the missing keys
    total_mapping = dict(consonant_mapping, **vowel_mapping)
    total_mapping = dict(total_mapping, **{
        # prefer right hand
        '1': ['Dis2'],
        '2': ['Dis1'],
        '3': ['Dis1', 'Dis2'],
        # first _ has to be handled extra
        '_': ['RightS'],
    })
    to_symbols = {}
    for notation, english in notation_to_eng_dict.items():
        result = []
        stems = notation.split('-')
        for stem in stems:
            result += [[]]
            if stem[0] = '_':
                result[-1] += ['LeftS']
                stem = stem[1:]
            result += [symbol for phoneme in stem for symbol in total_mapping[phoneme]]
        to_symbols[result] = english

    # now convert symbols to keys
    # TODO
