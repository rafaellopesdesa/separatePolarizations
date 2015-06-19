#!/bin/env python

import os, re, sys, shutil

os.system('rm -rf *tt *tl *ll')

for file in os.listdir('./'):
    isMatrixFile = re.match('matrix(\d+).f.original', file)
    if isMatrixFile is not None:
        os.rename(file, 'matrix%d.f' % int(isMatrixFile.group(1)))

for file in os.listdir('./'):

    isMatrixFile = re.match('matrix(\d+).f', file)

    if isMatrixFile is not None:

        inputFile = open(file)
        dummyFileTL = open(file + '.tl', 'w')
        dummyFileTT = open(file + '.tt', 'w')
        dummyFileLL = open(file + '.ll', 'w')

        helicityCombinationsTL = 0
        helicityCombinationsTT = 0
        helicityCombinationsLL = 0

        helicityWeightTL = 1
        helicityWeightTT = 1
        helicityWeightLL = 1
        
        
        for line in inputFile:

            isHelicityLine = re.search('DATA \\(NHEL\\(I,\s+(\d+)\\),I=1,6\\) \\/[\\+\\-\s]\d,[\\+\\-\s]\d,[\\+\\-\s](\d),[\\+\\-\s](\d),[\\+\\-\s]\d,[\\+\\-\s]\d\\/', line)
            isHelicityCombLine = re.search('DATA IDEN\\/(\d+)\\/', line)
            if isHelicityLine is not None:
                pol1 = int(isHelicityLine.group(2))
                pol2 = int(isHelicityLine.group(3))

                if (pol1 == 1 and pol2 == 0) or (pol1 == 0 and pol2 == 1):
                    helicityCombinationsTL = helicityCombinationsTL + 1
                    dummyFileTL.write(re.sub('NHEL\\(I,\s+\d+\\)', 'NHEL(I, %d)' % helicityCombinationsTL, line))
                elif pol1 == 1 and pol2 == 1:
                    helicityCombinationsTT = helicityCombinationsTT + 1
                    dummyFileTT.write(re.sub('NHEL\\(I,\s+\d+\\)', 'NHEL(I, %d)' % helicityCombinationsTT, line))
                elif pol1 == 0 and pol2 == 0:
                    helicityCombinationsLL = helicityCombinationsLL + 1
                    dummyFileLL.write(re.sub('NHEL\\(I,\s+\d+\\)', 'NHEL(I, %d)' % helicityCombinationsLL, line))
                else:
                    print 'Logic error. You are doing something wrong.'

            elif isHelicityCombLine is not None:
                totalCombinations = int(isHelicityCombLine.group(1))
                helicityWeightTL = helicityCombinationsTL * (helicityCombinationsTL+helicityCombinationsTT+helicityCombinationsLL)/totalCombinations
                helicityWeightTT = helicityCombinationsTL * (helicityCombinationsTL+helicityCombinationsTT+helicityCombinationsLL)/totalCombinations
                helicityWeightLL = helicityCombinationsLL * (helicityCombinationsTL+helicityCombinationsTT+helicityCombinationsLL)/totalCombinations

                dummyFileTL.write('      DATA IDEN /%d/\n' % helicityWeightTL)
                dummyFileTT.write('      DATA IDEN /%d/\n' % helicityWeightTT)
                dummyFileLL.write('      DATA IDEN /%d/\n' % helicityWeightLL)
               
            else:
                dummyFileTL.write(line)                
                dummyFileTT.write(line)                
                dummyFileLL.write(line)                

        inputFile.close()
        dummyFileTL.close()
        dummyFileTT.close()
        dummyFileLL.close()


if len(sys.argv) == 2:
    for file in os.listdir('./'):

        isMatrixFile = re.match('matrix(\d+).f.(\w+)', file)

        if isMatrixFile is not None:

            if isMatrixFile.group(2).strip() == sys.argv[1]:
                shutil.copy('matrix%d.f' % int(isMatrixFile.group(1)), 'matrix%d.f.original' % int(isMatrixFile.group(1)))
                shutil.copy(file, 'matrix%d.f' % int(isMatrixFile.group(1)))
            
