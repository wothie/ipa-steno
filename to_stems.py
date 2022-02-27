from eng_to_ipa_dict import eng_to_ipa_dict
from counted_english import counted_english
from affix_rules import prefixes, suffixes
from to_notation import count_syllables


# Order by length to get the most significant affixes first.
prefixes_sorted = sorted(prefixes, key=lambda x: len(x[0][0]), reverse=True)
suffixes_sorted = sorted(suffixes, key=lambda x: len(x[0][0]), reverse=True)


def edit_affix(english, ipa, edit, mode):
    """
    edit format: ((<remove_english>, <add_english>), (<remove_ipa>, <add_ipa>))
    returns edited (english, ipa) if the edit applies else (None, None)
    if suffix, the edits are applied to the end, else the front
    """
    (remove_english, add_english), (remove_ipa, add_ipa) = edit
    if mode=='prefix':
        # prefix
        if not english.startswith(remove_english) or not ipa.startswith(remove_ipa):
            # edit doesn't apply
            return None
        english = add_english + english[len(remove_english):]
        ipa = add_ipa + ipa[len(remove_ipa):]
    elif mode=='suffix':
        # suffix
        if not english.endswith(remove_english) or not ipa.endswith(remove_ipa):
            # edit doesn't apply
            return None
        english = english[:-len(remove_english)] + add_english
        ipa = ipa[:-len(remove_ipa)] + add_ipa

    # If return None if the result doesn't exist in the dictionary
    if not english in eng_to_ipa_dict:
        return None

    return english, ipa


def strip_affix(english):
    """
    Remove a single prefix and/or a single suffix.
    Output format: [(<prefix>, <prefix_ipa>), (<stem>, <stem_api>), (<suffix>, <suffix_ipa>)]
    the first or last tuple may be None, but not both
    If nothing can be reduced, an empty list is returned
    """
    prefix_result = None
    suffix_result = None
    stripped_english = english
    # Define single-syllable words if all ipas have one syllable
    if all([count_syllables(ipa) == 1 for ipa in eng_to_ipa_dict[english]]):
        return english, None, stripped_ipas, None

    # start with the unedited versions
    possible_splits = [(None, (english, ipa), None) for ipa in eng_to_ipa_dict[english]]
    unedited_length = len(possible_splits)

    for _, (english, ipa), _ in possible_splits:
        for prefix_versions in prefixes_sorted:
            for prefix, ipa_prefix, edits in prefix_versions:
                # Don't strip whole affixes
                if english == prefix:
                    # possible_splits at this point could have already reduced it, so we recompute.
                    return [(None, (english, ipa), None) for ipa in eng_to_ipa_dict[english]]
                if english.startswith(prefix):
                    # check all edits for every combination
                    possible_splits += [((prefix, ipa_prefix), edit_affix(english, ipa, edit, 'prefix'), None)
                                        for edit in edits]

    for prefix_bundle, (english, ipa), _ in possible_splits:
        for suffix_versions in suffixes_sorted:
            for suffix, ipa_suffix, edits in suffix_versions:
                # Don't strip whole affixes
                if english == suffix:
                    # possible_splits at this point could have already reduced it, so we recompute.
                    return [(None, (english, ipa), None) for ipa in eng_to_ipa_dict[english]]
                if english.endswith(suffix):
                    # check all edits for every combination
                    possible_splits += [(prefix_bundle, edit_affix(english, ipa, edit, 'suffix'), (suffix, ipa_suffix)
                                        for edit in edits]

    # Remove the unedited versions from the list
    possible_splits = possible_splits[unedited_length:]
    # only retain the elements where the middle isn't None as those signal failed edits
    possible_splits = [x for x in possible_splits if x[1]]
    return possible_splits


def strip_affixes(english):
    """
    Iteratively tries to strip affixes until none are left or the resulting word isn't a word anymore.
    Only the deepest level with any valid words remains
    Output format: [[(<prefix>, <prefix_ipa>)], (<stem>, <stem_api>), [(<suffix>, <suffix_ipa>)]]
    If nothing could be reduced, returns the empty list
    """
    # Try to strip one level off
    result = strip_affix(english)
    for i in range(len(result)):
        # Adhere to the new output format of this function compared to strip_affix
        # Wrap prefix and suffix in a list, if given
        result[i][0] = [result[i][0]] if result[i][0] else []
        result[i][2] = [result[i][2]] if result[i][2] else []

    while True:
        # variable used for replacing one level with the next one
        intermediate_result = []
        # Iteratively go one level deeper on the previous results until nothing can be done
        for prefix_bundle, (stripped_english, _), suffix_bundle in result:
            # variable for tracking which entries in this level are new per loop iteration
            old_index = len(intermediate_result)
            intermediate_result += strip_affix(stripped_english)
            # add pre-/suffix from previous level
            for i in range(old_index, len(intermediate_result)):
                new_prefix, new_suffix = intermediate_result[i][0], intermediate_result[i][2]
                intermediate_result[i][0] = prefix_bundle + [new_prefix] if new_prefix else prefix_bundle
                intermediate_result[i][2] = [new_suffix] + suffix_bundle if new_suffix else suffix_bundle

        # If intermediate_result is empty, we couldn't reduce anything in this level and are done.
        if not intermediate_result:
            break
        # Else we try one more level
        result = intermediate_result

    return result


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
        possible_splits = strip_affixes(english)
        # If there are no possible_splits, the word is accepted.
        if not possible_splits:
            accepted[english] = eng_to_ipa_dict[english]
        else:
            # try to get the split with the fewest elements to minimize strokes
            # First, flatten each split
            possible_splits = [prefix_bundle + [stem] + suffix_bundle
                               for prefix_bundle, stem, suffix_bundle in possible_splits]
            rejected[english] = sorted(possible_splits, key=len)[0]

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
