#!/bin/env python
# -*- coding: utf-8 -*-

import re
import pandas as pd
import itertools
from collections import Counter

# german stemming, many are repeats with different endings and such
# remove names
# not sure how accurate the book is, some mistakes including Ho gwarts on page 105, Lred
# non-dictionary words like undurselyhaft, aaaargh
# very slight differences, but same number of pages

# test suite
# lines 145 for quotes
# first line for periods

'''
see format_harry_poter doc string for info on how book text needs to be formatted
'''

class Book(object):
    '''
    attributes
    ---------
    pages:            list of pages, where each page is a list of words on that page.
    known_words:      optional list of words already learned
    word_list:        ordered list of all words in book, duplicates included
    total_words:      total number of words in book, duplicated included
    word_set:         set of all unique words in book
    num_unique_words: number of unique words in book
    word_data:        pandas data frame containing data for each word, columns described below
        index - word in lower case
        count - number of occurences of word in book
        learned - whether or not word has been learned (based on known_words list)
        page - page number of first occurence of word
    '''
    def __init__(self, pages, known_words=[]):
        self.pages = pages
        self.known_words = known_words
        self.word_list = list(itertools.chain.from_iterable(pages))
        self.total_words = len(self.word_list)
        self.word_set = set(self.word_list)
        self.num_unique_words = len(self.word_set)
        self.word_data = self._initialize_data_frame()
        self._set_known_words()    
        self._set_page_numbers()
        print 'Total number of words: ', self.total_words
        print 'Number of unique words: ', self.num_unique_words

    def _initialize_data_frame(self):
        df = pd.DataFrame.from_dict(Counter(self.word_list), orient='index')
        df = df.rename(columns={'index':'word', 0:'count'}).sort_values('count', ascending=False)
        return df
    
    def _set_known_words(self):
        '''says whether word has been learned based on known_words list'''
        '''may break if learned word isn't in harry potter?'''
        self.word_data['learned'] = False
        known_words_in_book = [w for w in self.known_words if w in self.word_data.index.values]
        self.word_data.loc[known_words_in_book, 'learned'] = True
        
    def _set_page_numbers(self):
        '''shows first page on which word appears'''
        self.word_data['page'] = -1
        for i, page in enumerate(self.pages):
            for word in page:
                if self.word_data.loc[word, 'page'] == -1:
                    self.word_data.loc[word, 'page'] = i+1
            

def read_known_word_list(filename):
    with open(filename) as f:
        known_words = f.readlines()
    known_words = [word.lower().strip().decode("utf-8") for word in known_words]
    return known_words

def format_harry_potter(filename):
    '''
    WARNING: this only works because of the unique way
    Harry Potter und der Stein der Weisen was formatted when I downloaded it.
    It will not work for other books, unless they happen to have same formatting

    To use other books, you want to write a similar method to this that will
    format your text so you have a list of "pages"
    where each page is a list of words on that page in order, eg
    [['Mr', 'und', 'Mrs', ...], ... , ['words', 'on', 'last', 'page', ...]]

    To make things simpler, you can put all the words on one page, but you will
    lose the page number meta-data. That would look like:
    [['Mr', 'und', 'Mrs Dursley', ..., 'words', 'on', 'last', 'page', ...]]
    (it needs to be a list of one list, not a single list of words, see double brackets)

    the words my need to be unicode but I'm not sure
    '''
    # read in text, excluding blank lines
    with open(filename) as f:
        raw_text = [line for line in f if not line.isspace()]

    # split into pages, exploiting page numbers printed in text
    pages = [] # initialize
    start_line = 0   # intitialize for first page
    for i,line in enumerate(raw_text):
        if len(line.split())==1 and line[0].isdigit():
            page_number = line
            end_line = i
            pages.append(raw_text[start_line:end_line])
            start_line = end_line+1  # update start_line for next page

    # if page ends in hyphen bring second half of chopped word back from next page   
    pages_copy = pages[:]  # slice to make copy
    for i, page in enumerate(pages_copy):
        last_line_on_page = page[-1]
        last_word = last_line_on_page.split()[-1] 
        # if page ends in hyphen, 
        if last_word[-1] == '-': 
            # grab second fragment of word form next page and append
            second_word_fragment = pages[i+1][0].split()[0] 
            new_last_word = last_word[0:-1] + second_word_fragment
            new_last_line = last_line_on_page.split()[0:-1] + [new_last_word]
            pages[i][-1] = " ".join(new_last_line)
            # delete fragment from next page
            pages[i+1][0] = " ".join(pages[i+1][0].split()[1:])
            
    # if line end in hyphen bring fragment from next line and move word to next line
    # (move to next line to avoid empty lines)
    pages_copy = pages[:]  # slice to make copy
    for j, page in enumerate(pages_copy):
        for i, line in enumerate(page):
            last_word = line.split()[-1]
            # if page ends in hyphen,
            if last_word[-1] == '-':
                # grab second fragment of word form next line and append to beginning
                # of next line
                second_word_fragment = page[i+1].split()[0]
                new_first_word = last_word[0:-1] + second_word_fragment
                new_line = [new_first_word] + page[i+1].split()[1:] 
                pages[j][i+1] = " ".join(new_line)
                # delete fragment from end of this line
                pages[j][i] = " ".join(line.split()[0:-1])

    # split each page into unicode words 
    pages_copy = pages[:]  # slice to make copy
    for i, page in enumerate(pages_copy):
        page_tmp = " ".join(page)
        page_tmp = re.findall("\w+", page_tmp.decode("utf-8"), re.U)
        pages[i] = [word.lower() for word in page_tmp]

    return [[],[],[],[]] + pages   # add 4 blank pages to match book
