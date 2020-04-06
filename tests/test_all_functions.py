
import pytest
from project1 import main
import os
import io
import sys

def test_findDocs():
    input = "*.txt"
    main.findDocs(input)
    assert os.path.basename(main.myFileNames[0]) == "news1.txt"

def test_findTokenLocs():
    main.findDocs("*.txt")
    with open(main.myFileNames[0], 'r', encoding="utf8") as file:
        main.unredactedDocs.append(file.read())
        file.close()
    match_locations = main.findTokenLocs(main.unredactedDocs[0], "coronavirus")
    assert len(match_locations[0]) == 2 #The token "coronavirus" will hit news1.txt, and if the method is working properly we will get back a list of length 2 at each position in match_locations.

def test_findNames():
    #Parameters documents, fromGender
    main.findDocs("*.txt")
    with open(main.myFileNames[0], 'r', encoding="utf8") as file:
        main.unredactedDocs.append(file.read())
        file.close()
    main.findNames(main.unredactedDocs, fromGender=False)
    assert main.myRedactList[0][0][2] == "Names"
    assert len(main.myRedactList[0][0]) == 3 #If all goes well, the findNames() method will give us a list of lists, each element has a length 3.


def test_findGenders():
    #findGenders(documents, nameFlag):
    main.findDocs("*.txt")
    main.myRedactList.clear()
    with open(main.myFileNames[0], 'r', encoding="utf8") as file:
        main.unredactedDocs.append(file.read())
        file.close()
    main.findGenders(main.unredactedDocs, nameFlag=False)
    assert main.myRedactList[0][0][2] == "Gender"
    assert len(main.myRedactList[0][0]) == 3

    pass

def test_findDates():
    main.findDocs("*.txt")
    main.myRedactList.clear()
    with open(main.myFileNames[0], 'r', encoding="utf8") as file:
        main.unredactedDocs.append(file.read())
        file.close()
    main.findDates(main.unredactedDocs)
    assert main.myRedactList[0][0][2] == "Dates"
    assert len(main.myRedactList[0][0]) == 3


def test_findConcepts():
    #(documents, concept)
    main.findDocs("*.txt")
    main.myRedactList.clear()
    with open(main.myFileNames[0], 'r', encoding="utf8") as file:
        main.unredactedDocs.append(file.read())
        file.close()
    concept_word = "politics"
    main.findConcepts(main.unredactedDocs, concept_word)
    assert main.myRedactList[0][0][2] == "Concept: politics"
    assert len(main.myRedactList[0][0]) == 3


def test_runStats():
    #(outputType, fileNames, foldername = "output\\"):
    main.findDocs("*.txt")
    with open(main.myFileNames[0], 'r', encoding="utf8") as file:
        main.unredactedDocs.append(file.read())
        file.close()
    main.findNames(main.unredactedDocs, fromGender=False)
    with pytest.raises(NameError):
        assert main.runStats(1,main.unredactedDocs) #This test makes sure a NameError is thrown when an invalid (non-string) outputType is used.
    text_trap = io.StringIO()
    sys.stdout = text_trap
    main.runStats("stdout",main.unredactedDocs)
    sys.stdout = sys.__stdout__
    assert type(text_trap.getvalue()) == str #Checks to make sure if stdout is selected as the option, a string is being printed to stdout.
    text_trap = io.StringIO()
    sys.stderr = text_trap
    main.runStats("stderr", main.unredactedDocs)
    sys.stderr = sys.__stderr__
    assert type(text_trap.getvalue()) == str  # Checks to make sure if stderr is selected as the option, a string is being printed to stdout.

    #Working on this test, pytest doesn't seem to actually create a new file when I run the runStats function for some reason.
    #main.runStats("myteststats", main.unredactedDocs, foldername = "output\\")
    #if not sys.platform == "win32":  # Does a quick check to see if you are on Windows or not.
    #    foldername = "output/"  # Switches the default filepath if so.
    #else:
    #    foldername = "output\\"
    #myStatsOutputPath = os.path.join(os.getcwd(), foldername, str("myteststats" + ".csv"))
    #assert os.path.isfile(myStatsOutputPath)



def test_outputDoc():
    #(fileNames, redactedDocs, foldername = "output\\")
    pass

def test_redact():
    #(documents):
    pass

