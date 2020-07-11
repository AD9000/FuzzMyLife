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
    for line in pParsed:
        parsed += line.split(',')
    return { 'values': parsed }

def parseJson(pParsed):
    return { 'values': list(pParsed.values()) }

def parsePlaintext(pParsed):
    return pParsed.split('\n')[:-1]

count = 0
xmlTemplate = None
values = []
def parseXml(pParsed):
    global xmlTemplate
    global count
    root = pParsed.getroot()
    recXml(root)
    xmlTemplate = root
    count = 0
    global values
    print(values)
    return {'values': values, 'template': xmlTemplate, 'File': FileType.XML}

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
def getInputFromDict(dic, fileType):
    pass


example = getDictFromInput()
#print(readXML())
#print(ET.tostring(xmlTemplate).decode())
#print(reconstructXml())
print(reconstructXml(example))