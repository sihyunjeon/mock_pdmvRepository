#!/usr/bin/env python3

import os
import sys
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--makedir", action = "store_true", default = False,
                    help = "create directories in generatorCards directory")
parser.add_argument("--input", action = "store", default = None,
                    help = "input CSV file to check")
args = parser.parse_args()

if not args.input:
    sys.exit("input CSV file not given")

if not args.makedir:
    print("dryrun, only checking if the directories exist or not\nto create directories, add --makedir")

os.system(f"sed -i 's/ //g' {args.input}")
os.system(f"sed -i 's/\t//g' {args.input}")

print("")
print(f"scanning {args.input}")
print("")

with open(args.input, newline = "") as csvFile:
    csvDict = csv.DictReader(csvFile)
    for l in csvDict:
        datasetName = f"{l['process']}_{l['setting']}_{l['generator']}"
        dirPath = os.path.join("generatorCards", l["directory"], l["process"], datasetName)
        if not os.path.exists(dirPath):
            print(f"{dirPath} does not exist")
            if args.makedir:
                print(f"{dirPath} created")
                os.system(f"mkdir -p {dirPath}")
#{'process': 'DYJets', ' setting': ' inclusive', ' generator': ' amcatnloFXFX-pythia', ' nevents': ' 1000000', ' directory': ' MadGraph5_aMCatNLO'}
#
