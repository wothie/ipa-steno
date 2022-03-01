from vowels_and_consonants import vowels, consonants


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


