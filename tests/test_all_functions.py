
import pytest
from project1 import main
import os
import io
import sys
import shutil #For cleaning up the output directory after all tests are complete.

#This file checks all of my methods in project1/main.py

def test_findDocs():
    input = "*.txt"
    main.findDocs(input)
    assert len(main.myFileNames) > 0 #Check that the function found at least 1 file.


def test_findTokenLocs():
    main.findDocs("*.txt")
    with open(main.myFileNames[0], 'r', encoding="utf8") as file:
        main.unredactedDocs.append(file.read())
        file.close()
    match_locations = main.findTokenLocs(main.unredactedDocs[0], "coronavirus")
    assert len(match_locations[0]) == 2 #The token "coronavirus" will hit news1.txt, and if the method is working properly we will get back a list of length 2 at each position in match_locations.

def test_findNames():

    main.findNames(main.unredactedDocs, fromGender=False)
    assert main.myRedactList[0][0][2] == "Names"
    assert len(main.myRedactList[0][0]) == 3 #If all goes well, the findNames() method will give us a list of lists, each element has a length 3.


def test_findGenders():

    main.myRedactList.clear()

    main.findGenders(main.unredactedDocs, nameFlag=False)
    assert main.myRedactList[0][0][2] == "Gender"
    assert len(main.myRedactList[0][0]) == 3 #If all goes well, the findGenders() method will give us a list of lists, each element has a length 3.


def test_findDates():

    main.myRedactList.clear()

    main.findDates(main.unredactedDocs)
    assert main.myRedactList[0][0][2] == "Dates"
    assert len(main.myRedactList[0][0]) == 3 #If all goes well, the findDates() method will give us a list of lists, each element has a length 3.


def test_findConcepts():

    main.myRedactList.clear()

    concept_word = "politics"
    main.findConcepts(main.unredactedDocs, concept_word)
    assert main.myRedactList[0][0][2] == "Concept: politics"
    assert len(main.myRedactList[0][0]) == 3 #If all goes well, the findConcepts() method will give us a list of lists, each element has a length 3.


def test_redact_and_outputDoc():

    main.myRedactList.clear()

    main.findNames(main.unredactedDocs, fromGender=False)
    main.redact(main.unredactedDocs)
    assert len(main.myRedactedDocs) == 1 #If it makes it though main.redact, we get one redacted doc back.
    main.outputDoc(main.myFileNames, main.myRedactedDocs)
    if not sys.platform == "win32":  # Does a quick check to see if you are on Windows or not.
        foldername = "output/"  # Switches the default filepath if not.
    else:
        foldername = "output\\"
    myOutputDir = os.path.join(os.getcwd(), foldername)
    assert os.path.exists(myOutputDir) #If outputDoc did its job, this directory will exist.
    baseFileName = os.path.basename(main.myFileNames[0])
    newPathName = str(myOutputDir + baseFileName + ".redacted")
    assert os.path.exists(newPathName) #The .redacted file should exist as well.


def test_runStats():

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

    main.runStats("myteststats", main.myFileNames, foldername = "output\\")
    if not sys.platform == "win32":  # Does a quick check to see if you are on Windows or not.
        foldername = "output/"  # Switches the default filepath if so.
    else:
        foldername = "output\\"
    myoutputfolder = os.path.join(os.getcwd(), foldername)
    myStatsOutputPath = os.path.join(os.getcwd(), foldername, str("myteststats" + ".csv"))
    assert os.path.isfile(myStatsOutputPath)
    shutil.rmtree(myoutputfolder) #Clears up any created directory for the tests.
