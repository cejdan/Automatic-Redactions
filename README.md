# Project Outline and Overview

This project redacts Names, Dates, Genders, or user-defined "Concept" related words from text documents. So if you provide the concept word "Politics", it will redact words like "Election", "government", "president", etc.
These concepts can be any single words that are common in the English language, like "Politics", or "virus" or what have you.
Currently this project does not support multi-word concepts like "the United States". Try "U.S." instead.


Running this project has two steps:
1. Ensure you have pipenv installed, clone the Github repo, then run in a command shell:


    pipenv install



2. Then, you must install the correct Spacy model. Type this into your command line:


    pipenv run python -m spacy download en_core_web_md 


This Spacy model is 96.4 Mb, so please ensure your computer or VM has enough space!
I chose the en_core_web_md because it has word vectors, but isn't quite as large as the en_core_web_lg model. It is a compromise between disc space, speed, and accuracy. The larger models have better similarity word vectors, so they have better similarity scores, but it takes more disc space, and runs more slowly. The medium sized model works just fine for this project.

# Running the program

To run the program, navigate to your project directory in your command shell, and type:

    pipenv run python project1/main.py --input '\*.txt' --names --genders --dates --concept 'politics' --concept 'virus' --output myfolder/ --stats mystats

## Descriptions and parameters for each flag

Parameter Flag | Accepted values | Description
-------------- | --------------- | ------------
--input | '\*.txt', '\*.md', 'folder/\*.txt' , and 'folder/\*.md' (on Windows, 'folder\\\*.txt' and 'folder\\\*.md' are also accepted.) | Optional - Default = '\*.txt' Providing a folder will search only that folder for the .txt or .md files. Omitting the folder will search the entire project directory for .txt or .md files.
--names | Boolean Flag (no additional values needed, --names is sufficient) | Optional, activates the findNames function. Defaults to False if omitted.
--genders | Boolean Flag | Optional, activates the findGenders function. Defaults to False if omitted.
--dates | Boolean Flag | Optional, activates the findDates function. Defaults to False if omitted.
--concepts | any English word | Optional, activates the findConcepts function. Defaults to none if omitted. Can specify multiple --concept words if desired.
--output | 'folder/' (or 'folder\\' if on Windows) | Optional, allows the user to choose a folder to output the redacted documents. Defaults to 'output/' if omitted.
--stats | stdout, stderr, or 'filename' | Optional, allows the user to choose how the run statistics are displayed, defaults to stdout if omitted, and if 'filename' is specified, it outputs a .csv to the same location as --output.


# Discussion of the Concepts method

The way I approached the concept redactions was to use Spacy's .similarity() methods. The larger models, like en_core_web_md and en_core_web_lg both come with pre-defined Word Vectors for all the words in the model.
We can use this, and generate a similarity score between 0 and 1 for each word in our document compared to our provided concept word. I used score >= 0.5 as considered similar enough to count as a redaction.
This score is relatively stringent, and performs well on a range of inputs. Lowering the threshold accepts more "noise", while increasing the threshold reduces more "signal". 0.5 was a compromise, and performs well under tests.

The findConcepts() method currently does not does not support redacting Phrases from your provided concepts.
So, if you supply the word "virus", and your document contains the phrase, "The novel Coronavirus", it will leave "The novel" and only redact "Coronavirus"
This is a feature I would like to implement in the future.


# Description of the Statistics Output and Method

The runStats() function has three main outputs, stdout (prints to the screen), stderr (prints to the built-in Python error messaging system), and to .csv file.
The stdout and stderr provide the same output, which is a list of each Redacted String, the Token Locations of the redaction, the type of redaction (like "Names" or "Genders"), broken up by document. 
It also provides a helpful summary of how many redactions were made for each type as well.
This is the preferred output for a quick summary of the run.

The file.csv output is designed for deeper analytics. It simply provides a .csv file, with the columns as Redacted String, Token Locations, Type of Redaction, and the FileName.
This output is designed for a user who wants to do their own analysis, and thus intentionally does not provide the summary like stdout and stderr.

# Descriptions of the Functions in the code 

More detailed comments are provided in the code itself, but I will describe each function briefly here.

Function Name | Description
------------- | -----------
findDocs(userglob) | This method is designed to accept a string like '\*.txt' or 'folder/\*.txt' and find the correct files, and append them to a list, myFileNames.
findTokenLocs(document, myToken) | accepts a list of documents and a token, and searches the document[i] for the token myToken. Returns a list of Token spans (ex. [[20,21],[300,301]])
findNames(documents, fromGender) | accepts a list of documents and a boolean fromGender flag, and appends matches for Names, or Noun Phrases containing Names for each document to myRedactList. if fromGender is true, it appends the word "Gender" instead of "Names" to myRedactList.
findGenders(documents, nameFlag) | accepts a list of documents and a boolean nameFlag. It adds Gendered words to the myRedactList, and if nameFlag was False, it ALSO redacts Names. The assumption is that people's names are always gendered, so it redacts them just to be safe. 
findDates(documents) | accepts a list of documents, and adds all the Dates to myRedactList, using Spacy's Named Entity recognition.
findConcepts(documents, concept) | Described above in the "Discussion of the Concepts method" section
runStats(outputType, fileNames, foldername = "output\\") | Described above in the "Discussion of the Statistics Output and Method" section
outputDoc(fileNames, redactedDocs, foldername = "output\\") | Uses the fileNames and redactedDocs to output to a folder, the default is output/ ("output\\" on Windows).
redact(documents) | accepts a list of documents, and uses the generated myRedactList to perform all the redactions. Writes the new redacted files to the myRedactedDocs list.



# Descriptions of Tests

I have included a test (or tests) for each method described above. I will describe the tests briefly here.
The tests touch essentally all lines of my main.py code.

Test Name | Description
--------- | -----------
test_findDocs() | checks if we found at least 1 document, using the default input of '\*.txt
test_findTokenLocs() | checks if using the token "coronavirus" contains a match of length 2. This is the expected output size, and we know our news1.txt contains the token "coronavirus"
test_findNames() | checks if the output of findNames is a list of list of lists, with the smallest list being length 3. This output format is required for our runStats and redact functions. It also checks to make sure it has the correct label "Names".
test_findGenders() | Similar to findNames, checks if the output is the correct size and has the correct label.
test_findDates() | Similar to findNames, checks if the output is the correct size and has the correct label.
test_findConcepts() | Similar to findNames, checks if the output is the correct size and has the correct label.
test_redact_and_outputDoc() | Tests both the redact and output methods. The redact check ensures we make it through the redact method fully, by populating myRedactedDocs. The output check ensures the correct folder and file is created properly.
test_runStats() | Tests to ensure if a filename is provided, that a .csv is created at the correct location. If stdout or stderr is provided, it checks to ensure that it properly is outputting strings to stdout or stderr.



# Limitations of the Redaction Program

Let's face it, this redaction program is not perfect. The documents MUST be checked to ensure they adequately meet your redaction needs.
Often it will miss names, or redact incorrect items, or will be too strict or too loose with your Concepts, and It also currently does not support redacting Phrases from your provided concepts.
The main reason for this limitation is that Spacy's out-of-the-box models are not perfect. Ideally, we would train the model futher on examples more specific to your area of need (i.e. medical records, politics, crime, etc.)
Additionally, if speed is less of a concern, we could use the en_core_web_lg model, which is slower but would be more accurate.





