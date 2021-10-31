from eng_stems_to_ipa_dict import eng_stems_to_ipa_dict
from sys import argv
from re import sub


if __name__=='__main__':
    in_file = open(argv[1], 'r')
    text = in_file.read()
    in_file.close()

    text = text.lower()
    text = sub(r'(?![a-z]|\'|-).+?', ' ', text)
    result = ""
    for line in text.split('\n'):
        line = line.strip()
        line = sub(r'\s+', ' ', line)
        result += line + '\n'

    out_file = open('source.txt', 'w')
    out_file.write(result)
    out_file.close()
