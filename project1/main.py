#Work begins here!

import argparse
#import project1


def main():
	pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
	
	#The required arguments will be:
	#--input (glob*.txt or glob.md) --names --dates --concept (str) --output (folder/) --stats (stderr, stdout, or filename)
    
    parser.add_argument("--input", type=glob, required=True, 
                         help="A glob (*.fileextention) that you want to search for. Only supports .txt and .md files for now.")
    parser.add_argument("--names", required=False,
						 help="An optional flag if you want to remove all names of people from the document. Cannot whitelist names currently.")
	parser.add_argument("--dates", required=False,
						 help="An optional flag if you want to remove all the dates from the document."
	parser.add_argument("--concept", type=str, required=False,
						 help="An optional flag which removes all words or phrases associated with a particular concept, like 'jail'. Uses a clustering algorithm and redacts related words and phrases to the provided string."
	parser.add_argument("--output", type=folder, required=False,
						 help="An optional flag if you want to specify which folder will be used to deposit output files. Default is the current directory."
	parser.add_argument("--stats", type=stderr,stdout,or filename, required=False,
						 help="An optional flag if you want to specify where the run statistics will go. They default to stdout."

    args = parser.parse_args()
    if args:
        main(args.input) #Not exactly sure how to call main here, with all args. Need to watch a video or something on the argparse module.
		