from enum import Enum, auto
import json
import xml.etree.ElementTree as ET
import csv
import sys
import copy

from log import *

class FileType(Enum):
    PLAINTEXT = auto()
    CSV = auto()
    JSON = auto()
    XML = auto()
    NONE = auto()


count = 0
xmlTemplate = None
jsonTemplate = {}
# Values can probably be removed but for now it used for debugging
values = []
'''
gives file extension: txt, json => FileType
'''
def classifyFile(inputFileName: str) -> list:
    with open(inputFileName, 'r') as fp:
        try:
            loaded = json.load(fp)
            return [FileType.JSON, loaded]
        except:
            logger.debug('not json')

        fp.seek(0)
        try:
            tree = ET.parse(inputFileName)
            return [FileType.XML, tree]
        except:
            logger.debug('not xml')

        fp.seek(0)
        lastc = len(fp.readline().split(','))
        if (lastc == 1):
            logger.debug('not csv')
        else:
            isCsv = True
            for i in fp.readlines():
                if (len(i.split(',')) != lastc):    
                    isCsv = False
                    logger.debug('not csv')
                    break
            if isCsv:
                fp.seek(0)
                return [FileType.CSV, [i.strip() for i in fp.readlines()]]
        
        fp.seek(0)
        return [FileType.PLAINTEXT, fp.read()]

    return [FileType.NONE, "Could not open file"]

'''
Parses the csv file to generate input dict for the fuzzer
@param: pParsed: Partially parsed input from classifyFile()
'''
def parseCsv(pParsed) -> dict:
    parsed = []
    cpl = 0
    for line in pParsed:
        splitLine = line.split(',')
        parsed += splitLine
        cpl = len(splitLine) - 1
    return { 'values': parsed, 'cpl': cpl, 'file': FileType.CSV }


'''
Reconstructs valid csv input to pass into the binary
@param: fuzzed: Mutated input from the fuzzer
'''
def reconstructCsv(fuzzed: dict) -> str:
    csv = []
    count = 0
    for i in fuzzed['values']:
        if count == fuzzed['cpl']:
            count = 0
            csv.extend([str(i), "\n"])
        else:
            csv.extend([str(i), ","])
            count += 1
    return ''.join(csv)


'''
Recursively parse json and generate template to be used for reconstruction 
@param: obj: valid json to be parsed
'''
def recJson(obj) -> None:
    global jsonTemplate
    global count
    global values
    for key in obj.keys():
        if isinstance(obj[key], list):
            jsonTemplate[key] = []
            for value in obj[key]:
                jsonTemplate[key].append(count)
                count = count + 1
                values.append(value)
        elif isinstance(obj[key], dict):
            recJson(obj[key])
        else:
            jsonTemplate[key] = count
            count = count + 1
            values.append(obj[key])

'''
Parses the json file to generate input dict for the fuzzer
@param: pParsed: Partially parsed input from classifyFile()
'''
def parseJson(pParsed)-> dict:
    logger.debug(pParsed)
    global jsonTemplate
    global values
    global count
    count = 0
    values = []
    jsonTemplate = {}
    recJson(pParsed)
    return { 'values': values, 'template': jsonTemplate, 'file': FileType.JSON }


'''
Recursively replace template with values to create valid json input 
@param: obj: template to be used
@param: values: values dict to be inserted
'''
def repJson(obj, values) -> None:
    for key in obj.keys():
        if isinstance(obj[key], list):
            replist = []
            for value in obj[key]:
                replist.append(values[value])
            obj[key] = replist
        elif isinstance(obj[key], dict):
            repJson(obj[key], values)
        else:
            obj[key] = values[obj[key]]

'''
Reconstructs valid json input to pass into the binary
@param: fuzzed: Mutated input from the fuzzer
'''
def reconstructJson(fuzzed: dict) -> str:
    obj = copy.deepcopy(fuzzed['template'])
    values = fuzzed['values']
    repJson(obj, values)
    return json.dumps(obj)


'''
Parses the plaintext file to generate input dict for the fuzzer
@param: pParsed: Partially parsed input from classifyFile()
'''
def parsePlaintext(pParsed) -> dict:
    return { 'values': pParsed.split('\n')[:-1], 'file': FileType.PLAINTEXT }


'''
Reconstructs valid plaintext input to pass into the binary
@param: fuzzed: Mutated input from the fuzzer
'''
def reconstructPlaintext(fuzzed: dict) -> str:
    pt = ""
    for i in range(0, len(fuzzed['values'])):
        if i == (len(fuzzed['values']) - 1):
            pt += str(fuzzed['values'][i])
        else:
            pt += str(fuzzed['values'][i]) + "\n"
    return pt

'''
Recursively parse xml and generate template to be used for reconstruction 
@param: root: Root node of the XML elementTree
'''
def recXml(root) -> None:
    global count
    global values
    for child in root:
        if len(child.attrib) > 0:
            replace = {}
            for key in dict(child.attrib).keys():
                values.append(key)
                values.append(dict(child.attrib)[key])
                replace[str(count)] = str(count + 1)
                count = count + 2
            child.attrib = replace
        if child.text is not None and "\n      " not in child.text:
            values.append(child.text)
            child.text = str(count)
            count = count + 1
        recXml(child)

'''
Parses the xml file to generate input dict for the fuzzer
@param: pParsed: Partially parsed input from classifyFile()
'''
def parseXml(pParsed) -> dict:
    global xmlTemplate
    global count
    global values
    values = []
    root = pParsed.getroot()
    recXml(root)
    xmlTemplate = root
    count = 0
    return {'values': values, 'template': xmlTemplate, 'file': FileType.XML }


'''
Recursively replace template with values to create valid xml input
@param: root: Root node of the xml element tree template
@param: values: Values array to be inserted into the template
'''
def repXml(root, values) -> None:
    for child in root:
        if len(child.attrib) > 0:
            replace = {}
            for key in dict(child.attrib).keys():
                replace[values[int(key)]] = values[int(dict(child.attrib)[key])]
            child.attrib = replace
        if child.text is not None and "\n      " not in child.text:
            child.text = values[int(child.text)]
        repXml(child, values)

'''
Reconstructs valid xml input to pass into the binary
@param: fuzzed: Mutated input from the fuzzer
'''
def reconstructXml(fuzzed: dict) -> str:
    root = copy.deepcopy(fuzzed['template'])
    values = fuzzed['values']
    for i in range(0, len(values)):
        if isinstance(values[i], int):
            values[i] = str(values[i])
    repXml(root, values)
    return ET.tostring(root).decode()


'''
Valid parsers currently supported by the parser
'''
parsers = {FileType.NONE: lambda: {'values': []}, FileType.JSON: parseJson, FileType.XML: parseXml, FileType.CSV: parseCsv, FileType.PLAINTEXT: parsePlaintext}

'''
convert the input file to something the fuzzer likes (a dictionary)
'''
def getDictFromInput(inputFileName: str) -> dict:
    fileType, pparsed = classifyFile(inputFileName)
    logger.debug(fileType)
    return parsers[fileType](pparsed)

'''
convert back the dictionary from the fuzzer to valid input
'''
def getInputFromDict(dic: dict) -> str:
    output = ""
    if dic['file'] == FileType.JSON:
        output = reconstructJson(dic)
    elif dic['file'] == FileType.PLAINTEXT:
        output = reconstructPlaintext(dic)
    elif dic['file'] == FileType.CSV:
        output = reconstructCsv(dic)
    elif dic['file'] == FileType.XML:
        output = reconstructXml(dic)
    else:
        logger.info("Error, invalid file type")
        exit()
    
    return output