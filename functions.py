import pandas as pd
import string
import pronouncing as pr


def string_adder(source, orig, start_index, end_index):

    '''
    Function to combine several strings into one and remove the strings
    that were part of the combination.

    Input
    -----
    source : list (str)
        A list of strings to combine.

    orig : int
        Index of the beginning of the poem.

    start_index : int
        Index of the first list item to add to orig.

    end_index : int
        Index of the last list item to add to orig.


    Output
    ------
    corrected : str
        Single string of the combined poem.

    NOTE: Overwrites `source` by deleting strings between `start_index`
    and `end_index`.


    '''

    # create list of all the strings to combine
    orig_list = [source[orig]] + source[start_index:end_index+1]

    # join into single string
    corrected = '\n\n'.join(orig_list)

    # delete no longer necessary strings from input list
    del source[start_index:end_index+1]

    return corrected


# clean up poem formatting
def line_creator(poem):

    '''
    Function to convert poem as a string into a poem as a list
    of lines.


    Input
    -----
    poems : str
        Poem to be converted.


    Output
    ------
    poem_lines : list (str)
        List of strings without whitespace or empty strings.

    '''

    return [line.strip() for line in poem.split('\r\n') if line]


def part_splitter(df, index, column):

    '''
    Function to split multi-part poem into a list of dictionaries,
    with each item being a part of the original poem.

    Input
    -----
    df : Pandas DataFrame
        Source DataFrame.

    index : int
        Actual (not positional) index number of the row with poem to transform.

    column : str
        Name of column containing list of poem lines.


    Output
    ------
    parts : list (dict)
        Individual poem parts, containing title, list of lines, and poem
        as a string.


    '''

    # empty list for dictionaries
    parts = []

    # loop over poem lines list
    for i, line in enumerate(df.loc[index, column]):

        # line with only numbers
        if line.isdecimal():

            # for all but first (0) index, append now-complete dictionary for
            # previous part
            if i:
                # join list to string
                parts_dict['poem_string'] = '\r\n '.join(
                                                parts_dict['poem_lines'])
                # append dictionary
                parts.append(parts_dict)

            # start new dictionary
            parts_dict = {}
            # create new part title
            parts_dict['title'] = f'{df.loc[index, "title"]}: Part {line}'
            # start list of poem lines
            parts_dict['poem_lines'] = []

        # actual line of poetry
        else:
            # append to list of poem lines
            parts_dict['poem_lines'].append(df.loc[index, column][i])

    # join final list of poem lines
    parts_dict['poem_string'] = '\r\n '.join(parts_dict['poem_lines'])

    # append final dictionary
    parts.append(parts_dict)

    return parts


def part_adder(df, index, column, drop=False, reset_index=False):

    '''
    Function to add poem parts (as a list of dictionaries) to the bottom
    of a DataFrame, with optional settings to drop row with original
    (multi-part) poem and reset the index of the transformed DataFrame.


    Input
    -----
    df : Pandas DataFrame
        Source DataFrame.

    index : int
        Actual (not positional) index number of the row with poem to transform.

    column : str
        Name of column containing list of poem lines.


    Optional input
    --------------
    drop : bool
        Whether to drop original (multi-part) poem from transformed DataFrame
        (default=False).

    reset_index : bool
        Whether to reset indices of transformed DataFrame (default=False).


    Output
    ------
    parts : list (dict)
        Individual poem parts, containing title, list of lines, and poem
        as a string.


    '''

    # split multi-part poems into parts
    parts = part_splitter(df, index, column)

    # add parts onto original dataframe
    df_added = df.append(pd.DataFrame(
                # set indices to continue sequentially from original dataframe
                parts, index=range(len(df), len(df)+len(parts))))

    if drop:
        # drop multi-part version
        df_added.drop(index=index, inplace=True)

    # reset index (optional)
    if reset_index:
        df_added.reset_index(drop=True, inplace=True)

    return df_added


# count number of words in a text
def word_counter(lines):

    '''
    Function to count the number of words in a list of strings.


    Input
    -----
    lines : list (str)
        List of strings to count.


    Output
    ------
    word_count : int
        Total number of words across all strings.

    '''

    # calculate the number of words per line
    line_count = [len(line.split()) for line in lines]

    # add up the word counts of each line
    word_count = sum(line_count)

    return word_count


def unique_word_counter(lines):

    '''
    Function to count the number of unique words in a list of
    strings.


    Input
    -----
    lines : list (str)
        List of strings to count.


    Output
    ------
    num_unique : int
        Total number of unique words across all strings.

    '''

    # lowercase all words, remove punctuation and en dashes
    process_lines = [line.lower().replace('—', ' ').
                     translate(str.maketrans('', '', string.punctuation))
                     for line in lines]

    # list of all words
    words = [word for line in process_lines
             for word in line.split()]

    # number of unique words
    num_unique = len(set(words))

    return num_unique


# count number of end rhymes in a text
def end_rhyme_counter(lines):

    '''
    Function to count the instances of rhymes that occur among
    the last words in lines (end rhymes).


    Input
    -----
    lines : list (str)
        List of strings to compare.


    Output
    ------
    sum(rhyme_counts) : int
        The number of end rhymes.

    '''

    # instantiate an empty dictionary
    rhyme_dict = {}

    # make a list of words at the end of the line
    end_words = [line.split()[-1].translate
                 (str.maketrans('', '', string.punctuation))
                 for line in lines]

    # loop to build the dictionary
    for word in end_words:
        for i in range(len(end_words)):

            # check if a word rhymes with another word in the list
            if end_words[i] in pr.rhymes(word):

                # check if word is already a key in the dictionary
                if word not in rhyme_dict:

                    # or if its rhyming word is already a key
                    # in the dictionary
                    if end_words[i] not in rhyme_dict:

                        # if neither is, create the word as key and
                        # it's rhyme as a value (in a list)
                        rhyme_dict[word] = [end_words[i]]

                else:
                    # if word is already a key, append its rhyme to
                    # its value
                    rhyme_dict[word].append(end_words[i])

    # count up the amount of (unique) rhymes per word
    rhyme_counts = [len(rhyme) for rhyme in rhyme_dict.values()]

    return sum(rhyme_counts)


# count total syllables in text
def syllable_counter(lines):

    '''
    Function to count all syllables in a list of strings.

    NOTE: This does not factor in multi-syllabic digits,
    times (i.e. 1:03), and most likely other non-"word" words.


    Input
    -----
    lines : list (str)
        List of strings to count.


    Output
    ------
    sum(total) : int
        Total number of syllables in the input list.



    [Modified from Allison Parrish's example in the documention
     for her library, pronouncing]:
    https://pronouncing.readthedocs.io/en/latest/tutorial.html

    '''
    # create empty list
    total = []

    # loop over list
    for line in lines:

        # turn each word into a string of its phonemes
        # if else statement ensures that each word is counted with
        # at least one syllable, even if that word is not in the
        # pronouncing library's dictionary (using phoneme for 'I'
        # as a placeholder for single syllable)
        phonemes = [pr.phones_for_word(word)[0]
                    if pr.phones_for_word(word)
                    else 'AY1' for word in line.split()]

        # count the syllables in each string and add the total
        # syllables per line to the total list
        total.append(sum([pr.syllable_count(phoneme)
                          for phoneme in phonemes]))

    # return the total number of syllables
    return sum(total)
