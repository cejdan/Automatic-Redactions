# This is Project 1 for the Spring 2020 Text Analytics class
# Written by Nicholas Cejda
# Student ID: 113825637

from __future__ import print_function
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
import pandas as pd
import sys




#Had to add some exceptions b/c Spacy's model isn't perfect. These are specific to my test files in the docs/ folder.
#ruler = EntityRuler(nlp, overwrite_ents=True)
#patterns = [{"label": "PERSON", "pattern": [{"LOWER": "secretary"}, {"LOWER": "of state"}]},
#            {"label": "PERSON", "pattern": "Sanders"},
#            {"label": "PERSON", "pattern": "Peter F. Nardulli"},
#            {"label": "PERSON", "pattern": "Hillary Clinton"},
#            {"label": "ORG", "pattern": "Charlotte Hornets"}]

#ruler.add_patterns(patterns)
#nlp.add_pipe(ruler)


#GLOBAL VARIABLES!
myFileNames = []
myRedactedDocs = []
nlp = spacy.load("en_core_web_md")
matcher = Matcher(nlp.vocab)


#This project needs to:
# DONE 1 - Accept a *.txt or *.md input (or both) and find all the .txt or .md files in the project folder.
# DONE 2 - Read the file(s) and redact (Store in a list?) all words and related words to the provided flags,
#     'names', 'genders', and 'dates'.
# DONE 3 - Redact all words and related words from the provided 'concept' flag(s) - can use word matrices from Spacy.
#     1 method call for each provided concept flag.
# DONE 4 - Actually replace all redacted words with either a single Block U+2588 character, or multiple block characters.
# 5 - Output the redacted files to a folder provided by the user (or default to output/ if none provided)
# 6 - Generate a statistics function, which prints information about the run to stdout, stderr, or a file.
# 7 - Write tests for each method in seperate test_etc.py files.


def findDocs(userglob):
    # This function takes in a glob like *.txt and appends a list of all the file names with that extension it can find.
    myInput = userglob

    folderCheck = re.compile(r".*/\.\*")

    if myInput == '*.txt':
        myPattern = re.compile(r'\.txt$')
    elif myInput == "*.md":
        myPattern = re.compile(r'\.md$')
    else:
        raise NameError("Sorry, the --input glob was neither '*.txt' or '*.md' or 'folder/*.txt' or 'folder/*.txt'")

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

    for i in range(0, len(documents)):
        doc = nlp(documents[i])
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

        if len(myRedactList) == len(documents) and len(thisRedactList) > 0:
            for j in range(0,len(thisRedactList)):
                myRedactList[i].append(thisRedactList[j])
        #elif len(thisRedactList) > 0:
        elif len(myRedactList) < len(documents):
            myRedactList.append(thisRedactList)


def findGenders(documents, genderFlag, nameFlag):

    if not genderFlag:
        return
    pass

# Some of the Male and Female words were taken from
# https://medium.com/@rajat.jain1/natural-language-extraction-using-spacy-on-a-set-of-novels-88b159d68686
# and https://www.thefreedictionary.com/List-of-pronouns.htm

    # Pronouns, Titles,  Descriptions,  Relationships,  Royalty
    female_words = ["she", "her", "hers", "herself",
                    'mrs', 'ms', 'miss', 'madam', 'madame', 'lady', 'mistress',
                    "female", "woman", "girl",
                    "sister", "mother", "mom", "grandmother", "grandma",
                    "wife", "niece", "daughter", "aunt",
                    "queen", "princess"]

    male_words = ["he", "him", "his", "himself",
                "mr", "mister", "sir",
                "boy", "male", "man",
                "dad", "daddy", "father", "grandfather", "husband", "nephew", "son", "uncle", "grandpa", "pa",
                "bro", "brother",
                "king", "prince"]

    gendered_words = female_words + male_words
    # Assume all names are Gendered, or would giveaway the gender. Just call findNames here to be safe.
    # No need to call it if its already been called.
    if not nameFlag:
        findNames(documents, True, True)

    for i in range(0,len(documents)):
        thisRedactList = []
        mySmallList = []
        for word in gendered_words:
            locationlist = findTokenLocs(documents[i], word)
            for j in range(0,len(locationlist)):
                token_locs = [locationlist[j][0],locationlist[j][1]]
                #print(word, locationlist[j][0],locationlist[j][1], "Gender")
                mySmallList = [word, token_locs, "Gender"]
                thisRedactList.append(mySmallList)

        if len(myRedactList) == len(documents) and len(thisRedactList) > 0:
            for j in range(0,len(thisRedactList)):
                myRedactList[i].append(thisRedactList[j])
        elif len(myRedactList) < len(documents):
            myRedactList.append(thisRedactList)


def findDates(documents, dateFlag):
    if not dateFlag:
        return

    for i in range(0, len(documents)):
        doc = nlp(documents[i])
        thisRedactList = []
        for ent in doc.ents:
            #print(ent.text, ent.label_)
            foundNP = False
            if ent.label_ == "DATE":
                #Now is the time to find out what the token locations are for this span of tokens
                token_locs = [ent.start, ent.end]
                mySmallList = [ent.text, token_locs, "Dates"]
                thisRedactList.append(mySmallList)

        if len(myRedactList) == len(documents) and len(thisRedactList) > 0:
            for j in range(0,len(thisRedactList)):
                myRedactList[i].append(thisRedactList[j])
        elif len(myRedactList) < len(documents):
            myRedactList.append(thisRedactList)


def findConcepts(documents, concept, conceptFlag):
    if not conceptFlag:
        return
    #Ok, need to build a similarity matrix for each word. Anything over 0.45 gets included as similar and added
    #to the redact list.
    conceptdoc = nlp(concept)
    for i in range(0,len(documents)):
        thisRedactList = []
        doc = nlp(documents[i])
        for j in range(0,len(doc)):
            if doc[j].has_vector:
                if doc[j].similarity(conceptdoc[0]) > 0.45: #I really like >0.45, it works really nicely! Very impressive!
                    token_locs = [j, j+1]
                    mySmallList = [doc[j].text, token_locs, str("Concept: " + concept)]
                    thisRedactList.append(mySmallList)

                    #print("Word: " + str(doc[j]) + " - Similarity to " + concept + ": " + str(doc[j].similarity(conceptdoc[0])))

        if len(myRedactList) == len(documents) and len(thisRedactList) > 0:
            for j in range(0,len(thisRedactList)):
                myRedactList[i].append(thisRedactList[j])
        elif len(myRedactList) < len(documents):
            myRedactList.append(thisRedactList)

# This eprint method is taken directly from StackOverflow:
# https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def runStats(outputType, fileNames):

    if outputType == "stdout":
        for i in range(0,len(fileNames)):
            simpleFileName = os.path.basename(fileNames[i])
            mystats = pd.DataFrame(myRedactList[i])
            mystats = mystats.rename(columns={0: "Redacted_String", 1: "Token_Location", 2: "Redaction_Type"})
            print("\n\n")
            print("All redactions from: " + simpleFileName)
            print(mystats)
            print("Summary of: " + simpleFileName)
            if mystats.empty:
                print("No redactions made in this document.")
            else:
                print(mystats.groupby('Redaction_Type').count()[['Redacted_String']])

    if outputType == "stderr":
        for i in range(0, len(fileNames)):
            simpleFileName = os.path.basename(fileNames[i])
            mystats = pd.DataFrame(myRedactList[i])
            mystats = mystats.rename(columns={0: "Redacted_String", 1: "Token_Location", 2: "Redaction_Type"})
            eprint("\n\n")
            eprint("All redactions from: " + simpleFileName)
            eprint(mystats)
            eprint("Summary of: " + simpleFileName)
            if mystats.empty:
                eprint("No redactions made in this document.")
            else:
                eprint(mystats.groupby('Redaction_Type').count()[['Redacted_String']])

    else:
        #The outputType is a string, which will be used as a file, outputted to the same folder where output doc goes.
        #outputCheck = re.compile(r".*/$")
        #if not re.search(outputCheck,outputType):
            #raise NameError("The string passed to ")
        myStatsOutputPath = os.path.join(os.getcwd(),str(outputType + ".csv"))

            # Here is what you will do.
            # First, take your pandas df, and add a column called from_file
            # All the rows will get the simpleFileName of that filename[i]
            # Merge this modified df with a larger df, until all are added.
            #       pd.concat(objs, axis=0, join='outer', ignore_index=False, keys=None,
            #           levels=None, names=None, verify_integrity=False, copy=True)
        fulldf = pd.DataFrame()
        for i in range(0,len(fileNames)):
            simpleFileName = os.path.basename(fileNames[i])
            mystats = pd.DataFrame(myRedactList[i])
            mystats = mystats.rename(columns={0: "Redacted_String", 1: "Token_Location", 2: "Redaction_Type"})
            fileList = []
            mylength = int(mystats[['Redacted_String']].count()[0]) #This line is broken right now.
            for j in range(0,mylength):
                fileList.append(simpleFileName)
            mystats['from_file'] = fileList
            fulldf = pd.concat([mystats,fulldf])

        fulldf.to_csv(myStatsOutputPath)
        #fulldf.groupby('Redaction_Type').count()[['Redacted_String']]






def outputDoc(fileNames, redactedDocs, foldername = "output\\"):

    if foldername == "output\\" and not sys.platform == "win32": #Does a quick check to see if you are on Windows or not.
        foldername = "output/" #Switches the default filepath if so.

    #Needs to check for a valid foldername input here.

    myOutputDir = os.path.join(os.getcwd(),foldername)
    if not os.path.exists(myOutputDir):
        os.mkdir(myOutputDir)

    for i in range(0,len(fileNames)):
        baseFileName = os.path.basename(fileNames[i])
        newPathName = str(myOutputDir + baseFileName + ".redacted")

        myUnicodeDoc = str(redactedDocs[i]).encode("utf8")

        with open(newPathName, "wb") as file:
            file.write(myUnicodeDoc)
            file.close()


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

    if not myRedactList:
        for i in range (0,len(documents)):
            doc = nlp(documents[i])
            myRedactedDocs.append(doc)
        return

    redactMe = []
    for i in range(0, len(myRedactList)):
        fileRedactList = myRedactList[i]
        redactTemp = sorted(fileRedactList, key=lambda start_token: start_token[1][0])
        redactMe.append(redactTemp)

    myRedactList.clear()
    for i in range(0,len(redactMe)):
        myRedactList.append(redactMe[i])

    for i in range(0,len(documents)):
        doc = nlp(documents[i])
        redact_positions = []
        mydoc = ""

        #This loop is designed to resolve all adjacent banned token spans. If two or more tokens,
        # say token 323:324 and 324:329 are both found, then we end up with just 323:329.
        j = 0
        while(j < len(redactMe[i])):
            redact_start = redactMe[i][j][1][0] #Just a regular int at this point. Doc i, term j's start token.
            redact_end = redactMe[i][j][1][1] #Doc i, term j's stop token.
            chunk_resolved = False
            while not chunk_resolved:
                if j < len(redactMe[i])-1 and redact_end == redactMe[i][j+1][1][0]:
                    redact_end = redactMe[i][j+1][1][1]
                    j = j + 1
                elif j < len(redactMe[i])-1 and redact_end > redactMe[i][j+1][1][0]: #In the case of an overlap, previous end will be larger than next start.
                    j = j + 1
                else:
                    chunk_resolved = True
            redact_positions.append([redact_start,redact_end])
            j = j + 1

        if not redactMe[i]:
            write_start = 0
            write_end = len(doc)
            mydoc = mydoc + doc[write_start:write_end].text_with_ws

        else:
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

    #KEY PIECE OF ARGPARSE CODE! parser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    #From https://stackoverflow.com/questions/26727314/multiple-files-for-one-argument-in-argparse-python-2-7

    # YAY, take a look at this website for --input a --input b to be converted to a list:
    # https://docs.python.org/2/library/argparse.html#action
    # 'append' - This stores a list, and appends each argument value to the list. This is useful to allow an option to be specified multiple times. Example usage:
    # >>> parser = argparse.ArgumentParser()
    # >>> parser.add_argument('--foo', action='append')
    # >>> parser.parse_args('--foo 1 --foo 2'.split())
    # Namespace(foo=['1', '2'])


    findNamesFlag = True
    findGendersFlag = False
    findDatesFlag = False
    findConceptFlag = False
    conceptWord1 = "politics"
    conceptWord2 = "virus"
    fileext = "*.txt"   #need to update findDocs to accept folder inputs as well, like "cooldocs/*.txt"



    findDocs(fileext)

    unredactedDocs = []

    if(myFileNames):
        for x in range(0,len(myFileNames)):
            myFile1 = open(myFileNames[x], 'r', encoding="utf8")
            unredactedDocs.append(myFile1.read())
            myFile1.close()

    myRedactList = []

    findNames(unredactedDocs, findNamesFlag, False)
    findGenders(unredactedDocs, findGendersFlag, findNamesFlag)
    findDates(unredactedDocs, findDatesFlag)
    findConcepts(unredactedDocs, conceptWord1, findConceptFlag)
    findConcepts(unredactedDocs, conceptWord2, findConceptFlag)

    redact(unredactedDocs)

    print(myRedactList)

    runStats("coolstats",myFileNames)
    #outputDoc(myFileNames, myRedactedDocs)


    #for x in range(0,len(myRedactedDocs)):
    print(myRedactedDocs[1])



