# CSV-comparer-with-Pandas
## Using Regex, .unique() and Fuzzywuzzy library to try compare values in different Data Frames
> ### Read CSV files and convert them into a dataframe
```sh
cms = pd.read_csv("GraphCMSDiagnoses.csv")
dc = pd.read_csv("DiagnosisCreatorDiagnoses.csv")
```
 > ### convert entries in individual headers into list and combine them into dictonary as key:value
 ```sh
 cmsDiagnosis = cms["nameStd"].tolist()
cmsIcd = cms["icd10"].tolist()
# convert items to dictonary as key:value (icd10:diagnosis)
knownIcd = dict(zip(cmsIcd,cmsDiagnosis))
dcDiagnosis = dc["diagnosis"].tolist()
dcIcd = dc["icd10"].tolist()
# convert items to dictonary as key:value (nan icd code:diagnosis)
unknownIcd = dict(zip(dcIcd,dcDiagnosis))
 ```
> ## Solution 1
> ### Identify unique values in GraphCMS Diagnoses using pandas .unique()
Using the for loop values in each header are reiterated to identify unique values. These unique values are then placed in individual dataframes and later concancatenated in single dataframe.
```sh 
for col in cms[["nameStd", "icd10"]]:
    # find unique values in dataframe
    cms[col] = cms[col].str.strip()
    print("Unique values in "+ str(col) + " is " + str(cms[col].nunique()))
    # get unique values in each column
    dx = pd.DataFrame(cms["nameStd"].unique()) # TODO : stil has non-unique diagnoses eg. Chronic Obstructive Pulmonary Disease 
    icd = pd.DataFrame(cms["icd10"].unique()) # TODO : removes non-unique ICD codes but does not accurately match the diagnoses to the right ICD code
    # concat each dataframe into single dataframe
    uniqueDf = pd.concat([dx, icd], axis=1)
```
> ## Solution 2
> ### Identify newly matched Diagnoses and ICD codes from GraphCMS to the diagnoses in the Diagnosis Creator using regex
```sh
for countID, diagnosis in unknownIcd.items():
    for refIcd, dx in knownIcd.items():
        m = re.search(diagnosis, dx) # -> didn#t match words present in the diagnosis eg reflux is in GERD in Graph CMS and acid reflux in Diagnosis creator
        if m:
            match = m.group()
            f.write(diagnosis + "," + refIcd + "," + dx + "\n")
```

> ## Solution 3
> ### use fuzzywuzzy library to match diagnosis based on the string using the [Levenshtein method](https://www.datacamp.com/community/tutorials/fuzzy-string-python)
```sh
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
```
