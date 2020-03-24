import argparse
import math
import re
import glob
import os
import nltk
import spacy
from spacy import displacy
from collections import Counter
from collections import OrderedDict
from spacy.pipeline import EntityRuler


#Had to add some exceptions b/c Spacy's model isn't perfect. These are specific to my test files in the docs/ folder.
nlp = spacy.load("en_core_web_sm")
ruler = EntityRuler(nlp, overwrite_ents=True)
patterns = [{"label": "PERSON", "pattern": "Secretary of State"},
            {"label": "PERSON", "pattern": [{"LOWER": "secretary"}, {"LOWER": "of state"}]},
            {"label": "PERSON", "pattern": "Sanders"},
            {"label": "PERSON", "pattern": "Peter F. Nardulli"},
            {"label": "PERSON", "pattern": "Hillary Clinton"},
            {"label": "ORG", "pattern": "Charlotte Hornets"}]

ruler.add_patterns(patterns)
nlp.add_pipe(ruler)

myFileNames = []
myRedactList = []



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


#nltk.download('punkt')
#Need a global variable myFileNames, accessible to all the methods.



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


def findNames(document, nameFlag):

    if not nameFlag:
        return

    # Step 1, use Spacy's en-core-web-lg module to identify Named Entites.
    # Step 2, add all People to the Redaction list.
    doc = nlp(document)

    for ent in doc.ents:
        #print(ent.text, ent.label_)
        foundNP = False
        if ent.label_ == "PERSON":
            pattern = re.compile(ent.text)
            for noun_chunks in doc.noun_chunks:
                #print(noun_chunks.text)
                if pattern.search(noun_chunks.text):
                    myRedactList.append(noun_chunks.text)
                    foundNP = True

            if not foundNP:
                myRedactList.append(ent.text)
        #elif ent.label_ == "ORG":
          #  myRedactList.append(ent.text)

    #This clears out duplicates.
    newList = list(OrderedDict.fromkeys(myRedactList))
    myRedactList.clear()
    for x in range(0, len(newList)):
        myRedactList.append(newList[x])
    #print(myRedactList)



def findGenders(document, genderFlag, nameFlag):
    if not genderFlag:
        return
    pass

# Some of the Male and Female words were taken from
# https://medium.com/@rajat.jain1/natural-language-extraction-using-spacy-on-a-set-of-novels-88b159d68686
# and https://www.thefreedictionary.com/List-of-pronouns.htm


    female_words = ["she", "her", "hers", "herself", "actress", "bachelorette", "empress", "queen", "heroine", "hostess",
                'mrs', 'ms', 'miss', 'lady', 'madameoiselle', 'baroness', 'mistress', 'queen',
                'princess', 'madam', 'madame', "landlady", "stewardess", "waitress", "girl", "bride", "sister", "mum",
                "mom", "mommy", "duchess", "woman", "mother", "goddess", "grandmother", "heiress", "heroine", "wife",
                "queen", "babe", "mistress", "niece", "policewoman", "saleswoman", "princess", "daughter", "aunt",
                "auntie", "witch", "grandma", "lass", "lassie", "girlie"]

    male_words = ['mr', 'sir', 'monsieur', 'captain', 'chief', 'master', 'lord', 'baron', 'mister', 'prince', 'king',
              "he", "him", "his", "himself", "actor", "bachelor", "emperor", "hero", "host", "landlord", "steward",
              "waiter", "fireman", "policeman", "mailman", "salesman", "boy", "male", "man", "dad", "daddy", "duke",
              "father", "god", "grandfather", "heir", "husband", "master", "nephew", "prince", "son", "uncle", "wizard",
              "grandpa", "pa", "pappy", "warlock", "lad", "laddie", "chap", "fella", "dude", "bro"]

    # Assume all names are Gendered, or would giveaway the gender. Just call findNames here to be safe.
    # No need to call it if its already been called.
    if not nameFlag:
        findNames(document, True)

    for word in female_words:
        myStr = r"\b" + word + r"\b"
        pattern = re.compile(myStr)
        if pattern.search(document):
            myRedactList.append(word)

    for word in male_words:
        myStr = r"\b" + word + r"\b"
        pattern = re.compile(myStr)
        if pattern.search(document):
            myRedactList.append(word)

    #Now time for some clean-up.
    # This clears out duplicates.
    newList = list(OrderedDict.fromkeys(myRedactList))
    myRedactList.clear()
    for x in range(0, len(newList)):
        myRedactList.append(newList[x])
    #print(myRedactList)







def findDates(document, dateFlag):
    if not dateFlag:
        return
    pass

def findConcepts(document, conceptFlag):
    if not conceptFlag:
        return
    pass

def printDoc(document):
    pass

def runStats():
    pass

def redact(document):

    # We sort our redactList by length. This ensures that the longer names like "President Donald Trump" get redacted
    # before "Trump". This is important because we are doing the replacements with regex, so if "Trump" is turned into
    # \u2588 then regex, won't find the longer form if the shorter form was redacted first. Not the most elegant
    # solution, but it works for now.

    sortRedact = sorted(myRedactList, key=len, reverse = True)
    print(sortRedact)


    for x in range(0,len(sortRedact)):

        sortRedact[x] = re.escape(sortRedact[x])
        myStr = r"\b" + sortRedact[x] + r"\b"
        pattern = re.compile(myStr)
        document = pattern.sub("\u2588", document)

    #If two redactions occur next to each other, turn it into one block. This helps further protect our document.
    twoBlocks = re.compile("\u2588" + " " + "\u2588")
    document = twoBlocks.sub("\u2588", document)

    return document













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

    findNamesFlag = True
    findGendersFlag = True

    fileext = "*.txt"
    findDocs(fileext)
    print(myFileNames)

    if(myFileNames):
        myNews1 = open(myFileNames[2], 'r', encoding="UTF-8")
        myNews = myNews1.read()
        myNews1.close()

    findNames(myNews, findNamesFlag)
    findGenders(myNews, findGendersFlag, findNamesFlag)
    redactNews = redact(myNews)

    block = "\u2588"


    print(redactNews)







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
