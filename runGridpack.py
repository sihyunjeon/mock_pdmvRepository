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

datasetJson = os.path.join(datasetPath, f"{datasetName}.json")
with open(datasetJson) as jsonFile:
    datasetObject = json.load(jsonFile)
    jsonFile.close()

os.system(f"mkdir {datasetName}")

def prepareDefaultCard():

    templateProccardPath = os.path.join(datasetPath, f"{datasetName}_proc_card.dat")
    nb_core = datasetObject["nb_core"]

    os.system(f"echo \"set nb_core {nb_core}\" > {datasetName}/{datasetName}_proc_card.dat")
    os.system(f"cat {templateProccardPath} >> {datasetName}/{datasetName}_proc_card.dat")

    templateMadspincardPath = os.path.join(datasetPath, f"{datasetName}_madspin_card.dat")
    if os.path.exists(templateMadspincardPath):
        os.system(f"cat {templateMadspincardPath} > {datasetName}/{datasetName}_madspin_card.dat")

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

    ickkw = datasetObject["run_card"]["ickkw"]
    os.system(f"sed -i 's|\$ickkw|{ickkw}|g' {runcardPath}")

    maxjetflavor = datasetObject["run_card"]["maxjetflavor"]
    os.system(f"sed -i 's|\$maxjetflavor|{maxjetflavor}|g' {runcardPath}")

    if isNLO:
        parton_shower = datasetObject["run_card"]["parton_shower"]
        os.system(f"sed -i 's|\$parton_shower|{parton_shower}|g' {runcardPath}")
    else:
        xqcut = datasetObject["run_card"]["xqcut"]
        os.system(f"sed -i 's|\$xqcut|{xqcut}|g' {runcardPath}")

def prepareCustomizeCard():

    customizecardPath = os.path.join(datasetName, f"{datasetName}_customizecards.dat")

    schemeCard = datasetObject["scheme"]
    schemecardPath = os.path.join(templatePath, "scheme", schemeCard)

    os.system(f"cat {schemecardPath} > {customizecardPath}")

    os.system(f"echo \"\"  >> {customizecardPath}")
    os.system(f"echo \"# User settings\" >> {customizecardPath}")
    for l in datasetObject["user"]:
        os.system(f"echo {l} >> {customizecardPath}")

def prepareWrapper():

    os.system(f"tar -czvf cardsPdmV.tar.xz {datasetName}")

    wrapper = open("gridpack_PdmV.sh", "w")

    genproductions = campaignObject["genproductions"]
    genproductionsLink = f"https://github.com/cms-sw/genproductions/archive/refs/tags/{genproductions}.tar.gz"

    wrapper.write("#!/usr/bin/env bash\n")
    wrapper.write("export HOME=`pwd`\n")
    wrapper.write(f"wget {genproductionsLink} \n")
    wrapper.write(f"tar -xf {genproductions}.tar.gz\n")
    wrapper.write(f"rm {genproductions}.tar.gz\n")
    wrapper.write(f"mv genproductions-{genproductions} genproductions\n")
    wrapper.write(f"mv cardsPdmV.tar.xz genproductions/bin/MadGraph5_aMCatNLO/\n")
    wrapper.write("rm cardsPdmV.tar.xz\n")
    wrapper.write("cd genproductions\n")
    wrapper.write("git init\n")
    wrapper.write(f"cd bin/MadGraph5_aMCatNLO/\n")
    wrapper.write("tar -xf cardsPdmV.tar.xz\n")
    wrapper.write("mkdir cardsPdmV\n")
    wrapper.write(f"mv {datasetName} cardsPdmV/\n")
    wrapper.write(f"./gridpack_generation.sh {datasetName} cardsPdmV/{datasetName}\n")
    wrapper.write(f"mv {datasetName}*.xz ../../../\n")
    wrapper.close()

    os.system("chmod a+x gridpack_PdmV.sh")

def prepareJDSFile():

    nb_core = datasetObject["nb_core"]

    jdsfile = open(f"gridpack_PdmV.jds", "w")
    jdsfile.write("executable = gridpack_PdmV.sh\n")
    jdsfile.write("transfer_input_files = cardsPdmV.tar.xz\n")
    jdsfile.write("when_to_transfer_output = on_exit\n")
    jdsfile.write("+JobFlavour = \"testmatch\"\n")
    jdsfile.write(f"+JobBatchName = \"{datasetName}\"\n")
    jdsfile.write(f"output = {datasetName}.stdout\n")
    jdsfile.write(f"error = {datasetName}.stderr\n")
    jdsfile.write(f"log = {datasetName}.stdlog\n")
    jdsfile.write(f"RequestCpus = {nb_core}\n")
    jdsfile.write(f"RequestMemory = 8000\n")
    jdsfile.write("queue\n")
    jdsfile.close()

def main():

    prepareDefaultCard()
    prepareRunCard()
    prepareCustomizeCard()
    prepareWrapper()
    prepareJDSFile()

if __name__ == "__main__":
    main()
