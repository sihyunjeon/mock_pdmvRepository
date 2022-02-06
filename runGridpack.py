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

    customizecardPath = os.path.join(datasetName, f"{datasetName}_customizecards.dat")

    schemeCard = generatorObject["scheme"]
    schemecardPath = os.path.join(templatePath, "scheme", schemeCard)

    os.system(f"cat {schemecardPath} > {customizecardPath}")

    os.system(f"echo \"\"  >> {customizecardPath}")
    os.system(f"echo \"# User settings\" >> {customizecardPath}")
    for l in generatorObject["user"]:
        os.system(f"echo {l} >> {customizecardPath}")

def prepareWrapper():

    os.system(f"tar -czvf cardsPdmV.tar.gz {datasetName}")

    wrapper = open("gridpack_PdmV.sh", "w")

    genproductions = campaignObject["genproductions"]

    wrapper.write("#!/usr/bin/env bash")
    wrapper.write(f"wget {genproductions}\n")
    wrapper.write(f"tar -xvf {genproductions}\n")
    wrapper.write("mv cardsPdmV.tar.gz genproductions/bin/MadGraph5_aMCatNLO/\n")
    wrapper.write("cd genproductions/bin/MadGraph5_aMCatNLO/\n")
    wrapper.write("tar -xvf cardsPdmV.tar.gz\n")
    wrapper.write(f"./gridpack_generation.sh {datasetName} {datasetName}\n")
    wrapper.close()

    os.system("chmod a+x gridpack_PdmV.sh")

def prepareJDSFile():

    jdsfile = open(f"gridpack_PdmV.jds", "w")
    jdsfile.write("executable = gridpack_PdmV.sh\n")
    jdsfile.write("transfer_input_files = cardsPdmV.tar.gz\n")
    jdsfile.write("when_to_transfer_output = on_exit\n")
    jdsfile.write("+JobFlavour = \"testmatch\"\n")
    jdsfile.write(f"+JobBatchName = \"{datasetName}\"\n")
    jdsfile.write(f"output = {datasetName}.stdout\n")
    jdsfile.write(f"error = {datasetName}.stderr\n")
    jdsfile.write(f"log = {datasetName}.stdlog\n")
    jdsfile.write("queue\n")
    jdsfile.close()

def main():

    prepareRunCard()
    prepareCustomizeCard()
    prepareWrapper()
    prepareJDSFile()

if __name__ == "__main__":
    main()
