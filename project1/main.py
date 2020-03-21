import argparse
import math
import re
import glob
import os
import nltk
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()


#This project needs to:
# 1 - Accept a *.txt or *.md input (or both) and find all the .txt or .md files in the project folder.
# 2 - Read the file(s) and redact (Store in a list?) all words and related words to the provided flags,
#     'names', 'genders', and 'dates'.
# 3 - Redact all words and related words from the provided 'concept' flag(s) - can use word matrices from Spacy.
#     1 method call for each provided concept flag.
# 4 - Double-check sentences, redact full sentences if the meaning is still clear. How, not sure yet. Optional for now.
# 5 - Actually replace all redacted words with either a single Block U+2588 character, or multiple block characters.
# 6 - Output the redacted files to a folder provided by the user (or default to output/ if none provided)
# 7 - Generate a statistics function, which prints information about the run to stdout, stderr, or a file.
# 8 - Write tests for each method in seperate test_etc.py files.



#Need a global variable myFileNames, accessible to all the methods.
myFileNames = []


def findDocs(userglob):
    # This function takes in a glob like *.txt and appends a list of all the file names with that extention it can find.
    myInput = userglob

    if myInput == '*.txt':
        myPattern = re.compile(r'\.txt')
    elif myInput == "*.md":
        myPattern = re.compile(r'\.md')
    else:
        raise NameError("Sorry, the --input glob was neither *.txt or *.md")

    for files in os.walk(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        for items in files[2]:
            myMatch = re.search(myPattern, items)
            if myMatch:
                currentFilePath = (files[0] + '\\' + items)
                myFileNames.append(currentFilePath)


def redactNames(document):

    # I guess step1 is to use NLTK on the provided document to split the string into words.
    #Then we will classify them as Names or Not Names
    #Then I will add all the strings to-be-redacted to a list. This can be a running list between methods.

    #document input must be a string.
    tokens = nltk.word_tokenize(document)
    print(tokens)
    










#
# parser = argparse.ArgumentParser(description="Calculate volume of a cylinder")
# parser.add_argument('--radius', type=int, help='Radius of Cylinder')
# parser.add_argument('--height', type=int, help='Height of Cylinder')
# args = parser.parse_args()

#
# def cylinder_volume(radius, height):
#    vol = (math.pi) * (radius ** 2) * (height)
#    return vol




if __name__ == '__main__':
    #
    # What I want is a list of document names. I can accept an input *.txt, and I want to find all the strings
    # "news1, news2, etc. and make them into a list, which I can then cycle through when using nltk and spacy.

    fileext = "*.txt"
    findDocs(fileext)
    print(myFileNames)

    if(myFileNames):
        myNews1 = open(myFileNames[1], 'r', encoding="UTF-8")
        myNews = myNews1.read()
        myNews1.close()

    redactNames(myNews)

    block = "\u2588"
    #match = re.compile("the ")
    #match2 = re.compile("coronavirus")
    #match3 = re.compile(block + " " + block)
    #redactNews = match.sub(block + " ", myNews)
    #redactNews = match2.sub(block, redactNews)
    #redactNews = match3.sub(block, redactNews)
    print(myNews)
    #print(redactNews)







    #print(myFileNames)
    #print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
# def main():
# 	pass
#
#

#
# 	#The required arguments will be:
# 	#--input (glob*.txt or glob.md) --names --dates --concept (str) --output (folder/) --stats (stderr, stdout, or filename)
#
#     parser.add_argument("--input", type=glob, required=True,
#                          help="A glob (*.fileextention) that you want to search for. Only supports .txt and .md files for now.")
#     parser.add_argument("--names", required=False,
# 						 help="An optional flag if you want to remove all names of people from the document. Cannot whitelist names currently.")
# 	parser.add_argument("--dates", required=False,
# 						 help="An optional flag if you want to remove all the dates from the document."
# 	parser.add_argument("--concept", type=str, required=False,
# 						 help="An optional flag which removes all words or phrases associated with a particular concept, like 'jail'. Uses a clustering algorithm and redacts related words and phrases to the provided string."
# 	parser.add_argument("--output", type=folder, required=False,
# 						 help="An optional flag if you want to specify which folder will be used to deposit output files. Default is the current directory."
# 	parser.add_argument("--stats", type=stderr,stdout,or filename, required=False,
# 						 help="An optional flag if you want to specify where the run statistics will go. They default to stdout."
#
#     args = parser.parse_args()
#     if args:
#         main(args.input) #Not exactly sure how to call main here, with all args. Need to watch a video or something on the argparse module.
#
