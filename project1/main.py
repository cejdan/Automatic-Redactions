# This is Project 1 for the Spring 2020 Text Analytics class
# Written by Nicholas Cejda
# Student ID: 113825637


import argparse
import math
import re
import glob
import os
import nltk
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from collections import Counter
from collections import OrderedDict
from spacy.pipeline import EntityRuler


#Had to add some exceptions b/c Spacy's model isn't perfect. These are specific to my test files in the docs/ folder.
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
ruler = EntityRuler(nlp, overwrite_ents=True)
patterns = [{"label": "PERSON", "pattern": [{"LOWER": "secretary"}, {"LOWER": "of state"}]},
            {"label": "PERSON", "pattern": "Sanders"},
            {"label": "PERSON", "pattern": "Peter F. Nardulli"},
            {"label": "PERSON", "pattern": "Hillary Clinton"},
            {"label": "ORG", "pattern": "Charlotte Hornets"}]

ruler.add_patterns(patterns)
nlp.add_pipe(ruler)

myFileNames = []

myRedactedDocs = []





#This project needs to:
# DONE 1 - Accept a *.txt or *.md input (or both) and find all the .txt or .md files in the project folder.
# 2 - Read the file(s) and redact (Store in a list?) all words and related words to the provided flags,
#     'names', 'genders', and 'dates'.
# 3 - Redact all words and related words from the provided 'concept' flag(s) - can use word matrices from Spacy.
#     1 method call for each provided concept flag.
# 4 - Double-check sentences, redact full sentences if the meaning is still clear. How, not sure yet. Optional for now.
# DONE 5 - Actually replace all redacted words with either a single Block U+2588 character, or multiple block characters.
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


def findTokenLocs(document, myToken):
    #Needs to return a list of all the places token hits in document. Ex, [[20:21],[300:301]]
    #This method only handles single tokens for now. Building it for the findGender method.
    doc = nlp(document)
    patternstr = [{'LOWER': str(myToken)}]
    matcher.add(str(myToken), None, patternstr)
    matches = matcher(doc)
    myMatchLocs = []
    for i in range(0,len(matches)):
        myMatchLocs.append([matches[i][1], matches[i][2]])
    matcher.remove(str(myToken))
    return myMatchLocs


def findNames(documents, nameFlag, fromGender):
    if not nameFlag:
        return

    # Step 1, use Spacy's en-core-web-lg module to identify Named Entites.
    # Step 2, add all People and their token locs to the Redaction list.

    for x in range(0, len(documents)):
        doc = nlp(documents[x])
        thisRedactList = []

        for ent in doc.ents:
            #print(ent.text, ent.label_)
            foundNP = False
            if ent.label_ == "PERSON":

                #Now is the time to find out what the token locations are for this span of tokens
                token_locs = [ent.start, ent.end]

                #pattern = re.compile(ent.text)
                for noun_chunks in doc.noun_chunks:
                    if noun_chunks.start <= ent.start and ent.end <= noun_chunks.end:
                        #print(noun_chunks.text)
                        token_locs = [noun_chunks.start, noun_chunks.end]
                        if fromGender:
                            mySmallList = [noun_chunks.text, token_locs, "Gender"]
                        else:
                            mySmallList = [noun_chunks.text, token_locs, "Names"]
                        thisRedactList.append(mySmallList)
                        foundNP = True

                if not foundNP:
                    if fromGender:
                        mySmallList = [ent.text, token_locs, "Gender"]
                    else:
                        mySmallList = [ent.text, token_locs, "Names"]

                    thisRedactList.append(mySmallList)

        if len(myRedactList) == len(documents):
            myRedactList[x].append(mySmallList)
        else:
            myRedactList.append(thisRedactList)


def findGenders(documents, genderFlag, nameFlag):

    if not genderFlag:
        return
    pass

# Some of the Male and Female words were taken from
# https://medium.com/@rajat.jain1/natural-language-extraction-using-spacy-on-a-set-of-novels-88b159d68686
# and https://www.thefreedictionary.com/List-of-pronouns.htm

    female_words = ["she", "her", "hers", "herself", "actress", "bachelorette", "empress", "heroine", "hostess",
        'mrs', 'ms', 'miss', 'lady', 'madameoiselle', 'baroness', 'mistress', 'queen',
        'madam', 'madame', "landlady", "stewardess", "waitress", "girl", "bride", "sister",
        "mom", "mommy", "duchess", "woman", "mother", "goddess", "grandmother", "heroine", "wife",
        "babe", "niece", "policewoman", "saleswoman", "princess", "daughter", "aunt",
        "witch", "grandma", "female"]

    male_words = ["he", "him", "his", 'mr', 'sir', 'monsieur', 'captain', 'chief', 'master', 'lord', 'baron', 'mister',
        'prince', 'king', "himself", "actor", "bachelor", "emperor", "host",
        "waiter", "fireman", "policeman", "mailman", "salesman", "boy", "male", "man", "dad", "daddy", "duke",
        "father", "god", "grandfather", "husband", "nephew", "son", "uncle", "wizard",
        "grandpa", "pa", "warlock", "chap", "fella", "dude", "bro"]

    gendered_words = female_words + male_words
    # Assume all names are Gendered, or would giveaway the gender. Just call findNames here to be safe.
    # No need to call it if its already been called.
    if not nameFlag:
        findNames(documents, True, True)

    for i in range(0,len(documents)):
        thisRedactList = []
        mySmallList = []
        for word in gendered_words:
            avacadotoast = findTokenLocs(documents[i], word)
            for j in range(0,len(avacadotoast)):
                token_locs = [avacadotoast[j][0],avacadotoast[j][1]]
                #print(word, avacadotoast[j][0],avacadotoast[j][1], "Gender")
                mySmallList = [word, token_locs, "Gender"]
                thisRedactList.append(mySmallList)

        if len(myRedactList) == len(documents) and len(thisRedactList) > 0:
            myRedactList[i].append(mySmallList)
        elif len(thisRedactList) > 0:
            myRedactList.append(thisRedactList)


def findDates(documents, dateFlag):
    if not dateFlag:
        return
    pass

def findConcepts(documents, concept, conceptFlag):
    if not conceptFlag:
        return
    pass



 #def outputDoc(fileNames, foldername = "output/"):

    #I should build a test here to make sure foldername is of the form folder/.


    #for i in range(0,len(fileNames)):
       # filename = os.path.basename(fileNames[i])
        #pathname = os.path.abspath()


         #report = open(foldername + 'redactedDocs.redacted', 'w')
         #report.write()
    # pass

def runStats():
    pass

def redact(documents):

    #  OK, Going to totally re-write this method. We want to use the TOKEN LOCs, found at:
    #  myRedactList[DOC i][RedactME j][TOKEN_LOC = 1][START(0) or STOP(1)]
    # And replace whatever tokens are there with a block.
    # Actually, we will use the original doc as a template, copying tokens and whitespace to a new file one by one until
    # we reach a BANNED token or token span. We won't write that or those tokens, we will instead write a single block.
    # Do I need to find all contigious sequences and mush them together? Probably.
    # Luckily sorting them is quick and easy with:
    #for x in range(0, len(myRedactList)):
    #    fileRedactList = myRedactList[x]
    #    redactme = sorted(fileRedactList, key=lambda start_token: start_token[1][0])
    #    Proceed with redaction using the redactme sorted list as your banned tokens.
    # When redacting I can check if token.end[i] == token.start[i+1], these are uninterrupted redaction blocks.
    # Turn the whole thing (could be as large as a whole sentence) into one single block. "\u2588"


    redactMe = []
    for i in range(0, len(myRedactList)):
        fileRedactList = myRedactList[i]
        redactTemp = sorted(fileRedactList, key=lambda start_token: start_token[1][0])
        redactMe.append(redactTemp)
    print(redactMe)
    for i in range(0,len(documents)):
        doc = nlp(documents[i])
        redact_positions = []
        mydoc = ""

        #This loop is designed to resolve all adjacent banned token spans. If two or more tokens,
        # say token 323:324 and 324:329 are both found, then we end up with just 323:329.
        j = 0
        while(j < len(redactMe[i])):
            redact_start = redactMe[i][j][1][0] #Just a regular int at this point.
            redact_end = redactMe[i][j][1][1]
            chunk_resolved = False
            while not chunk_resolved:
                if j < len(redactMe[i])-1 and redact_end == redactMe[i][j+1][1][0]:
                    redact_end = redactMe[i][j+1][1][1]
                    j = j + 1
                else:
                    chunk_resolved = True
            redact_positions.append([redact_start,redact_end])
            j = j + 1

        #From here, I can use my redact_start and redact_end as my banned token spans to reconstruct the document.


        write_start = 0
        write_end = redact_positions[0][0] #This is the first banned token position. Might be 0, that's ok.
        for j in range(0,len(redact_positions)):
            mydoc = mydoc + doc[write_start:write_end].text_with_ws
            mydoc = mydoc + "\u2588 " #Single block for the entire redacted section will do, highly protected this way.

            write_start = redact_positions[j][1] #This is the previous redact_end.
            if j == len(redact_positions)-1:
                break
            else:
                write_end = redact_positions[j+1][0] #This is the next redact_start. Basically, write_start:write_end spans the non-banned section.

        if redact_positions[len(redact_positions)-1][1] < len(doc):
            # We need to write one more time if the last token isn't on the redaction list.
            write_end = len(doc)
            mydoc = mydoc + doc[write_start:write_end].text_with_ws


        myRedactedDocs.append(mydoc)


if __name__ == '__main__':


    findNamesFlag = True
    findGendersFlag = False

    fileext = "*.txt"
    findDocs(fileext)
    print(myFileNames)
    unredactedDocs = []

    if(myFileNames):
        for x in range(0,len(myFileNames)):
            myFile1 = open(myFileNames[x], 'r', encoding="UTF-8")
            unredactedDocs.append(myFile1.read())
            myFile1.close()

    myRedactList = []
    findNames(unredactedDocs, findNamesFlag, False)


    findGenders(unredactedDocs, findGendersFlag, findNamesFlag)
    print(myRedactList)
    redact(unredactedDocs)
    print(myRedactedDocs[1])


    #for x in range(0,len(myRedactedDocs)):
    #    print(myRedactedDocs[x])

