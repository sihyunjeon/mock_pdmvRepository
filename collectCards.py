#!/usr/bin/env python3

import os
import sys
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--datasetpath", action = "store", default = None,
                    help = "path to dataset directory")
parser.add_argument("--campaign", action = "store", default = None,
                    help = "campign setting")
args = parser.parse_args()

datasetPath = args.datasetpath
campaign = args.campaign
campaignPath = os.path.join("campaignCoordinations", campaign)

templatePath = os.path.join("campaignCoordinations", campaign, "template", "MadGraph5_aMCatNLO")

if not datasetPath:
    sys.exit("[error] dataset path not given")

if not campaign:
    sys.exit("[error] campaign not given")

campaignJson = os.path.join(campaignPath, f"{campaign}.json")
with open(campaignJson) as jsonFile:
    campaignObject = json.load(jsonFile)
    jsonFile.close()

if not datasetPath.endswith("/"):
    datasetPath = f"{datasetPath}/"
datasetName = datasetPath.rsplit("/", 2)[1]
print (datasetName)
generatorJson = os.path.join(datasetPath, f"{datasetName}.json")
with open(generatorJson) as jsonFile:
    generatorObject = json.load(jsonFile)
    jsonFile.close()

os.system(f"mkdir {datasetName}")

def prepareRunCard():

    templateRuncardPath = os.path.join(templatePath, "run_card")

    if "amcatnlo" in datasetName:
        os.system(f"cp {templateRuncardPath}/NLO_run_card.dat {datasetName}/{datasetName}_run_card.dat")
        isNLO = True
    elif "madgraph" in datasetName:
        os.system(f"cp {templateRuncardPath}/LO_run_card.dat {datasetName}/{datasetName}_run_card.dat")
        isNLO = False
    else:
        sys.exit("[error] dataset name not properly set")

    runcardPath = os.path.join(datasetName, f"{datasetName}_run_card.dat")

    beamEnergy = campaignObject["beamEnergy"]
    os.system(f"sed -i 's|\$ebeam1|{beamEnergy}|g' {runcardPath}")
    os.system(f"sed -i 's|\$ebeam2|{beamEnergy}|g' {runcardPath}")

    ickkw = generatorObject["run_card"]["ickkw"]
    os.system(f"sed -i 's|\$ickkw|{ickkw}|g' {runcardPath}")

    maxjetflavor = generatorObject["run_card"]["maxjetflavor"]
    os.system(f"sed -i 's|\$maxjetflavor|{maxjetflavor}|g' {runcardPath}")

    if isNLO:
        parton_shower = generatorObject["run_card"]["parton_shower"]
        os.system(f"sed -i 's|\$parton_shower|{parton_shower}|g' {runcardPath}")
    else:
        xqcut = generatorObject["run_card"]["xqcut"]
        os.system(f"sed -i 's|\$xqcut|{xqcut}|g' {runcardPath}")

def prepareCustomizeCard():

    schemeCard = generatorObject["scheme"]
    schemecardPath = os.path.join(templatePath, "scheme", schemeCard)
    os.system(f"cat {schemecardPath} > {datasetName}/{datasetName}_customizecards.dat")

    customizecardPath = os.path.join(datasetPath, f"{datasetName}_customizecards.dat")

    os.system(f"cat {schemecardPath} > {datasetName}/{datasetName}_customizecards.dat")
    for l in generatorObject["user"]:
        os.system(f"echo {l} >> {datasetName}/{datasetName}_customizecards.dat")

def prepareWrapper():

    genproductions = jsonObject["genproductions"]
    os.system(f"wget {genproductions}")
    


def main():

    prepareRunCard()
    prepareCustomizeCard()
#    prepareWrapper()

if __name__ == "__main__":
    main()
