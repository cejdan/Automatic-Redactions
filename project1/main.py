# This is Project 1 for the Spring 2020 Text Analytics class
# Written by Nicholas Cejda
# Student ID: 113825637

from __future__ import print_function
import argparse
import re
import os
import spacy
from spacy.matcher import Matcher

import pandas as pd
import sys



#GLOBAL VARIABLES!
#We will use these lists, Spacy model, and spacy Matcher object across multiple methods.
myFileNames = []
myRedactedDocs = []
unredactedDocs = []
myRedactList = []
nlp = spacy.load("en_core_web_md")
matcher = Matcher(nlp.vocab)


#This project needs to:
# DONE 1 - Accept a *.txt or *.md input (or both) and find all the .txt or .md files in the project folder.
# DONE 2 - Read the file(s) and redact (Store in a list?) all words and related words to the provided flags,
#     'names', 'genders', and 'dates'.
# DONE 3 - Redact all words and related words from the provided 'concept' flag(s) - can use word matrices from Spacy.
#     1 method call for each provided concept flag.
# DONE 4 - Actually replace all redacted words with either a single Block U+2588 character, or multiple block characters.
# DONE 5 - Output the redacted files to a folder provided by the user (or default to output/ if none provided)
# DONE 6 - Generate a statistics function, which prints information about the run to stdout, stderr, or a file.
# DONE 7 - Write tests for each method in separate test_etc.py files.


def findDocs(userglob):


    # There are really only 12 valid inputs to this function:
    # *.txt, '*.txt', "*.txt",
    # *.md , '*.md' , "*.md"
    # folder/*.txt , 'folder/*.txt', "folder/*.txt"
    # folder/*.md, 'folder/*.md', "folder/*.md"
    # This function takes in a glob like *.txt or folder/*.txt and appends a list of all the file names with that extension it can find.


    myInput = userglob

    #This regex's job is to find valid folder name inputs. It looks for things like 'coolfolder\\*.txt' or 'myfolder/*.md'
    folderCheck = re.compile(r"[\'\"]?(\w*)([/\\])\*\.([tm][xd]t?)[\'\"]?")
    folderMatch = re.search(folderCheck, myInput)

    if folderMatch: #Asks, does the string have the form "folder/*.txt" or "folder\*.txt"  ?
        if sys.platform == "win32": #Ensures that the provided folder has backslashes if you are on windows.
            myFolder = folderCheck.sub(r"\\\\\1", myInput) #will be the string \\myfolder
            myFiles = folderCheck.sub(r"\.\3", myInput) #Will be the string txt or md
        else:
            myFolder = folderCheck.sub( r"/\1", myInput) #Otherwise, ensures it is a forward slash, so, /myfolder
            myFiles = folderCheck.sub(r"\.\3", myInput) #Will be the string txt or md

        #myFolder is now the string "/folder" or "\\folder". This is our new regex pattern.
        myFolderPattern = re.compile(myFolder)
        myFilePattern = re.compile(myFiles)
        folderExists = False

        # This for loop takes the current file's location, and goes up two directories, then it recursively checks all subdirectories looking for any
        # folders with the pattern "/folder" or "\\folder"
        for files in os.walk(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
            myFolderMatch = re.search(myFolderPattern, files[0])
            if myFolderMatch:
                folderExists = True
                for items in files[2]: #These items in files[2] are the actual file names inside that folder.
                    myFileMatch = re.search(myFilePattern, items) #We can then do a regex search on them, to see if they match our *.txt or *.md pattern.
                    if myFileMatch:
                        #print("Found a file match!")
                        if sys.platform == "win32":
                            currentFilePath = (files[0] + '\\' + items)
                        else:
                            currentFilePath = (files[0] +'/' + items)
                        myFileNames.append(currentFilePath) #When we find a hit, we append that file's whole path to myFileNames, for later use by other methods.

        if not folderExists:
            raise NameError("Sorry, the folder " + myFolder + " you specified does not exist. Please input a valid folder name.")


    # If the user input simply *.txt, we will find ALL *.txt files anywhere in the project directory!
    # If this behavior is not desired, use the "folder/*.txt" input mode instead!
    elif myInput == '*.txt' or myInput == r"'*.txt'" or myInput == r"*.txt":
        myPattern = re.compile(r'\.txt$')
        for files in os.walk(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
            for items in files[2]:
                myMatch = re.search(myPattern, items)
                if myMatch:
                    if sys.platform == "win32":
                        currentFilePath = (files[0] + '\\' + items)
                    else:
                        currentFilePath = (files[0] + '/' + items)
                    myFileNames.append(currentFilePath)

    #Same thing for the *md files. This will even find the README.md and redact it as well!
    elif myInput == "*.md" or myInput == "'*.md'" or myInput == r"*.md":
        myPattern = re.compile(r'\.md$')
        for files in os.walk(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
            for items in files[2]:
                myMatch = re.search(myPattern, items)
                if myMatch:
                    if sys.platform == "win32":
                        currentFilePath = (files[0] + '\\' + items)
                    else:
                        currentFilePath = (files[0] + '/' + items)
                    myFileNames.append(currentFilePath)

    else:
        raise NameError("Sorry, the --input glob was neither '*.txt' or '*.md' or 'folder/*.txt' or 'folder/*.md' - Don't forget the quotes ('' or "") ! ")


def findTokenLocs(document, myToken):
    #Needs to return a list of all the places token hits in document. Ex, [[20:21],[300:301]]
    #This method only handles single tokens for now. Building it for the findGender method.
    doc = nlp(document) #Create a new nlp model of our document. Pretty slow!! But it works.
    patternstr = [{'LOWER': str(myToken)}]
    matcher.add(str(myToken), None, patternstr) #We add a pattern to our pattern matcher, with the provided myToken.
    matches = matcher(doc) #We add all the matches to a matches variable.
    myMatchLocs = []
    for i in range(0,len(matches)):
        myMatchLocs.append([matches[i][1], matches[i][2]]) #myMatchLocs will contain all the match locations in the format we want.
    matcher.remove(str(myToken)) #We need this matcher.remove statement to clean up the matcher. Without this, incorrect matches pop up.
    return myMatchLocs #Returns a list of matches, like [[10,11],[33,34]]


def findNames(documents, fromGender):

    # Step 1, use Spacy's en-core-web-lg module to identify Named Entites.
    # Step 2, add all People and their token locs to the Redaction list.

    for i in range(0, len(documents)):
        doc = nlp(documents[i])
        thisRedactList = []

        #We search the named entities in our nlp model.
        for ent in doc.ents:
            foundNP = False
            if ent.label_ == "PERSON":

                #Now is the time to find out what the token locations are for this span of tokens
                token_locs = [ent.start, ent.end]

                # We want to know if the entity is part of a larger noun phrase. For example,
                # If our named entity is "Mike DeWine", we want to fully redact the phrase "Ohio Gov. Mike DeWine"
                # It is still super obvious who you are talking about if you don't redact "Ohio Gov." as well!
                # This loop logic handles these cases.
                for noun_chunks in doc.noun_chunks:
                    if noun_chunks.start <= ent.start and ent.end <= noun_chunks.end:
                        token_locs = [noun_chunks.start, noun_chunks.end]
                        if fromGender:
                            mySmallList = [noun_chunks.text, token_locs, "Gender"]
                        else:
                            mySmallList = [noun_chunks.text, token_locs, "Names"]
                        thisRedactList.append(mySmallList)
                        foundNP = True

                if not foundNP:
                    if fromGender: #Here we ask if we are coming from the findGenders method. If so, we append "Genders" instead of "Names"
                        mySmallList = [ent.text, token_locs, "Gender"]
                    else:
                        mySmallList = [ent.text, token_locs, "Names"]

                    thisRedactList.append(mySmallList)

        # This bit of code is reused in all the findX methods. Basically it ensures that len(myRedactList) will always match the
        # length of the number documents being used in the run, no matter if findNames, findGenders, findDates, or findConcepts
        # is run first.
        # This allows us to ALWAYS know that myRedactList[0] corresponds to myDocument[0]. Very useful when doing our stats function.
        if len(myRedactList) == len(documents) and len(thisRedactList) > 0:
            for j in range(0,len(thisRedactList)):
                myRedactList[i].append(thisRedactList[j])
        elif len(myRedactList) < len(documents):
            myRedactList.append(thisRedactList)


def findGenders(documents, nameFlag):

# Some of the Male and Female words were taken from
# https://medium.com/@rajat.jain1/natural-language-extraction-using-spacy-on-a-set-of-novels-88b159d68686
# and https://www.thefreedictionary.com/List-of-pronouns.htm

# This method is by far my most inefficient. It is SLOW! Mostly because it re-creates a new nlp doc object every single loop.
# If I were to upgrade any method in this program, I would start here, to improve the speed. But it works for now.
# Also, the words chosen here are only a tiny subset of the English gendered-words. I had to remove tons of uncommon words to speed
# up the method ('dutchess' and 'duke', etc.). This list is serviceable for our purposes here.

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
        findNames(documents, True)

    for i in range(0,len(documents)): #Loop for each document we want to redact.
        thisRedactList = []
        mySmallList = []
        #Loop once for every word in the gendered word list.
        for word in gendered_words:
            locationlist = findTokenLocs(documents[i], word) #Run our findTokenLocs for every word.
            for j in range(0,len(locationlist)):
                token_locs = [locationlist[j][0],locationlist[j][1]]
                #print(word, locationlist[j][0],locationlist[j][1], "Gender")
                mySmallList = [word, token_locs, "Gender"]
                thisRedactList.append(mySmallList)

        #This section is described in the findNames method.
        if len(myRedactList) == len(documents) and len(thisRedactList) > 0:
            for j in range(0,len(thisRedactList)):
                myRedactList[i].append(thisRedactList[j])
        elif len(myRedactList) < len(documents):
            myRedactList.append(thisRedactList)


def findDates(documents):
    # This method uses the named entity "DATE" from our Spacy model. It has some issues with things like ages,
    # like it thinks "30 years old" is a date, but it does a decent job overall.
    # The method strategy is the same as the findNames method.

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


def findConcepts(documents, concept):

    # Here we use Spacy's similarity functions to compare Word Vectors. If spacy gives a Similarity score of >= 0.5,
    # that's good enough to redact.
    # This method's limitation is that is does not deal with Phrases. Only single words. So concepts can slip through,
    # for example, if you redact the concept "Politics", from the phrase "The Democratic Primary Election", it will only redact
    # "Democratic" and "Elections", leaving the word "Primary."
    # I would improve this method to include phrases with more time.

    #First, check and see if the input has quotes or not. Need to remove those if it does.
    conceptCheck = re.compile(r"[\'\"](\w*)[\'\"]")
    conceptMatch = conceptCheck.search(concept)

    if conceptMatch:
        concept = conceptCheck.sub(r"\1",concept) #Removes the quotes, if they exist.

    conceptdoc = nlp(concept)
    if not conceptdoc[0].has_vector:
        raise NameError("Apologies, the concept you entered has no word vector in the Spacy model. This means it can't assign similarity scores! Please try again with a more common word, or maybe check your spelling?")
    for i in range(0,len(documents)):
        thisRedactList = []
        doc = nlp(documents[i])
        for j in range(0,len(doc)):
            #Only check words with similarity vectors.
            if doc[j].has_vector:
                if doc[j].similarity(conceptdoc[0]) >= 0.5: #I really like >0.5, it works really nicely! Very impressive!
                    token_locs = [j, j+1]
                    mySmallList = [doc[j].text, token_locs, str("Concept: " + concept)]
                    thisRedactList.append(mySmallList)

                    #print("Word: " + str(doc[j]) + " - Similarity to " + concept + ": " + str(doc[j].similarity(conceptdoc[0])))

        if len(myRedactList) == len(documents) and len(thisRedactList) > 0:
            for j in range(0,len(thisRedactList)):
                myRedactList[i].append(thisRedactList[j])
        elif len(myRedactList) < len(documents):
            myRedactList.append(thisRedactList)

# This eprint method is taken directly from StackOverflow user MarcH:
# https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
# The purpose is to provide a super easy way to print to stderr.
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def runStats(outputType, fileNames, foldername = "output\\"):
    # The stats function has 3 options, stdout, stderr, or create a csv file.
    # We take advantage of the structure of myRedactList to generate this summary, and to know which file each redaction came from.
    # I left the Redacted strings in on purpose, it greatly helps the user identify what is happening in the program.
    # I built the program with the end user in mind who knows what is being redacted, and will publish or distribute only the
    # redacted doc, not the stats summary.

    # Note, The .csv file does not include a quick summary, like the stdout and stderr do. This is intentional, as
    # I assume the user will do a more detailed analysis on the .csv than they will with the stdout or stderr outputs.

    if outputType == "stdout":
        for i in range(0,len(myRedactList)):
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

    elif outputType == "stderr":
        for i in range(0, len(myRedactList)):
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
        if not type(outputType) == str:
            raise NameError("Please provide either 'stdout', 'stderr', or a string input (filename) to the --stats flag. Your input was not a string.")

        if foldername == "output\\" and not sys.platform == "win32":  # Does a quick check to see if you are on Windows or not.
            foldername = "output/"  # Switches the default filepath if so.

            # Needs to check for a valid foldername input here.
        folderCheck = re.compile(r"[\'\"]?(\w*)([/\\])[\'\"]?")
        folderMatch = re.search(folderCheck, foldername)
        if folderMatch:
            if sys.platform == "win32":
                foldername = folderCheck.sub(r"\1\\", foldername)
            else:
                foldername = folderCheck.sub(r"\1/", foldername)

            #Need to check and remove quotes if output type had quotes.
            outputTypeCheck = re.compile(r"'(\w*)'")
            outputTypeCheck2 = re.compile(r'"(\w*)"')
            outputMatch1 = outputTypeCheck.search(outputType)
            outputMatch2 = outputTypeCheck2.search(outputType)

            if outputMatch1:
                outputType = outputTypeCheck.sub(r"\1", outputType)
            elif outputMatch2:
                outputType = outputTypeCheck2.sub(r"\1", outputType)

            myStatsOutputPath = os.path.join(os.getcwd(), foldername, str(outputType + ".csv"))

            # Here is what the following section does,
            # First, take your pandas df, and add a column called from_file
            # All the rows will get the simpleFileName of that filename[i]
            # Merge this modified df with a larger df, until all are added.

            fulldf = pd.DataFrame()
            for i in range(0,len(myRedactList)):
                simpleFileName = os.path.basename(fileNames[i])
                mystats = pd.DataFrame(myRedactList[i])
                mystats = mystats.rename(columns={0: "Redacted_String", 1: "Token_Location", 2: "Redaction_Type"})
                fileList = []
                for j in range(0,len(mystats.index)):
                    fileList.append(simpleFileName)
                mystats['from_file'] = fileList
                fulldf = pd.concat([fulldf,mystats])

            if not myRedactList:
                file = open(myStatsOutputPath, "w")
                file.write("No redactions were made this time!")
                file.close()
            else:
                #print(fulldf)
                fulldf.to_csv(myStatsOutputPath, index=False)
        else:
            raise NameError("Sorry, the folder you specified to --output is not a valid folder path. Did you forget to add a '/'? Please input something like: 'myoutput/' or 'output/'")


def outputDoc(fileNames, redactedDocs, foldername = "output\\"):

    #OutputDoc's job is to put the redactedDocs into a specified folder.
    #Needs to be run AFTER redact().

    if foldername == "output\\" and not sys.platform == "win32": #Does a quick check to see if you are on Windows or not.
        foldername = "output/" #Switches the default filepath if so.

    #Needs to check for a valid foldername input here.
    folderCheck = re.compile(r"[\'\"]?(\w*)([/\\])[\'\"]?")
    folderMatch = re.search(folderCheck, foldername)
    if folderMatch:
        if sys.platform == "win32":
            foldername = folderCheck.sub(r"\1\\", foldername)
        else:
            foldername = folderCheck.sub(r"\1/", foldername)

        myOutputDir = os.path.join(os.getcwd(),foldername)
        if not os.path.exists(myOutputDir):
            os.mkdir(myOutputDir)

        for i in range(0,len(redactedDocs)):
            baseFileName = os.path.basename(fileNames[i])
            newPathName = str(myOutputDir + baseFileName + ".redacted")

            myUnicodeDoc = str(redactedDocs[i]).encode("utf8")

            with open(newPathName, "wb") as file:
                file.write(myUnicodeDoc)
                file.close()
    else:
        raise NameError("Sorry, the folder you specified to --output is not a valid folder path. Did you forget to add a '/'? Please input something like: 'myoutput/' or 'output/'")

def redact(documents):

    #  OK, This method is a little bit complex. Bear with me.
    #  We want to use the TOKEN LOCs, found at:
    #  myRedactList[DOC i][RedactME j][TOKEN_LOC = 1][START(0) or STOP(1)]
    # And replace whatever tokens are there with a block.
    # Actually, we will use the original doc as a template, copying tokens and whitespace to a new file one by one until
    # we reach a BANNED token or token span. We won't write that or those tokens, we will instead write a single block.
    # I need to find all contiguous token spans, and deal with overlapping token spans.
    # I want to replace long token spans with a SINGLE block. This is way more protected than each character being replaced.
    # For example, "Ohio Gov. Mike DeWine" is replaced with a single block.
    # Luckily sorting the token spans is quick and easy with:
    #for x in range(0, len(myRedactList)):
    #    fileRedactList = myRedactList[x]
    #    redactme = sorted(fileRedactList, key=lambda start_token: start_token[1][0])
    # I can then proceed with redaction using the redactme sorted list as your banned tokens.
    # When redacting I can check if token.end[i] == token.start[i+1], these are uninterrupted redaction blocks.
    # Turn the whole thing (could be as large as a whole sentence) into one single block. "\u2588"

    if not myRedactList:
        for i in range (0,len(documents)):
            doc = nlp(documents[i])
            myRedactedDocs.append(doc)
        return

    redactMe = [] #A temp list used just for sorting the token spans.
    for i in range(0, len(myRedactList)):
        fileRedactList = myRedactList[i]
        redactTemp = sorted(fileRedactList, key=lambda start_token: start_token[1][0])
        redactMe.append(redactTemp)

    myRedactList.clear()
    for i in range(0,len(redactMe)):
        myRedactList.append(redactMe[i])  #Re-append back to myRedactList, for consistency.

    for i in range(0,len(documents)): #This is a big loop, once for each document.
        doc = nlp(documents[i]) #Create a new nlp doc object.
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

        #By the end of this logic, we have generated a redacted document. Append it to myRedactedDocs, and start again for the next document.
        myRedactedDocs.append(mydoc)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        help="Please input either *.txt, *.md, or folder/*.txt, or folder/*.md. These are the only supported options currently. \
                                   If you omit this flag, the default is *.txt, which will locate all the .txt files in the project directory and redact them.",
                        action='append')
    parser.add_argument('--names', help= "A boolean flag indicating if you want names redacted or not. Defaults to false.", action = "store_true")
    parser.add_argument('--dates',
                        help="A boolean flag indicating if you want dates redacted or not. Defaults to false.",
                        action="store_true")
    parser.add_argument('--genders',
                        help="A boolean flag indicating if you want genders redacted or not. Defaults to false.",
                        action="store_true")

    parser.add_argument('--concept',
                        help="A string, where you decide what concept to redact. The program will find similar words and redact \
                        them. So for example, if you provide the word 'politics', it will redact words like 'election', 'congress', 'president', etc.",
                        action='append')

    parser.add_argument('--output',
                        help = "An output folder for the redacted documents, the default is 'CURDIR/output/', but you can set it to a different name if desired.",)
    parser.add_argument('--stats',
                        help = "Must be either 'stdout', 'stderr', or a string of your choosing (ex. 'mycoolstats') to output a .csv. If --stats is not called, no stats are produced.")

    args = parser.parse_args()


    if args.input is not None: #If user uses --input as a flag, take their input.
        for i in range(0,len(args.input)):
            findDocs(args.input[i])
    else: #If they omit the --input flag, assume a *.txt input.
        findDocs('*.txt')

    if myFileNames: #Generates a list of file names.
        for x in range(0,len(myFileNames)):
            myFile1 = open(myFileNames[x], 'r', encoding="utf8")
            unredactedDocs.append(myFile1.read())
            myFile1.close()


    if args.names: #If the user supplies the --names flag, run findNames()
        findNames(unredactedDocs, False)
        findNamesFlag = True
    else: #Otherwise, don't run it.
        findNamesFlag = False

    if args.dates: #Same with --dates
        findDates(unredactedDocs)

    if args.genders: #and --genders
        findGenders(unredactedDocs, findNamesFlag)

    if args.concept is not None: #We run one findConcepts call for each --concept supplied to the command line.
        for i in range(0,len(args.concept)):
            findConcepts(unredactedDocs, args.concept[i])


    redact(unredactedDocs) #Redact all unredactedDocs. Will do nothing if the myRedactList is empty or the unredactedDocs is empty.

    if not args.output: #Uses the default output/ folder if the --output flag is omitted.
        outputDoc(myFileNames, myRedactedDocs)
    else:
        outputDoc(myFileNames, myRedactedDocs, foldername = args.output)


    if args.stats: #if --stats filename is included
        if not args.output: #But if --output not specified, put the stats in the output// folder by default.
            runStats(args.stats, myFileNames)
        else: #Otherwise, put it wherever the --output is putting other output files.
            runStats(args.stats, myFileNames, foldername = args.output)
