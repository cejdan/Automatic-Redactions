# cs5293sp20-project1
README is under construction! Will have it up and ready Monday, April 6th.

This project redacts user-inputted words or phrases from text documents

To run, you must install the correct Spacy model. Type this into your command line:
pipenv run python -m spacy download en_core_web_md 
It is 96.4 Mb, so please ensure your computer or VM has enough space!
I chose the en_core_web_md because it has word vectors, but isn't quite as large as the en_core_web_lg model. It is a compromise between disc space, speed, and accuracy. The larger models have better similarity word vectors, so they have better similarity scores, but it takes more disc space, and runs more slowly. The medium sized model will work just fine for this project.
