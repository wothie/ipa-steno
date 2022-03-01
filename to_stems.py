from eng_to_ipa_dict import eng_to_ipa_dict
from counted_english import counted_english
from affix_rules import prefixes, suffixes
from count_syllables import count_syllables

from suffix_trees.STree import STree
from itertools import product
from more_itertools import intersperse


# Order by length of the english affix to get the most significant affixes first.
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

    # Return None if the result doesn't exist in the dictionary
    if not english in eng_to_ipa_dict or not ipa in eng_to_ipa_dict[english]:
        return None

    return english, ipa


def strip_affix(english):
    """
    Remove a single prefix and/or a single suffix.
    Output format: [(<prefix>, <prefix_ipa>), (<stem>, <stem_api>), (<suffix>, <suffix_ipa>)]
    the first or last tuple may be None, but not both
    If nothing can be reduced, an empty list is returned
    """
    # Define single-syllable words if all ipas have one syllable
    if all([count_syllables(ipa) == 1 for ipa in eng_to_ipa_dict[english]]):
        return []

    # start with the unedited versions
    possible_splits = [[None, (english, ipa), None] for ipa in eng_to_ipa_dict[english]]
    unedited_length = len(possible_splits)

    for _, (english, ipa), _ in possible_splits[:]:
        for prefix_versions in prefixes_sorted:
            for prefix, ipa_prefix, edits in prefix_versions:
                # Don't strip whole affixes
                if english == prefix:
                    return []
                if english.startswith(prefix):
                    # check all edits for every combination
                    possible_splits += [[(prefix, ipa_prefix), edit_affix(english, ipa, edit, 'prefix'), None]
                                        for edit in edits]

    # only retain the elements where the middle isn't None as those signal failed edits
    possible_splits = [x for x in possible_splits if x[1]]
    for prefix_pair, (english, ipa), _ in possible_splits[:]:
        for suffix_versions in suffixes_sorted:
            for suffix, ipa_suffix, edits in suffix_versions:
                # Don't strip whole affixes
                if english == suffix:
                    return []
                if english.endswith(suffix):
                    # check all edits for every combination
                    possible_splits += [[prefix_pair, edit_affix(english, ipa, edit, 'suffix'), (suffix, ipa_suffix)]
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
    Output format: [[("part", "ipa_part")]]
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

    # flatten the result
    return [prefix_bundle + [(english, ipa)] + suffix_bundle
            for prefix_bundle, (english, ipa), suffix_bundle in result]


def word_at(string, index, sep='|'):
    """
    for string from sep.join([words]), where none of words contains sep returns the word which
    index falls into
    """
    start_index = string.rfind(sep, 0, index)
    end_index = string.find(sep, index)
    return string[start_index+1:end_index]


def recurse_compounds(splits, compounds):
    """
    expects a [(<english>, <ipa>)] and a dictionary as generated in split_compounds
    returns a new list which is broken down as far as possible into compounds
    If used in sequence, the iterator should sort stems from shortest to longest
    """
    result = []
    for split in splits:
        intermediate_result = [[]]
        for stem, ipa in split:
            if stem not in compounds or not compounds[stem]:
                # this stem cannot be reduced further
                intermediate_result = [intermediate_part + [(stem, ipa)]
                                       for intermediate_part in intermediate_result]
            else:
                # all combinations to spell all splits
                intermediate_result = [intermediate_part + compound
                                       for intermediate_part in intermediate_result
                                       for compound in compounds[stem]]
        result += intermediate_result
    return result

def split_compounds(stems):
    """
    Creates a suffix_tree for english to test whether one stem is made up of several others.
    Return format: <english>: [[(<english_part>, <ipa_part>)]]
    If the stem couldn't be split, its entry will be an empty list.
    If it could be split, only the ipa_options that allowed the split are kept
    """
    # Create large string of all stems to find words again later
    sorted_stems = sorted(stems, key=len)
    stems_string = '|'.join(sorted_stems) + '|'
    stems_tree = STree(stems_string)
    result = {stem: [] for stem in stems}

    for stem in sorted_stems:
        # Reject the first match, as we sorted the stems by length, so the first match is stem itself
        matches = [word_at(stems_string, index) for index in sorted(stems_tree.find_all(stem))][1:]
        if not matches:
            # stem isn't substring of anything
            continue
        # Check that match\stem still equals a valid stem
        splits = [list(filter(str.strip, intersperse(stem, (single_match.split(stem)))))
                  for single_match in matches]
        # First check that the parts appear in the dictionary
        splits = list(filter(lambda split: all([part in eng_to_ipa_dict for part in split]), splits))
        # Then check that there is some valid ipa parts
        # Construct all combinations of ipa_parts and check if they equal the ipa_stem
        ipa_splits = [[eng_to_ipa_dict[part] for part in split] for split in splits]
        ipa_splits = [list(product(*ipa_versions)) for ipa_versions in ipa_splits]

        for ipa_split, split in zip(ipa_splits, splits):
            # Each ipa_split has several versions, each a tuple of strings
            # i.e. ipa_split: [("ipa_part",)]
            for ipa_version in ipa_split:
                # Check that the concatenation of all parts is a valid ipa spelling for the match
                if ''.join(ipa_version) not in eng_to_ipa_dict[''.join(split)]:
                    # doesn't combine to a valid word, so ignore
                    continue
                # The result will include one entry for each possible spelling of the same split
                # Check for duplicates from the other stems
                if list(zip(split, ipa_version)) not in result[''.join(split)]:
                    result[''.join(split)] += [list(zip(split, ipa_version))]

    for stem, splits in result.items():
        result[stem] = recurse_compounds(splits, result)
    return result


if __name__=='__main__':
    #stems = {english: eng_to_ipa_dict[english] for english, _ in counted_english[:1000]
    #            if english in eng_to_ipa_dict.keys()}
    affix_free    = {}
    stems = {}
    affixed = {}
    todo = [english for english, _ in counted_english if english in eng_to_ipa_dict.keys()]

    # Strip all words of their affixes if they have any
    for english in todo:
        possible_splits = strip_affixes(english)
        # If there are no possible_splits, the word is a stem.
        if not possible_splits:
            affix_free[english] = eng_to_ipa_dict[english]
        else:
            affixed[english] = possible_splits

    # Check for compound words in affix_free. Stems can only be made up of other affix_free
    # Keep a dict from full to compound to also handle splitting the affix_free of affixed words
    decomposed = split_compounds(affix_free)
    compounds = {}
    for stem, splits in decomposed.items():
        if not splits:
            # Couldn't be split. Truly a single-stroke worthy candidate
            # Just take the first version for now
            stems[stem] = eng_to_ipa_dict[stem][0]
        else:
            # Wasn't so stemmy after all.
            # Try to minimize strokes by using shorter splits.
            # By recurse_decomposed, all parts should already be accepted
            compounds[stem] = splits[0]
    # Same deal for the affixed ones, as they are only split by affixes now
    for stem, splits in affixed.items():
        # Using decomposed as reference should be enough, as the parts in affixed
        # are all in affix_free.keys()
        compounds[stem] = recurse_compounds(splits, decomposed)[0]
    # Add pre- and suffixes themselves as stems
    # Also just take the first ipa option for each of them for now
    for entry in prefixes:
        english, ipa, _ = entry[0]
        stems[english] = ipa
    for entry in suffixes:
        english, ipa, _ = entry[0]
        stems[english] = ipa

    # write output
    out_file = open('eng_stems_to_ipa_dict.py', 'w')

    out_file.write('stems = {\n')
    for key, val in stems.items():
        out_file.write('{}: {},\n'.format(repr(key), repr(val)))
    out_file.write('}\n')
    out_file.write('compounds = {\n')
    for key, val in compounds.items():
        out_file.write('{}: {},\n'.format(repr(key), repr(val)))
    out_file.write('}')

    out_file.close()
