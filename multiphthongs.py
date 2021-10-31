from nltk import ngrams
from collections import Counter
from vowels_and_consonants import vowels, consonants

# One dict for consonant clusters, one for vowel clusters and one for combined clusters that aren't in the other two.

max_len = 3
depth = 100

if __name__=='__main__':
    in_file = open('source_ipa.txt', 'r')
    text = in_file.read()
    in_file.close()

    # make all one line
    text = ' '.join(text.split('\n'))

    result = {}
    for n in range(max_len):
        tokens = [''.join(zipped) for zipped in ngrams(text, n + 1)]
        result.update(dict(Counter(tokens)))
    result = sorted(result.items(), key=lambda item: item[1], reverse = True)

    # For the consonant clusters
    consonants_result = {}

    for cluster, number in result:
        if all(map(lambda c: c in consonants, cluster)):
            # consonant cluster
            consonants_result[cluster] = number
    # For the vowel clusters
    vowels_result = {}
    for cluster, number in result:
        if all(map(lambda c: c in vowels, cluster)):
            # Vowel cluster
            vowels_result[cluster] = number
    # The rest
    rest_result = {}
    for cluster, number in result:
        if cluster not in consonants_result and cluster not in vowels_result:
            rest_result[cluster] = number

    out_file = open('multiphthongs.txt', 'w')
    out_file.write('consonants = {\n')
    for cluster, number in consonants_result.items():
        out_file.write('"{}": {},\n'.format(cluster, number))
    out_file.write('}\n\n')
    out_file.write('vowels = {\n')
    for cluster, number in vowels_result.items():
        out_file.write('"{}": {},\n'.format(cluster, number))
    out_file.write('}\n\n')
    out_file.write('rest = {\n')
    for cluster, number in rest_result.items():
        out_file.write('"{}": {},\n'.format(cluster, number))
    out_file.write('}')
    out_file.close()
