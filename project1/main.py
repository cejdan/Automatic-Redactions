
import argparse
import math
import re
import glob
import os
import nltk

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

    #What I want is a list of document names. I can accept an input *.txt, and I want to find all the strings "news1, news2, etc.
    #and make them into a list, which I can then cycle through when using nltk and spacy.

    myInput = "*.txt"
    myFileNames = []
    for name in glob.glob('../docs/'+myInput):
        print(os.path.abspath(name))
        myFileNames.append(os.path.abspath(name))
    print(myFileNames)


    myNews1 = open(myFileNames[1], 'r', encoding="UTF-8")
    myNews = myNews1.read()
    myNews1.close()


    block = "\u2588"
    match = re.compile("the ")
    match2 = re.compile("coronavirus")
    match3 = re.compile(block+" "+block)
    redactNews = match.sub(block+" ", myNews)
    redactNews = match2.sub(block, redactNews)
    redactNews = match3.sub(block, redactNews)
    print(myNews)
    print(redactNews)





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
