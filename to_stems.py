from eng_to_ipa_dict import eng_to_ipa_dict
from counted_english import counted_english
from affix_rules import prefixes, suffixes

def check_ipa_prefix(english, ipa_list, ipa_prefixes):
    for ipa_prefix in ipa_prefixes:
        # Make sure we only count significant ones (if possible).
        for ipa_english in ipa_list:
            if ipa_english.startswith(ipa_prefix):
                # prefix is the same for some pair of ipa_english and ipa_prefix
                return True
    return False


def check_ipa_suffix(english, ipa_list, ipa_suffixes):
    for ipa_suffix in ipa_suffixes:
        # Make sure we only count significant ones (if possible).
        for ipa_english in ipa_list:
            if ipa_english.endswith(ipa_suffix):
                # suffix is the same for some pair of ipa_english and ipa_suffix
                return True
    return False


if __name__=='__main__':
    # Order by length to get the most significant affixes first.
    prefixes_sorted = sorted(prefixes.keys(), key=len)
    suffixes_sorted = sorted(suffixes.keys(), key=len)

    accepted = {english: eng_to_ipa_dict[english] for english, _ in counted_english[:1000] if english in eng_to_ipa_dict}
    rejected = {}

    for english, ipa_list in eng_to_ipa_dict.items():
        was_rejected = False

        for prefix in prefixes_sorted:
            # Don't remove prefixes that are whole words
            if english == prefix:
                continue
            if english.startswith(prefix):
                if check_ipa_prefix(english, eng_to_ipa_dict[english], prefixes[prefix]):
                    # add this prefix to the reasons for rejection
                    if english in rejected:
                        rejected[english] += [prefix]
                    else:
                        rejected[english] = [prefix]
                    was_rejected = True

                    # We already have the longest prefix that fits this word, so no need to search further
                    break

        for suffix in suffixes_sorted:
            # Don't remove suffixes that are whole words
            if english == suffix:
                continue
            if english.endswith(suffix):
                if check_ipa_suffix(english, eng_to_ipa_dict[english], suffixes[suffix]):
                    # add this suffix to the reasons for rejection
                    if english in rejected:
                        rejected[english] += [suffix]
                    else:
                        rejected[english] = [suffix]
                    was_rejected = True

                    # We already have the longest suffix that fits this word, so no need to search further
                    break

        if not was_rejected:
            # Found a full word that doesn't have any pre- or suffixes
            accepted[english] = eng_to_ipa_dict[english]


    # write output
    out_file = open('eng_stems_to_ipa_dict.py', 'w')

    out_file.write('eng_stems_to_ipa_dict = {\n')
    for key, val in accepted.items():
        out_file.write('"{}": {},\n'.format(key, val))
    out_file.write('}\n')

    out_file.write('rejected = {\n')
    for key, val in rejected.items():
        out_file.write('"{}": {},\n'.format(key, val))
    out_file.write('}')

    out_file.close()
