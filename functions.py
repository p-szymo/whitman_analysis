import pandas as pd


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
