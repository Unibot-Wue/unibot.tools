### KNOWN ISSUES ###
# When running Rasa with the generated files I get: ActionNotFoundException: Cannot access action 'utter_faq', as that name is not a registered action for this domain. Available actions are:...
# When exporting a csv file using Excel, the last line does not end with a delimiter. Therefore the last example question of the last faq is not converted. (Fix this around itertools - maybe also iterate until len(row) and check if the value is ""

### TODOS ###
# Add Python requirements to git repo
# Test end2end
# Write short documentation
#handle multiple lines

import argparse
import yaml
import sys
import pandas as pd


#since we're working with str we'd like to transform to literal strings we need to change representer styles
#found on https://stackoverflow.com/questions/6432605/any-yaml-libraries-in-python-that-support-dumping-of-long-strings-as-block-liter

class literal_str(str): pass
class folded_str(str): pass

def change_style(style, representer):
    def new_representer(dumper, data):
        scalar = representer(dumper, data)
        scalar.style = style
        return scalar
    return new_representer

from yaml.representer import SafeRepresenter

represent_literal_str = change_style('|', SafeRepresenter.represent_str)
represent_folded_str = change_style('>', SafeRepresenter.represent_str)
yaml.add_representer(literal_str, represent_literal_str)
yaml.add_representer(folded_str, represent_folded_str)


class Intent:
    """This class contains all information for an intent"""
    def __init__(self, id):
        self.id = id
        self.examples = []
        #for mapping later - not used so far
        self.action = "utter_" +  self.id
        self.anwser = "Action not Found"

        self.category = self.id.split("/")[0]

def convert(file,filetype,ignored,answer,prefix1):

    intent_action_table = pd.read_excel(file, sheet_name=None)
    intent_df = intent_action_table['intents']
    action_df = intent_action_table['actions']
    intent_dict = {}
    categories = []
    nlu = []
    responses = {}

    #iterrate over df
    for index,row in intent_df.iterrows():

        #read in intent
        intent_id = row['intent']

        #check if intent exists, if not create
        if intent_id not in intent_dict:
            intent_dict[intent_id] = Intent(intent_id)
            #also check if category is already listed
            if intent_dict[intent_id].category not in categories:
                categories.append(intent_dict[intent_id].category)

        #append new example
        intent_dict[intent_id].examples.append("- " +row['example'])


    for intent in intent_dict:
        #read in actions for intents
        for index, row in action_df.iterrows():
            if row['action'] == intent_dict[intent].action:
                intent_dict[intent].anwser = row['text']

        #append to nlu list
        nlu.append({"intent": intent, "examples": literal_str("\n".join(intent_dict[intent].examples))})
        responses[intent_dict[intent].action] = [{"text": folded_str(intent_dict[intent].anwser)}]


    #prepare categorys for yaml
    str_categories_list = []
    for c in categories:
        str_categories_list.append("-" + c)

    str_categories = literal_str("\n".join(str_categories_list))

    #create yaml_files
    with open(r'nlu.yml', 'w', encoding='utf-8') as nlu_file:
        yaml.dump({"nlu":nlu}, nlu_file, allow_unicode=True)

    with open(r'domain.yml', 'w', encoding='utf-8') as domain_file:
        yaml.dump({"intents":str_categories, "responses":responses}, domain_file, allow_unicode=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='xls2yaml by viind GmbH. Copyright 2021. Initial version by MN')
    #parser.add_argument("-F", "--file", help="FAQ file", type=is_file, default='faq.csv')
    parser.add_argument("-F", "--file", help="FAQ file", default=\
        'example\intent_action_table.xlsx')
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
