from eng_composition import eng_composition

import sys
from collections import Counter


if __name__=='__main__':
    in_file = open('source.txt', 'r')
    text = in_file.read()
    in_file.close()

    result = Counter(text.split())
    # only take the words that we have an ipa for
    first_count = {english: count for english, count in result.most_common() if english in eng_composition}

    # add to each word also the count of words that its a part of
    # divide by the total number of splits per word for "fairness"
    recursive_count = first_count.copy()
    for english, count in first_count.items():
        for split in eng_composition[english]:
            for part in split:
                if part in recursive_count:
                    recursive_count[part] += count/len(split)
                else:
                    # add those stems that are needed for other words
                    recursive_count[part] = count/len(split)
    # sort by count
    result = dict(sorted(recursive_count.items(), key=lambda x: x[1], reverse=True))

    out_file = open('counts.py', 'w')
    out_file.write('counts = {\n')
    for english, count in result.items():
        # don't write the counts, just sort
        out_file.write('{}: {},\n'.format(repr(english), count))
    out_file.write('}')
    out_file.close()
