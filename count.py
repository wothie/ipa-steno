import sys
from collections import Counter

if __name__=='__main__':
    in_file = open('source.txt', 'r')
    text = in_file.read()
    in_file.close()

    result = Counter(text.split())

    out_file = open('counted_english.py', 'w')
    out_file.write('counted_english = [\n')
    for word, count in sorted(dict(result).items(), key=lambda x: x[1], reverse=True):
        out_file.write('({}, {}),\n'.format(repr(word), count)) 
    out_file.write(']')
    out_file.close()
