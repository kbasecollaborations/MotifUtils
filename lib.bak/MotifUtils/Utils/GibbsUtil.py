import sys
import os
import json
from Bio import motifs
from Bio import SeqIO
from Bio.Alphabet import IUPAC
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

def build_gibbs_command(inputFilePath, motifLen):
    #outputFilePath = '/kb/module/work/tmp/gibbs_output.txt'
    if not os.path.exists('/kb/module/work/tmp/gibbs'):
        os.mkdir('/kb/module/work/tmp/gibbs')
    outputFilePath = '/kb/module/work/tmp/gibbs/gibbs_output_' + str(motifLen) +  '.txt'

    #outputFilePath = './temp/gibbs_output.txt'
    length = '8'
    command = 'Gibbs ' + inputFilePath + ' ' + str(motifLen) + ' -n > ' + outputFilePath
    return command

def run_gibbs_command(command):
    os.system(command)

def parse_gibbs_output(path):
    outputFileList = []
    #outputFileDir = '/kb/module/work/tmp'
    #for i in range(motif_min_length,motif_max_length+1,2):
        #outputFileList.append(outputFileDir + '/gibbs_output_' + str(i) + '.txt')
    for filename in os.listdir(path):
        outputFileList.append(path + '/' + filename)


    #outputFileDir = '/Users/arw/identify_promoter/test_local/workdir/tmp'
    #outputFilePath = outputFileDir + '/gibbs_output_' + str(motifLen) + '.txt'
    motifList = []
    for outputFilePath in outputFileList:

        gibbsFile = open(outputFilePath,'r')

        motifDict = {}
        pwmList = []
        processPWM = False
        processLoc = False
        gotSig = False
        motifIncluded = False

        #TODO: keeping p-value as -1 until I understand the output stats better
        motifDict['Locations'] = []
        for line in gibbsFile:
            if 'nMotifLen' in line:
                MotifLen = int(line.split()[2])
            if processLoc is True:
                if '****' in line:
                    processLoc = False
                    gotSig = False
                    motifDict['p-value'] = -1.0

                    a = []
                    c = []
                    g = []
                    t = []
                    for row in motifDict['pwm']:
                        a.append(row[0][1])
                        c.append(row[1][1])
                        g.append(row[2][1])
                        t.append(row[3][1])

                    motifStr = '>test\n'
                    motifStr += 'A ' + str(a).replace(',','') + '\n'
                    motifStr += 'C ' + str(c).replace(',','') + '\n'
                    motifStr += 'G ' + str(g).replace(',','') + '\n'
                    motifStr += 'T ' + str(t).replace(',','') + '\n'
                    handle = StringIO(motifStr)
                    BioMotif = motifs.read(handle, 'jaspar')
                    motifDict['Iupac_signature']=str(BioMotif.degenerate_consensus)

                    for m in motifList:
                        if motifDict['Iupac_signature'] == m['Iupac_signature']:
                            motifIncluded = True
                    if not motifIncluded:
                        if len(motifDict['pwm']) != len(motifDict['Iupac_signature']):
                            print(outputFilePath)
                            print(motifDict['Iupac_signature'])
                            print(len(motifDict['pwm']))
                        motifList.append(motifDict)
                    motifDict = {}
                    motifDict['Locations'] = []
                    motifIncluded = False
                    pwmList = []
                #add motif to list from here
                elif 'Num Motifs' not in line:
                    elems = line.split()
                    if not gotSig:
                        motif = elems[4]
                        #motifDict['Iupac_signature'] = motif
                        gotSig = True
                    locList = []
                    if len(line.split()) == 10:
                        locList.append(elems[9])
                        locList.append(elems[2])
                        locList.append(elems[6])
                        if elems[8] == 'F':
                            locList.append('+')
                        else:
                            locList.append('-')
                    elif len(line.split()) == 9:
                        locList.append(elems[8])
                        locList.append(elems[2])
                        locList.append(elems[5])
                        if elems[7] == 'F':
                            locList.append('+')
                        else:
                            locList.append('-')
                    motifDict['Locations'].append(locList)
            elif processPWM is True:
                if 'Background' in line:
                    processPWM = False
                    motifDict['pwm'] = pwmList
                elif '|' in line:
                    before = after
                    after = int(line.split()[0])
                    if before != -1 and after != -1:
                        if (after-before) != 1:
                            for i in range(0,(before-after)):
                                rowList = []
                                rowList.append(('A',.25))
                                rowList.append(('C',.25))
                                rowList.append(('G',.25))
                                rowList.append(('T',.25))
                                pwmList.append(rowList)
                    #baseCount += 1
                    elems = line.split()
                    rowList = []
                    rowList.append(('A',float(elems[2])))
                    rowList.append(('C',float(elems[4])))
                    rowList.append(('G',float(elems[5])))
                    rowList.append(('T',float(elems[3])))
                    pwmList.append(rowList)


            elif 'columns' in line:
                motifLength = int(line.split()[0])
                processLoc = True
            elif 'Motif probability model' in line:
                processPWM = True
                before = -1
                after = -1

    #jsonFilePath = outputFileDir + '/gibbs.json'
    #with open(jsonFilePath,'w') as jsonFile:
    #    json.dump(motifList,jsonFile)
    return motifList
