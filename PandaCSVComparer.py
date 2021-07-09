import itertools
import pandas as pd
import re
from fuzzywuzzy import fuzz, process


# read csv files and determine headers for columns
cms = pd.read_csv("GraphCMSDiagnoses.csv")
dc = pd.read_csv("DiagnosisCreatorDiagnoses.csv")

# detect matched entities in cmsDiagnosis column
# cms.head() -> checks the first columns
# cms.info() -> checks to see the data types in column and if there are null values

"""
print(cms.columns) -> Index(['nameStd', 'icd10'], dtype='object')
print(dc.columns) -> Index(['diagnosis', 'icd10'], dtype='object')

"""

cmsDiagnosis = cms["nameStd"].tolist()
cmsIcd = cms["icd10"].tolist()
# convert items to dictonary as key:value (icd10:diagnosis)
knownIcd = dict(zip(cmsIcd,cmsDiagnosis))

dcDiagnosis = dc["diagnosis"].tolist()
dcIcd = dc["icd10"].tolist()
# convert items to dictonary as key:value (nan icd code:diagnosis)
unknownIcd = dict(zip(dcIcd,dcDiagnosis))
print
# SOLUTION A - USING UNIQUE() IN PANDAS
for col in cms[["nameStd", "icd10"]]:
    # find unique values in dataframe
    cms[col] = cms[col].str.strip()
    print("Unique values in "+ str(col) + " is " + str(cms[col].nunique()))
    # get unique values in each column
    # TO DO: optimize using regex to find texts that are part of the diagnoses
    dx = pd.DataFrame(cms["nameStd"].unique()) # -> stil has non-unique diagnoses eg. Chronic Obstructive Pulmonary Disease 
    icd = pd.DataFrame(cms["icd10"].unique()) # -> removes non-unique ICD codes but does not accurately match the diagnoses to the right ICD code
    # concat each dataframe into single dataframe
    uniqueDf = pd.concat([dx, icd], axis=1)

uniqueDf.to_csv("UniqueGraphCMSDx.csv" , header=["Diagnosis", "ICD_Code"])


# SOLUTION B - USING REGEX
# use regular expressions to determine the icd from cmsIcd and map onto dcIcd
filename = "matched_icd10.csv"
f = open(filename,"w")
# create headers of csv file
headers = "DC_Diagnosis, CMS_ICD, CMS_Diagnosis\n"
f.write(headers)

for countID, diagnosis in unknownIcd.items():
    for refIcd, dx in knownIcd.items():
        m = re.search(diagnosis, dx) # -> didn't match words present in the diagnosis eg reflux is in GERD in Graph CMS and acid reflux in Diagnosis creator
        if m:
            match = m.group()
           #  f.write(diagnosis + "," + refIcd + "," + dx + "\n")

f.close()

# SOLUTION C - USING FUZZYWUZY LIBRARY
""" 
map the columns in cms and dc to match the same ICD codes using the dict property 
to match each diagnoses with unknown ICD codes to those with known ICD codes
"""
dxList = []
for refIcd, dx in knownIcd.items():
    # logic for fuzzywuzzy
    # get the dx and diagnosis which match higher than threshold eg. 80%
    threshold = process.extractOne(dx,dcDiagnosis, scorer = fuzz.token_set_ratio)
    if threshold[1] > 90:
        # get diagnoses with scores > 90 and place dx, dcDiagnosis and icd into one item as a list
        items = [dx,refIcd,str(threshold[0])]
        # append items into one big list
        dxList.append(items)

# Create a dataframe
matcheDx = pd.DataFrame(dxList, columns=["CMSDx", "ICD", "dcDx"])

# write it into excel sheet 
matcheDx.to_csv("matchedDx.csv")


