from eng_to_ipa_dict import eng_to_ipa_dict

if __name__=='__main__':
    in_file = open('source.txt', 'r')
    text = in_file.read()
    in_file.close()

    result = [[]]
    for line in text.split('\n'):
        for word in line.split():
            # Just take the first translation for now
            word = eng_to_ipa_dict.get(word, [''])[0]
            if word:
                result[-1] += [word]
        result += [[]]

    out_file = open('source_ipa.txt', 'w')
    out_file.write('\n'.join([' '.join(line) for line in result]))
    out_file.close()
