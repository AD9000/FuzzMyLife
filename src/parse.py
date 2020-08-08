import json
import xml.etree.ElementTree as ET
import csv
import sys
import copy

from log import *
from fileTypes import *

# count = 0
# xmlTemplate = None
# jsonTemplate = {}
# Values can probably be removed but for now it used for debugging
# values = []
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
def reconstructCsv(fuzzed: dict) -> bytes:
    csv = []
    count = 0
    for i in fuzzed['values']:
        if not isinstance(i, bytes):
            i = str(i).encode() # bad?
        if count == fuzzed['cpl']:
            count = 0
            csv.extend([i, b"\n"])
        else:
            csv.extend([i, b","])
            count += 1
    return b''.join(csv)


'''
Recursively parse json and generate template to be used for reconstruction 
@param: obj: valid json to be parsed
'''
# can't deal with lists of dictionaries
def recJson(obj: dict, values: list = [], jsonTemplate: dict = {}, count: int = 0, tags: list = []) -> (list, dict):
    # global jsonTemplate
    # global count
    # global values
    for key in obj.keys():
        tags.append(key)
        tmpkey = len(tags)-1
        if isinstance(obj[key], list):
            jsonTemplate[tmpkey] = []
            for value in obj[key]:
                if isinstance(value, dict):
                    newTemplate = {}
                    values, newTemplate, count, tags = recJson(value, values,  newTemplate, count, tags)
                    jsonTemplate[tmpkey].append(newTemplate)
                else:
                    jsonTemplate[tmpkey].append(count)
                    count = count + 1
                    values.append(value)
        elif isinstance(obj[key], dict):
            newTemplate = {}
            values, newTemplate, count, tags = recJson(obj[key], values,  newTemplate, count, tags)
            jsonTemplate[tmpkey] = newTemplate
        else:
            jsonTemplate[tmpkey] = count
            count = count + 1
            values.append(obj[key])
    return values, jsonTemplate, count, tags

def recList(obj: dict, values: list = [], jsonTemplate: dict = {}, count: int = 0, tags: list = []) -> (list, dict):
    pass

'''
Parses the json file to generate input dict for the fuzzer
@param: pParsed: Partially parsed input from classifyFile()
'''
def parseJson(pParsed)-> dict:
    logger.debug(pParsed)
    # global jsonTemplate
    # global values
    # global count
    # count = 0
    # values = []
    # jsonTemplate = {}
    values, jsonTemplate, _, tags = recJson(pParsed)
    # print({ 'values': values, 'tags': tags, 'template': jsonTemplate, 'file': FileType.JSON })
    return { 'values': values, 'tags': tags, 'template': jsonTemplate, 'file': FileType.JSON }


'''
Recursively replace template with values to create valid json input 
@param: tmpl: template to be used
@param: values: values dict to be inserted
'''
def repJson(tmpl: dict, values: list, tags: list) -> None:
    print(tmpl, values, tags)
    obj = {}
    for tmpkey in tmpl.keys():
        key = tags[tmpkey]
        if isinstance(tmpl[tmpkey], list):
            replist = []
            for value in tmpl[tmpkey]:
                if isinstance(value, dict):
                    newobj = repJson(value, values, tags)
                    replist.append(newobj)
                else:
                    replist.append(values[value])
            obj[key] = replist
        elif isinstance(tmpl[tmpkey], dict):
            newobj = repJson(tmpl[tmpkey], values, tags)
            obj[key] = newobj
        else:
            print(tmpl[tmpkey])
            obj[key] = values[tmpl[tmpkey]]
    return obj

'''
Reconstructs valid json input to pass into the binary
@param: fuzzed: Mutated input from the fuzzer
'''
def reconstructJson(fuzzed: dict) -> bytes:
    # obj = copy.deepcopy(fuzzed['template'])
    values = fuzzed['values']
    print("\n\n\n" + str(values) + "\n\n\n")
    obj = repJson(fuzzed['template'], values, fuzzed['tags'])
    print("obj: " + str(obj))
    return json.dumps(obj, ensure_ascii=False).encode()
    # I don't think ensure_ascii is actually doing anything


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
def reconstructPlaintext(fuzzed: dict) -> bytes:
    pt = b""
    for i in range(0, len(fuzzed['values'])):
        if isinstance(fuzzed['values'][i], bytes):
            pt += fuzzed['values'][i]
        else:
            pt += str(fuzzed['values'][i]).encode() # bad
        if i < (len(fuzzed['values']) - 1):
            pt += b"\n"
    return pt

'''
Recursively parse xml and generate template to be used for fuzzing & reconstruction 
@param: root: Root node of the XML elementTree
'''
def recXml(root, values: list = [], vcount: int = 0, tags: list = []) -> (list, int, list):
    tags.append(root.tag)
    root.tag = str(len(tags)-1)
    # print(root.tag)

    for child in root:
        # print(child.tag, child.attrib, child.text)
        if len(child.attrib) > 0:
            replace = {}
            for key in dict(child.attrib).keys():
                values.append(key)
                values.append(dict(child.attrib)[key])
                replace[str(vcount)] = str(vcount + 1)
                vcount = vcount + 2
            child.attrib = replace
        if child.text is not None and "\n      " not in child.text:
            values.append(child.text)
            child.text = str(vcount)
            vcount = vcount + 1
        values, vcount, tags = recXml(child, values, vcount, tags)
    return values, vcount, tags

'''
Parses the xml file to generate input dict for the fuzzer
@param: pParsed: Partially parsed input from classifyFile()
'''
def parseXml(pParsed) -> dict:
    # global xmlTemplate
    # global count
    root = pParsed.getroot()
    values, _, tags = recXml(root)
    # print(tags)
    xmlTemplate = root
    # count = 0
    return {'values': values, 'tags': tags, 'template': xmlTemplate, 'file': FileType.XML }


'''
Recursively replace template with values to create valid xml input
@param: root: Root node of the xml element tree template
@param: values: Values array to be inserted into the template
'''
def repXml(root, values, tags) -> None:
    root.tag = str(tags[int(root.tag)])
    # print(root.tag)
    for child in root:
        # print(child.tag, child.attrib)
        # child.attrib is a dictionary where each field contains the values index of its new value
        if len(child.attrib) > 0:
            replace = {}
            for key in dict(child.attrib).keys():
                replace[values[int(key)]] = values[int(dict(child.attrib)[key])]
            child.attrib = replace
            # print(child.attrib)
        if child.text is not None and "\n      " not in child.text:
            child.text = values[int(child.text)]
        repXml(child, values, tags)

'''
Reconstructs valid xml input to pass into the binary
@param: fuzzed: Mutated input from the fuzzer
'''
def reconstructXml(fuzzed: dict) -> bytes:
    root = copy.deepcopy(fuzzed['template'])
    values = fuzzed['values']
    for i in range(0, len(values)):
        if isinstance(values[i], int):
            values[i] = str(values[i])
    repXml(root, values, fuzzed['tags'])
    return ET.tostring(root)


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
    a = parsers[fileType](pparsed)
    print(a)
    return a

'''
convert back the dictionary from the fuzzer to valid input
'''
def getInputFromDict(dic: dict) -> bytes:
    output = b""
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