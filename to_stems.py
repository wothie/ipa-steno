from eng_to_ipa_dict import eng_to_ipa_dict
from counted_english import counted_english
from affix_rules import prefixes, suffixes
from to_notation import count_syllables


# Order by length to get the most significant affixes first.
prefixes_sorted = sorted(prefixes.keys(), key=len, reverse=True)
suffixes_sorted = sorted(suffixes.keys(), key=len, reverse=True)


def strip_affix(english, stripped_apis):
    """
    Remove a single prefix and/or a single suffix.
    Returns the new stripped english, the prefix or [],
    the list of stripped apis, and the suffix or [].
    """
    prefix_result = None
    suffix_result = None
    stripped_english = english
    # Determine single-syllable words if all ipas have one syllable
    if all([count_syllables(ipa) == 1 for ipa in eng_to_ipa_dict[english]]):
        return english, None, stripped_apis, None

    for prefix in prefixes_sorted:
        # Don't strip whole affixes
        if english == prefix:
            return english, None, stripped_apis, None
        if english.startswith(prefix):
            # Alphabetical prefix found. Check if it's also pronounced like a prefix
            remaining_apis = [ipa[len(ipa_prefix):]
                             for ipa in stripped_apis for ipa_prefix
                             in sorted(prefixes[prefix], key=len, reverse=True)
                             if ipa.startswith(ipa_prefix)]
            # If any are left, we found our prefix.
            if remaining_apis:
                stripped_english = stripped_english[len(prefix):]
                stripped_apis = remaining_apis
                prefix_result = prefix
                break

    for suffix in suffixes_sorted:
        # Don't strip whole affixes
        if english == suffix:
            return stripped_english, None, stripped_apis, None
        if english.endswith(suffix):
            # Alphabetical suffix found. Check if it's also pronounced like a suffix
            remaining_apis = [ipa[:-len(ipa_suffix)]
                             for ipa in stripped_apis for ipa_suffix
                             in sorted(suffixes[suffix], key=len, reverse=True)
                             if ipa.endswith(ipa_suffix)]
            # If any are left, we found our suffix.
            if remaining_apis:
                stripped_english = stripped_english[:-len(suffix)]
                stripped_apis = remaining_apis
                suffix_result = suffix
                break

    return stripped_english, prefix_result, stripped_apis, suffix_result


def strip_affixes(english):
    """
    Iteratively tries to strip affixes until none are left or the resulting word isn't a word anymore.
    Returns the prefixes and suffixes in order.
    """
    prefix_result = []
    stripped_apis = eng_to_ipa_dict[english]
    suffix_result = []
    while english in eng_to_ipa_dict.keys():
        english, prefix, stripped_apis, suffix = strip_affix(english, stripped_apis)
        prefix_result = prefix_result + [prefix] if prefix else prefix_result
        suffix_result = [suffix] + suffix_result if suffix else suffix_result
        if not prefix and not suffix:
            # Nothing could be stripped, we are done.
            break

    return prefix_result, suffix_result


if __name__=='__main__':
    #accepted = {english: eng_to_ipa_dict[english] for english, _ in counted_english[:1000]
    #            if english in eng_to_ipa_dict.keys()}
    accepted = {}
    rejected = {}
    todo = [english for english, _ in counted_english if english in eng_to_ipa_dict.keys()]

    for english in todo:
        # Only allowed single-letter words are I and a
        # Those don't even have to get rejected as they won't be multi-stroke either
        if len(english) == 1 and english not in 'ia':
            continue
        stripped_prefixes, stripped_suffixes = strip_affixes(english)
        # If there are no stripped_prefixes or stripped_suffixes, the word is accepted.
        if not stripped_prefixes and not stripped_suffixes:
            accepted[english] = eng_to_ipa_dict[english]
        else:
            rejected[english] = [stripped_prefixes, stripped_suffixes]

    # write output
    out_file = open('eng_stems_to_ipa_dict.py', 'w')

    out_file.write('eng_stems_to_ipa_dict = {\n')
    for key, val in accepted.items():
        out_file.write('{}: {},\n'.format(repr(key), val))
    out_file.write('}\n')

    out_file.write('rejected = {\n')
    for key, val in rejected.items():
        out_file.write('{}: {},\n'.format(repr(key), val))
    out_file.write('}')

    out_file.close()
