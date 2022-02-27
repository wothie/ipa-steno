from vowels_and_consonants import vowels, consonants
from eng_to_simp_ipa_dict import eng_to_simp_ipa_dict
from sys import stdin


def count_syllables(word):
    count = 0
    in_cluster = False
    for c in word:
        if c in vowels:
            if not in_cluster:
                count += 1
            in_cluster = True
        elif c in consonants:
            in_cluster = False
    return count


def split_at(word, index):
    """
    Assumes that index points to the left position of a vowel cluster.
    Returns all consonants up to the cluster, the cluster, and all consonants after it.
    Also returns whether there are more syllables to either side.
    """

    beginning = word[:index]
    middle = end = ''
    in_cluster = True
    for c in word[index:]:
        if c in vowels and in_cluster:
            middle += c if c in vowels else ''
        else:
            end += c
            in_cluster = False
    # remove vowels from beginning and end
    left_syllable = bool([c for c in beginning if c in vowels])
    right_syllable = bool([c for c in end if c in vowels])
    beginning = ''.join([c for c in beginning if c in consonants])
    end = ''.join([c for c in end if c in consonants])

    return beginning, middle, end, left_syllable, right_syllable


def nth_syllable_position(word, n):
    """
    Returns the index of the nth syllable in the word, where syllables are measured by arbitrary vowel clusters.
    -1 is returned should the bitch have too few syllables.
    """

    in_cluster = False
    for i, c in enumerate(word):
        if c in vowels and not in_cluster:
            in_cluster = True
            if n == 0:
                # That was the last one
                return i
        elif c in consonants:
            if in_cluster:
                # Just got through another syllable
                n -= 1
            in_cluster = False
    return -1


def to_notation(beginning, middle, end, left_syllable, right_syllable):
    """
    e.g. "nenaumik" -> "_nnAmk_"; "blegik" -> "blegk_"
    """

    result = '_' if left_syllable else ''
    if len(beginning) > 2:
        # only first consonant and the one right before the vowel cluster
        beginning = beginning[0] + beginning[-1]
    result += beginning
    if len(middle) > 1:
        # use marker that there are more than one vowel
        if (diphthong_positions := [i for i in range(len(middle)) if middle[i] in 'ƐӔƆUꞮɅƏ']):
            # There is a diphthong. Take the first one
            middle = middle[diphthong_positions[0]]
        middle = middle[0]
    result += middle
    if len(end) > 2:
        # only last consonant and the one right after the vowel cluster
        end = end[0] + end[-1]
    result += end
    result += '_' if right_syllable else ''

    return result


def find_longest(word):
    """
    Tries splitting the word at all possible places and uses the one that produces the longest notation.
    This is for disambiguation.
    Ties are attempted to resolve by preferring diphtongs
    """
    results = [to_notation(*split_at(word, nth_syllable_position(word, i)))
               for i in range(count_syllables(word))]
    # sort by length
    results = sorted(results, key=len, reverse=True)
    # take only the longest ones
    results = list(filter(lambda x: len(x) == len(results[0]), results))
    # prefer diphthongs
    results = sorted(results, key=lambda ipa: len(list(filter(lambda x: x in 'ƐӔƆUꞮɅƏ', ipa))), reverse=True)
    if not results:
        # We found a word without syllables
        return None
    return results[0]


if __name__=='__main__':
    out_file = open('eng_to_notation_dict.py', 'w')
    out_file.write('eng_to_notation_dict = {\n')
    for english, ipa_list in eng_to_simp_ipa_dict.items():
        results = [find_longest(ipa) for ipa in ipa_list]
        results = list(filter(lambda x: x, results))
        results = sorted(results, key=len, reverse=True)
        out_file.write('"{}": "{}",\n'.format(english, results[0]))
    out_file.write('}')
