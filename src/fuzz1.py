from enum import Enum, auto
import sys
import json
import xml.etree.ElementTree as ET
import csv

binary = sys.argv[1]
inputFileName = sys.argv[2]

class FileType(Enum):
    PLAINTEXT = auto()
    CSV = auto()
    JSON = auto()
    XML = auto()
    NONE = auto()


count = 0
xmlTemplate = None
jsonTemplate = {}
#Values can probably be removed but for now it used for debugging
values = []
'''
gives file extension: txt, json => FileType
'''
def classifyFile():
    with open(inputFileName, 'r') as fp:
        try:
            loaded = json.load(fp)
            return [FileType.JSON, loaded]
        except:
            print('not json')

        fp.seek(0)
        try:
            tree = ET.parse(inputFileName)
            return [FileType.XML, tree]
        except:
            print('not xml')

        fp.seek(0)
        lastc = len(fp.readline().split(','))
        if (lastc == 1):
            print('not csv')
        else:
            isCsv = True
            for i in fp.readlines():
                if (len(i.split(',')) != lastc):    
                    isCsv = False
                    print('not csv')
                    break
            if isCsv:
                fp.seek(0)
                return [FileType.CSV, [i.strip() for i in fp.readlines()]]
        
        fp.seek(0)
        return [FileType.PLAINTEXT, fp.read()]

    return [FileType.NONE, "Could not open file"]


def parseCsv(pParsed):
    parsed = []
    cpl = 0
    for line in pParsed:
        parsed += line.split(',')
        cpl = len(line.split(',')) - 1
    return { 'values': parsed, 'cpl': cpl, 'file': FileType.CSV }

def reconstructCsv(fuzzed):
    csv = ""
    count = 0
    for i in fuzzed['values']:
        if count == fuzzed['cpl']:
            count = 0
            csv += i + "\n"
        else:
            csv += i + ","
            count += 1
    return csv


def parseJson(pParsed):
    print(pParsed)
    global jsonTemplate
    global values
    global count
    count = 0
    values = []
    jsonTemplate = {}
    recJson(pParsed)
    return { 'values': values, 'template': jsonTemplate, 'file': FileType.JSON }

def recJson(obj):
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


def reconstructJson(fuzzed):
    obj = fuzzed['template']
    values = fuzzed['values']
    repJson(obj, values)
    return obj

def repJson(obj, values):
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



def parsePlaintext(pParsed):
    return { 'values': pParsed.split('\n')[:-1], 'file': FileType.PLAINTEXT }

def reconstructPlaintext(fuzzed):
    pt = ""
    for i in range(0, len(fuzzed['values'])):
        if i == (len(fuzzed['values']) - 1):
            pt += fuzzed['values'][i]
        else:
            pt += fuzzed['values'][i] + "\n"
    return pt


def parseXml(pParsed):
    global xmlTemplate
    global count
    global values
    values = []
    root = pParsed.getroot()
    recXml(root)
    xmlTemplate = root
    count = 0
    return {'values': values, 'template': xmlTemplate, 'file': FileType.XML }

def recXml(root):
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

def reconstructXml(fuzzed):
    root = fuzzed['template']
    values = fuzzed['values']
    repXml(root, values)
    return ET.tostring(root).decode()
    
def repXml(root, values):
    for child in root:
        if len(child.attrib) > 0:
            replace = {}
            for key in dict(child.attrib).keys():
                replace[values[int(key)]] = values[int(dict(child.attrib)[key])]
            child.attrib = replace
        if child.text is not None and "\n      " not in child.text:
            child.text = values[int(child.text)]
        repXml(child, values)


parsers = {FileType.NONE: lambda: {'values': []}, FileType.JSON: parseJson, FileType.XML: parseXml, FileType.CSV: parseCsv, FileType.PLAINTEXT: parsePlaintext}

'''
convert the input file to something the fuzzer likes (a dictonary)
'''
def getDictFromInput():
    fileType, pparsed = classifyFile()
    return parsers[fileType](pparsed)

'''
convert back the dict from the fuzzer to valid input
'''
def getInputFromDict(dic):
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
        print("Error, invalid file type")
        exit()
    
    print(output)
    return output

example = getDictFromInput()
getInputFromDict(example)