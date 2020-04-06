# cs5293sp20-project1
README is under construction! Will have it up and ready Monday, April 6th.

This project redacts Names, Dates, Genders, or user-defined "Concept" related words from text documents.

To run this project, ensure you have pipenv installed, then clone the Github repo, and run in a command shell:

pipenv install

*************Then, to run, you must install the correct Spacy model. Type this into your command line: ****************

pipenv run python -m spacy download en_core_web_md 

*******************************************************************************************************

This model is 96.4 Mb, so please ensure your computer or VM has enough space!
I chose the en_core_web_md because it has word vectors, but isn't quite as large as the en_core_web_lg model. It is a compromise between disc space, speed, and accuracy. The larger models have better similarity word vectors, so they have better similarity scores, but it takes more disc space, and runs more slowly. The medium sized model will work just fine for this project.
