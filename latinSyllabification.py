# -*- coding: utf-8 -*-
import re

consonant_groups = ['qu', 'ch', 'ph', 'fl', 'fr', 'st', 'br', 'cr', 'cl', 'pr', 'tr', 'ct', 'th', 'sp']
diphthongs = ['ae', 'au', 'ei', 'oe', 'ui', 'ya', 'ex', 'ix']
vowels = ['a', 'e', 'i', 'o', 'u', 'y']

abbreviations = {
    u'dns': ['do', 'mi', 'nus'],
    u'dūs': ['do', 'mi', 'nus'],
    u'dne': ['do', 'mi', 'ne'],
    u'alla': ['al', 'le', 'lu', 'ia'],
    u'xpc': ['xp', 'ic', 'tuc'],
    u'^': ['us'],
    u'ā': ['am'],
    u'ē': ['em'],
    u'ū': ['um'],
    u'ō': ['om']
}


def syllabify_word(inp, verbose=False):
    '''
    separate each word into UNITS - first isolate consonant groups, then diphthongs, then letters.
    each vowel / diphthong unit is a "seed" of a syllable; consonants and consonant groups "stick"
    to adjacent seeds. first make every vowel stick to its preceding consonant group. any remaining
    consonant groups stick to the vowel behind them.
    '''
    #

    # remove all whitespace and newlines from input:
    inp = re.sub(r'[\s+]', '', inp)

    # convert to lowercase. it would be possible to maintain letter case if we saved the original
    # input and then re-split it at the very end of this method, if that's desirable
    inp = str.lower(inp)

    if verbose:
        print('syllabifying {}'.format(inp))

    if len(inp) <= 1:
        return inp
    if inp == 'euouae':
        return 'e-u-o-u-ae'.split('-')
    if inp == 'cuius':
        return 'cu-ius'.split('-')
    if inp == 'eius':
        return 'e-ius'.split('-')
    if inp == 'iugum':
        return 'iu-gum'.split('-')
    if inp == 'iustum':
        return 'iu-stum'.split('-')
    if inp == 'iusticiam':
        return 'iu-sti-ci-am'.split('-')
    if inp == 'iohannes':
        return 'io-han-nes'.split('-')
    word = [inp]

    # for each unbreakable unit (consonant_groups and dipthongs)
    for unit in consonant_groups + diphthongs:
        new_word = []

        # check each segment of the word for this unit
        for segment in word:

            # if this segment is marked as unbreakable or does not have the unit we care about,
            # just add the segment back into new_word and continue
            if '*' in segment or unit not in segment:
                new_word.append(segment)
                continue

            # otherwise, we have to split this segment and then interleave the unit with the rest
            # this 'reconstructs' the original word even in cases where the unit appears more than
            # once
            split = segment.split(unit)

            # necessary in case there exists more than one example of a unit
            rep_list = [unit + '*'] * len(split)
            interleaved = [val for pair in zip(split, rep_list) for val in pair]

            # remove blanks and chop off last extra entry caused by list comprehension
            interleaved = [x for x in interleaved[:-1] if len(x) > 0]
            new_word += interleaved
        word = list(new_word)

    # now split into individual characters anything remaining
    new_word = []
    for segment in word:
        if '*' in segment:
            new_word.append(segment.replace('*', ''))
            continue
        # if not an unbreakable segment, then separate it into characters
        new_word += list(segment)
    word = list(new_word)

    # add marker to units to mark vowels or diphthongs this time
    for i in range(len(word)):
        if word[i] in vowels + diphthongs:
            word[i] = word[i] + '*'

    if verbose:
        print('split list: {}'.format(word))

    if not any(('*' in x) for x in word):
        return [''.join(word)]

    # begin merging units together until all units are marked with a *.
    escape_counter = 0
    while not all([('*' in x) for x in word]):

        # first stick consonants / consonant groups to syllables ahead of them
        new_word = []
        i = 0
        while i < len(word):
            if i + 1 >= len(word):
                new_word.append(word[i])
                break
            cur = word[i]
            proc = word[i + 1]
            if '*' in proc and '*' not in cur:
                new_word.append(cur + proc)
                i += 2
            else:
                new_word.append(cur)
                i += 1
        word = list(new_word)

        # then stick consonants / consonant groups to syllables behind them
        new_word = []
        i = 0
        while i < len(word):
            if i + 1 >= len(word):
                new_word.append(word[i])
                break
            cur = word[i]
            proc = word[i + 1]
            if '*' in cur and '*' not in proc:
                new_word.append(cur + proc)
                i += 2
            else:
                new_word.append(cur)
                i += 1
        word = list(new_word)

        if verbose:
            print('merging into syls:{}'.format(word))

        escape_counter += 1
        if escape_counter > 100:
            raise RuntimeError('input to syllabification script has created an infinite loop')

    word = [x.replace('*', '') for x in new_word]

    return word


def syllabify_text(input, verbose=False):
    words = input.split(' ')
    word_syls = [syllabify_word(w, verbose) for w in words]
    syls = [item for sublist in word_syls for item in sublist]
    return syls


if __name__ == "__main__":
    # fpath = "/Users/tim/Desktop/002v_transcript.txt"
    # with open(fpath) as f:
    #     ss = ' '.join(f.readlines())
    # res = syllabify_text(ss, True)
    # print(res)

    inp = 'quaecumque ejus michi antiphonum assistens alleluya dixit extra exhibeamus Es En xcvbnmzxcbvnm'
    res = syllabify_text(inp, True)
    print(res)
