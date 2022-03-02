from eng_to_ipa_dict import eng_to_ipa_dict
from affix_rules import prefixes, suffixes

from suffix_trees.STree import STree


def edit_affix(english, ipa, affix, edit, mode):
    """
    edit format: ((<remove_english>, <add_english>), (<remove_ipa>, <add_ipa>))
    for mode=='infix' edit is a list of two elements, each of the above once
    returns edited english if the edit applies else None
    if suffix, the edits are applied to the end, else the front
    """
    if not affix:
        # the edit is the same as doing nothing, but still check if word exists
        if english in eng_to_ipa_dict and ipa in eng_to_ipa_dict[english]:
            return [(english, english)]
    elif mode == 'prefix':
        (remove_english, add_english), (remove_ipa, add_ipa) = edit
        if english.startswith(remove_english) and ipa.startswith(remove_ipa):
            edited_english = add_english + english[len(remove_english):]
            edited_ipa = add_ipa + ipa[len(remove_ipa):]
            if edited_english in eng_to_ipa_dict and edited_ipa in eng_to_ipa_dict[edited_english]:
                return [(affix, remove_english), (edited_english, english[len(remove_english):])]
    elif mode == 'suffix':
        (remove_english, add_english), (remove_ipa, add_ipa) = edit
        if english.endswith(remove_english) and ipa.endswith(remove_ipa):
            edited_english = english[:-len(remove_english)] + add_english
            edited_ipa = ipa[:-len(remove_ipa)] + add_ipa
            if edited_english in eng_to_ipa_dict and edited_ipa in eng_to_ipa_dict[edited_english]:
                return [(edited_english, english[:-len(remove_english)]), (affix, remove_english)]

    return None


def edit_compound(english, ipa, stem, stem_ipa, affixes, edits):
    """
    similar to edit_affix.
    stem and stem_ipa define which substring to remove. We only split the first occurence
    edits is a list of two: one for the left remainder, one for the right one
    """
    # only split the first occurence, as the rest can be handled later
    split = english.split(stem, 1)
    ipa_split = ipa.split(stem_ipa, 1)
    if len(split) == 2 and len(ipa_split) == 2:
        edited_start = edit_affix(split[0], ipa_split[0], affixes[0], edits[0], 'suffix')
        edited_end = edit_affix(split[1], ipa_split[1], affixes[1], edits[1], 'prefix')
        if (split[0] or split[1]) and (not split[0] or edited_start) and (not split[1] or edited_end):
            first = [edited_start[0]] if edited_start else []
            last = [edited_end[-1]] if edited_end else []
            return first + [(stem, stem)] + last

    return None


def word_at(string, index, sep='|'):
    """
    for string from sep.join([words]), where none of words contains sep returns the word which
    index falls into
    """
    start_index = string.rfind(sep, 0, index)
    end_index = string.find(sep, index)
    return string[start_index+1:end_index]


if __name__=='__main__':
    # End goal: dict from word to composition
    # Intermediate: dict from word to words its in. Works well with suffix trees
    # Basically turn intermediate around and select which decomposition to use.

    # Build suffix tree of all words
    words_string = '|' + '|'.join([english for (english, _, _), *_ in prefixes] +
                         [english for (english, _, _), *_ in suffixes] +
                         [english for english in eng_to_ipa_dict]) + '|'
    suffix_tree = STree(words_string)
    # New dictionary that includes affixes
    ipas = dict(eng_to_ipa_dict, **dict(
                {versions[0][0]: [ipa for _, ipa, _ in versions] for versions in prefixes + suffixes}))
    inverse_composition = {}
    for affixes, mode, separator_func, index_func in [
        (prefixes, 'prefix', lambda x: '|' + x, lambda x: x+1),
        (suffixes, 'suffix', lambda x: x + '|', lambda x: x)]:

        for versions in affixes:
            # The english is the same in every case
            english, _, _ = versions[0]
            # Find matches
            matches = [word_at(words_string, index_func(index))
                       for index in suffix_tree.find_all(separator_func(english))]
            # Remove the affix itself
            matches.remove(english)
            edited_matches = [edit_affix(match_english, match_ipa, affix, edit, mode)
                              for match_english in matches
                              for match_ipa in ipas[match_english]
                              for affix, _, edits in versions
                              for edit in edits]
            # edit_affix returns None when the edit is invalid
            # also remove ipa for now, we don't claim him
            edited_matches = [x for x in edited_matches if x]
            inverse_composition[english] = edited_matches

    # Now for the normal words
    for english, word_ipas in eng_to_ipa_dict.items():
        # give a minimum size to stems, otherwise we get words split up into syllables or less
        if len(english) < 5:
            inverse_composition[english] = []
            continue
        matches = [word_at(words_string, index)
                   for index in suffix_tree.find_all(english)]
        # Remove the affix itself
        matches.remove(english)
        edited_matches = [edit_compound(match_english, match_ipa, english, ipa,
                              # for now, we don't have any sophisticated edits
                              ['', ''],
                              [(('', ''), ('', '')), (('', ''), ('', ''))])
                          for match_english in matches
                          for match_ipa in ipas[match_english]
                          for ipa in word_ipas]
        # Removes Nones
        edited_matches = [x for x in edited_matches if x]
        inverse_composition[english] = edited_matches

    # Invert the dictionary to get the form we want
    composition = {english: [] for english in inverse_composition.keys()}
    for splits in inverse_composition.values():
        for split in splits:
            stems = [part[0] for part in split]
            original = ''.join([part[1] for part in split])
            composition[original] += [stems]

    # Now each word is split into 0-3 parts. Break each of those down as far as possible.
    # Also the stems aren't assigned yet.
    # By sorting length-wise we make sure that all values we access have already been refined.
    for english, splits in sorted(composition.items(), key=lambda x: len(x[0])):
        result = []
        if not splits:
            result = [[english]]
        for split in splits:
            intermediate_result = [[]]
            for part in split:
                if part not in composition or not composition[part]:
                    # this part cannot be reduced further
                    intermediate_result = [intermediate_part + [part]
                                           for intermediate_part in intermediate_result]
                else:
                    # all combinations to spell all splits
                    intermediate_result = [intermediate_part + subpart
                                           for intermediate_part in intermediate_result
                                           for subpart in composition[part]]
            # There will be duplicates on some words
            for split in intermediate_result:
                if split not in result:
                    result += [split]
        composition[english] = result                  

    # write output
    out_file = open('eng_stems_to_ipa_dict.py', 'w')
    out_file.write('eng_stems_to_ipa_dict = {\n')
    for key, val in composition.items():
        out_file.write('{}: {},\n'.format(repr(key), repr(val)))
    out_file.write('}')

    out_file.close()
