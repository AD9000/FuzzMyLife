# from pwn import *
# import sys
# import xml
# import csv

# b = sys.argv[1]
# template = sys.argv[2]

# # = process(b)
# content = ""
# fp = open(template, "r")
# isCSV = False

# try:
#     reader = csv.reader(fp, delimiter=",")
#     isCSV = True
# except:
#     isCSV = False

# print(isCSV)
# print(list(reader))

# """
# print(b)
# print(template)

# content = "".join(content)
# print(content)


# #p.sendline("header,must,stay,intact")
# inp = "a,b,c,d"
# p.sendline(content)
# p.shutdown()
# """

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
  
def parseXml(pParsed):
  print(pParsed.getroot())


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


print(getDictFromInput())
