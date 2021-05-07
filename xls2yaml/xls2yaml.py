### KNOWN ISSUES ###
# When running Rasa with the generated files I get: ActionNotFoundException: Cannot access action 'utter_faq', as that name is not a registered action for this domain. Available actions are:...
# When exporting a csv file using Excel, the last line does not end with a delimiter. Therefore the last example question of the last faq is not converted. (Fix this around itertools - maybe also iterate until len(row) and check if the value is ""

### TODOS ###
# Add Python requirements to git repo
# Test end2end
# Write short documentation

import os
import argparse
import yaml
import csv
import sys
import itertools

def convert(file, filetype, ignored, answer, prefix):
    reader = csv.reader(file, dialect='excel', delimiter=';', quotechar='"')
    nlu = []
    responses = {}
    for idx,row in enumerate(reader):
        if idx not in ignored:
            print("Converting line ", idx)
            examples = []
            for entry in itertools.islice(row, answer+1, len(row)-1): # -1 because Dialect.lineterminator not implemented yet
                examples.append("- "+entry)
            print(row[answer])
            name = prefix+"/imported_"+str(idx)
            nlu.append({"intent":name,"examples":"\n".join(examples)})
            responses["utter_"+name] = [{"text":row[answer]}]
    with open(r'domain.yml', 'w', encoding='utf-8') as domain_file:
        yaml.dump({"intents":[prefix], "responses":responses}, domain_file, allow_unicode=True)
    with open(r'nlu.yml', 'w', encoding='utf-8') as nlu_file:
        yaml.dump({"nlu":nlu}, nlu_file, allow_unicode=True)
        
# add support for block scalars: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
# This is needed for "examples"
def str_presenter(dumper, data):
  if len(data.splitlines()) > 1:  # check for multiline string
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(str, str_presenter)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='xls2yaml by viind GmbH. Copyright 2021. Initial version by MN')
    #parser.add_argument("-F", "--file", help="FAQ file", type=is_file, default='faq.csv')
    parser.add_argument("-F", "--file", help="FAQ file", default='example\example.csv', type=argparse.FileType('r', encoding='UTF-8'))
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
