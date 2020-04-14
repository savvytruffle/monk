#!/usr/bin/env python
# coding: utf-8

###############################################################################
# Converts formatting in bibtex files so each entry is tagged by SurnameYear 
# instead of default sequence... mostly because in papers it's easier to cite
# $> python monk.py input.bib output.bib
###############################################################################


import numpy as np
import re, sys


# from http://bib-it.sourceforge.net/help/fieldsAndEntryTypes.php#Entries
bibtex_entries = ['@ARTICLE', '@INBOOK', '@BOOK', '@BOOKLET', 
                 '@INCOLLECTION', '@INPROCEEDINGS', '@MANUAL',
                 '@MASTERSTHESIS', '@MISC', '@PHDTHESIS', 
                 '@PROCEEDINGS', '@TECHREPORT', '@UNPUBLISHED']

suffix = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
         'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y' ,'z']


def read_bib(fname):
    """Reads in .bib file"""
    print("Reading {}".format(fname))
    with open(fname, 'r') as bibfile:
        data = bibfile.read()
    return data

def get_entries(text, base_entries):
    """Counts number of entries for each base entry and identifies
    which entries have positive counts
    
    Parameters:
    text : str, input text
    base_entries : str or list of str, base entry expressions
    
    Returns:
    entries_count : array of int, number of counts in text for 
                                    each base entry
    which_entries : array of str, list of entries with + counts
    """
    entries_count = np.array([text.count(be) for be in base_entries])
    which_entries = np.array(base_entries)[entries_count>0]
    return entries_count, which_entries

def get_split_expr(which_entries):
    """Makes search expression for re.split"""
    split_expr = '('
    split_expr += '|'.join([str(we) for we in which_entries])
    split_expr += ')'
    return split_expr

def split_entries(text, split_expr):
    """Splits text into entries according to split expression"""
    return re.split(split_expr, text)[1:]

def edit_entries(x, which_entries):
    """Modifies citations in x such that each citation is tagged
    by first author's last name and year (e.g., Surname2020), 
    rather than default bibtex sequences """
    author_list = []
    ay_list = []
    xout = {}
#    common_latex_accents = ["{\`", "{\'", "{\^", "{\~", "{\=", 
#    						"{\.", "}"]
    for we in which_entries:
        xout.setdefault(we, []) 
        
    for ii in range(len(x))[::2]:
        Nchars = x[ii+1].find('author')
        replace_segment = x[ii+1][1:Nchars]
        first_author = x[ii+1][Nchars:].split(",")[0].strip("author = {{").strip("}")
        first_author = re.sub(r'[^a-zA-Z\-]', '', first_author)
        #first_author = x[ii+1][Nchars:].split(",")[0].strip("author = ")
#        for cla in common_latex_accents:
#                first_author = first_author.replace(cla, "")
        author_list.append(first_author)
        year = replace_segment[:4]
        replace_with = first_author+year
        ay_list.append(replace_with)
        author_count = ay_list.count(replace_with)
        if author_count>1:
            replace_with += suffix[author_count-1]
        replace_with += ',\n        '
        newstuff = x[ii+1].replace(replace_segment, replace_with)
        xout[x[ii]].append(x[ii]+newstuff)
    return author_list, ay_list, xout

def write_bib(fname, xout):
    """Writes out bib file"""
    print("Writing to {}".format(fname))
    with open(fname, 'w') as newbibfile:
        for we in xout.keys():
            newbibfile.write("\n".join([blurb for blurb in xout[we]]))
    return

def find_indices(text, expr):
    """Identify indices where search expression (expr) 
    occurs in base expression (text)"""
    places = []
    i = text.find(expr)
    while i>=0:
        places.append(i)
        i = text.find(expr, i + 1)
    return places

def main(infile, outfile=None):
    if outfile is None:
        outfile = 'new_'+infile
    data = read_bib(infile)
    entries_count, which_entries = get_entries(data, bibtex_entries)
    split_expr = get_split_expr(which_entries)
    print("Converting {} entries from default to SurnameYear format & removing non-alphanumeric sequences".format(" ".join([we for we in which_entries])))
    data2 = split_entries(data, split_expr)
    author_list, ay_list, outdata = edit_entries(data2, which_entries)
    write_bib(outfile, outdata)


if __name__ == "__main__":
    main(*sys.argv[1:])
