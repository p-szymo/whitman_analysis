import pandas as pd
import string
import pronouncing as pr

# nlp packages
import nltk
from nltk import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
# from nltk.corpus import stopwords
from nltk.corpus import wordnet
# from textblob import TextBlob as tb


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


# contractions conversions
def load_dict_contractions():

    '''
    Dictionary of contractions as keys and their expanded words
    as values.


    [Code modified from]:
    https://stackoverflow.com/questions/19790188/expanding-english-\
    language-contractions-in-python

    '''

    return {
        "ain't": "is not",
        "amn't": "am not",
        "aren't": "are not",
        "can't": "cannot",
        "can't've": "cannot have",
        "'cause": "because",
        "cuz": "because",
        "couldn't": "could not",
        "couldn't've": "could not have",
        "could've": "could have",
        "daren't": "dare not",
        "daresn't": "dare not",
        "dasn't": "dare not",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "d'you": "do you",
        "e'er": "ever",
        "em": "them",
        "'em": "them",
        "everyone's": "everyone is",
        "finna": "fixing to",
        "gimme": "give me",
        "gonna": "going to",
        "gon't": "go not",
        "gotta": "got to",
        "hadn't": "had not",
        "hadn't've": "had not have",
        "hasn't": "has not",
        "haven't": "have not",
        "he'd": "he would",
        "he'd've": "he would have",
        "he'll": "he will",
        "he'll've": "he he will have",
        "he's": "he is",
        "how'd": "how would",
        "how'll": "how will",
        "how're": "how are",
        "how's": "how is",
        "i'd": "i would",
        "i'd've": "i would have",
        "i'll": "i will",
        "i'll've": "i will have",
        "i'm": "i am",
        "i'm'a": "i am about to",
        "i'm'o": "i am going to",
        "isn't": "is not",
        "it'd": "it would",
        "it'd've": "it would have",
        "it'll": "it will",
        "it'll've": "it will have",
        "it's": "it is",
        "i've": "i have",
        "kinda": "kind of",
        "let's": "let us",
        "ma'am": "madam",
        "mayn't": "may not",
        "may've": "may have",
        "mightn't": "might not",
        "mightn't've": "might not have",
        "might've": "might have",
        "mustn't": "must not",
        "mustn't've": "must not have",
        "must've": "must have",
        "needn't": "need not",
        "needn't've": "need not have",
        "ne'er": "never",
        "o'": "of",
        "o'clock": "of the clock",
        "o'er": "over",
        "ol'": "old",
        "oughtn't": "ought not",
        "oughtn't've": "ought not have",
        "shalln't": "shall not",
        "shan't": "shall not",
        "shan't've": "shall not have",
        "she'd": "she would",
        "she'd've": "she would have",
        "she'll": "she will",
        "she'll've": "she will have",
        "she's": "she is",
        "shouldn't": "should not",
        "shouldn't've": "should not have",
        "should've": "should have",
        "so's": "so as",
        "so've": "so have",
        "somebody's": "somebody is",
        "someone's": "someone is",
        "something's": "something is",
        "that'd": "that would",
        "that'd've": "that would have",
        "that'll": "that will",
        "that're": "that are",
        "that's": "that is",
        "there'd": "there would",
        "there'd've": "there would have",
        "there'll": "there will",
        "there're": "there are",
        "there's": "there is",
        "these're": "these are",
        "they'd": "they would",
        "they'd've": "they would have",
        "they'll": "they will",
        "they'll've": "they will have",
        "they're": "they are",
        "they've": "they have",
        "this's": "this is",
        "those're": "those are",
        "to've": "to have",
        "'tis": "it is",
        "tis": "it is",
        "'twas": "it was",
        "twas": "it was",
        "wanna": "want to",
        "wasn't": "was not",
        "we'd": "we would",
        "we'd've": "we would have",
        "we'll": "we will",
        "we'll've": "we will have",
        "we're": "we are",
        "weren't": "were not",
        "we've": "we have",
        "what'd": "what did",
        "what'll": "what will",
        "what'll've": "what will have",
        "what're": "what are",
        "what's": "what is",
        "what've": "what have",
        "when's": "when is",
        "when've": "when have",
        "where'd": "where did",
        "where're": "where are",
        "where's": "where is",
        "where've": "where have",
        "which's": "which is",
        "will've": "will have",
        "who'd": "who would",
        "who'd've": "who would have",
        "who'll": "who will",
        "who'll've": "who will have",
        "who're": "who are",
        "who's": "who is",
        "who've": "who have",
        "why'd": "why did",
        "why're": "why are",
        "why've": "why have",
        "why's": "why is",
        "won't": "will not",
        "won't've": "will not have",
        "wouldn't": "would not",
        "wouldn't've": "would not have",
        "would've": "would have",
        "y'all": "you all",
        "y'all'd": "you all would",
        "y'all'd've": "you all would have",
        "y'all're": "you all are",
        "y'all've": "you all have",
        "you'd": "you would",
        "you'd've": "you would have",
        "you'll": "you will",
        "you'll've": "you will have",
        "you're": "you are",
        "you've": "you have",
        }


# obtain POS tags
def get_wordnet_pos(word):

    '''
    Function to map part-of-speech tag to first character
    lemmatize() accepts.


    Input
    -----
    word : str
        Word to tag.


    Output
    ------
    tag : wordnet object
        POS tag in the necessary format for WordNetLemmatizer().



    [Code borrowed from]:
    https://www.machinelearningplus.com/nlp/lemmatization-examples-python/

    '''

    # get primary tag
    tag = nltk.pos_tag([word])[0][1][0].upper()

    # proper format conversion dictionary
    tag_dict = {'J': wordnet.ADJ,
                'N': wordnet.NOUN,
                'V': wordnet.VERB,
                'R': wordnet.ADV}

    # tag, if known; use noun if unknown
    return tag_dict.get(tag, wordnet.NOUN)


# apply text cleaning techniques
def clean_text(text, stop_words):

    '''
    Function to make text lowercase, tokenize words and words with
    apostrophes, convert contractions to full words, lemmatize by
    POS tag, and remove stop words and words shorter than 3
    characters.


    Input
    -----
    text : str
        Text to be cleaned.

    stop_words : list (str)
        List of words to remove from the text.


    Output
    ------
    text : str
        Lowercase, lemmatized text without contractions, stop words,
        and one- to two-letter words.

    '''

    # make text lowercase and convert some punctuation
    text = text.lower().replace("’", "'").replace('—', ' ').\
        replace('-', ' ')

    # remove punctuation other than apostrophes
    text = text.translate(str.maketrans(
        '', '', string.punctuation.replace("'", "")))

    # initial tokenization to remove non-words
    tokenizer = RegexpTokenizer("([a-z]+(?:'[a-z]+)?)")
    words = tokenizer.tokenize(text)

    # convert contractions
    contractions = load_dict_contractions()
    words = [contractions[word] if word in contractions else
             word for word in words]

    # stringify and remove leftover apostrophes
    text = ' '.join(words)
    text = text.replace("'", "")

    # remove stop words, lemmatize using POS tags,
    # and remove two-letter words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word, get_wordnet_pos(word))
             for word in nltk.word_tokenize(text)
             if word not in stop_words]

    # removing any words that got lemmatized into a stop word
    words = [word for word in words if word not in stop_words]

    # removing words less than 3 characters
    words = [word for word in words if len(word) > 2]

    # rejoin into a string
    text = ' '.join(words)

    return text
