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