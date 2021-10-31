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


def split_middle(word):
    """
    Splits a word into three parts.
    The onset, the middle vowel cluster, and the ending.
    Onset and ending come with their vowels removed.
    """

    syllable_count = count_syllables(word)
    if syllable_count == 1:
        # no need to find right cluster
        # position of the first vowel
        vowel_position = [n for n, c in enumerate(word) if c in vowels][0]
        return split_at(word, vowel_position)
    elif syllable_count == 2:
        # Try to maximize the number of consonants in the final word
        starting_consonants_number = [n for n, c in enumerate(word) if c in vowels][0]
        ending_consonants_number = [n for n, c in enumerate(word[::-1]) if c in vowels][0]
        if ending_consonants_number <= starting_consonants_number:
            # first syllable
            position = nth_syllable_position(word, syllable_count - 2)
        else:
            # last syllable
            position = nth_syllable_position(word, syllable_count - 1)
        return split_at(word, position)
    elif 3 <= syllable_count <= 4:
        # Take the second one, unless there's only one consonant after it
        second_syllable_position = nth_syllable_position(word, syllable_count - 1)
        consonants_after_middle_vowel = len([c for c in word[second_syllable_position:] if c in consonants])
        consonants_before_middle_vowel = len([c for c in word[:second_syllable_position] if c in consonants])
        if consonants_after_middle_vowel >= 2 or consonants_after_middle_vowel > consonants_before_middle_vowel:
            return split_at(word, second_syllable_position)
        return split_at(word, nth_syllable_position(word, syllable_count - 2))
    elif syllable_count >= 5:
        # Take the second to last syllable unless there's only 1 consonant
        second_syllable_position = nth_syllable_position(word, syllable_count - 1)
        consonants_after_middle_vowel = len([c for c in word[second_syllable_position:] if c in consonants])
        if consonants_after_middle_vowel >= 2:
            return split_at(word, second_syllable_position)
        return split_at(word, nth_syllable_position(word, syllable_count - 2))


def to_notation(beginning, middle, end, left_syllable, right_syllable):
    """
    e.g. "nenaumik" -> "_nnaumk_"; "blegik" -> "blegk_"
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

if __name__=='__main__':
    # Try to take the shorter simplified ipa word.
    out_file = open('eng_to_notation_dict.py', 'w')
    out_file.write('eng_to_notation_dict = {\n')
    for english, ipa_list in eng_to_simp_ipa_dict.items():
        result_list = [to_notation(*split_middle(ipa)) for ipa in ipa_list]
        shortest_result = result_list[0]
        min = len(shortest_result)
        for result in result_list:
            if len(result) < min:
                min = len(result)
                shortest_result = result
        out_file.write('"{}": "{}",\n'.format(english, shortest_result))
    out_file.write('}')
