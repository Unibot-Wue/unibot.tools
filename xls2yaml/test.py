import os
import argparse
import yaml
import csv
import sys
import itertools
import pandas as pd


#since we're working with str we'd like to transform to literal strings we need to change representer styles
#found on https://stackoverflow.com/questions/6432605/any-yaml-libraries-in-python-that-support-dumping-of-long-strings-as-block-liter

class literal_str(str): pass

def change_style(style, representer):
    def new_representer(dumper, data):
        scalar = representer(dumper, data)
        scalar.style = style
        return scalar
    return new_representer

from yaml.representer import SafeRepresenter

represent_literal_str = change_style('|', SafeRepresenter.represent_str)
yaml.add_representer(literal_str, represent_literal_str)



class Intent:
    """This class contains all information for an intent"""
    def __init__(self, id):
        self.id = id
        self.examples = []
        #for mapping later - not used so far
        self.utter = ""

def convert(file,filetype,ignored,answer,prefix1):

    intent_action_table = pd.read_excel(file, sheet_name=None)
    intent_df = intent_action_table['intents']
    intent_dict = {}
    nlu = []

    #iterrate over df
    for index,row in intent_df.iterrows():

        #read in intent
        intent_id = row['intent']

        #check if intent exists, if not create
        if intent_id not in intent_dict:
            intent_dict[intent_id] = Intent(intent_id)

        #append new example
        intent_dict[intent_id].examples.append("- " +row['example'])

    for intent in intent_dict:
        #append to nlu list
        nlu.append({"intent": intent, "examples": literal_str("\n".join(intent_dict[intent].examples))})

    #create yaml_files
    with open(r'nlu.yml', 'w', encoding='utf-8') as nlu_file:
        yaml.dump({"nlu":nlu}, nlu_file, allow_unicode=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='xls2yaml by viind GmbH. Copyright 2021. Initial version by MN')
    #parser.add_argument("-F", "--file", help="FAQ file", type=is_file, default='faq.csv')
    parser.add_argument("-F", "--file", help="FAQ file", default=\
        '/Users/nicoelbert/Documents/GitHub/unibot.tools/xls2yaml/example/intent_action_table.xlsx')
    parser.add_argument("-T", "--type", help="Filetype", choices=['csv'], default='csv')
    parser.add_argument("-I", "--ignored", help="Ignored lines", nargs='*', default=[0])
    parser.add_argument("-A", "--answer", help="Answer column", type=int, default=1)
    parser.add_argument("-P", "--prefix", help="Intent prefix", default='faq')
    args = parser.parse_args()
    print("file", args.file)
    print("type", args.type)
    print("ignored lines", args.ignored)
    print("answer column", args.answer)
    print("prefix", args.prefix)
    # DO STUFF
    convert(args.file, args.type, args.ignored, args.answer, args.prefix)
    sys.exit(0)
