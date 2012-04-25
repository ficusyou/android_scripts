#!/usr/bin/env python

'''
Copyright 2012

@author: Ken Mamitsuka, Lien Mamitsuka
'''

import re
import os
import sys
import getopt
from xml.dom.minidom import parse

# usage
def usage ():
    print ""
    print "verify_strings.py -d [directory] -t [strings|plurals]"
    print "     directory - where the values directories can be found. Example res/"
    print ""
    sys.exit(0)

def getStringsByType(dom, type):
    if type == 'plurals':
        return getPlurals(dom)
    return getStrings(dom)

# take the dom and return strings (an array with string name, string content pairs)
def getStrings(dom):
    strings = dom.getElementsByTagName("string")
    parsedArray = []
    for s in strings:
        nameAttr = s.getAttributeNode("name").nodeValue
        text = getText(s.childNodes)
        parsedArray.append([nameAttr, text])
    return parsedArray

# take the dom and return plurals (an array with plurals_quantity name, string content pairs)
def getPlurals(dom):
    plurals = dom.getElementsByTagName("plurals")
    parsedArray = []
    for p in plurals:
        nameAttr = p.getAttributeNode("name").nodeValue
        items = p.getElementsByTagName("item")
        for i in items:
            quantityAttr = i.getAttributeNode("quantity").nodeValue
            text = getText(i.childNodes)
            parsedArray.append([nameAttr + ' => ' + quantityAttr, text])
    return parsedArray

# pull all text out of node
def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

# generate strings dict for a file
def genDict(array):
    stringsDict={}
    for a in array:
        name = a[0]
        string = a[1]
        stringDict={}
        for n in re.finditer("%[^a-z]*([a-z])", string):
            formatArg=n.group(1)
            try:
                stringDict[formatArg] += 1
            except:
                stringDict[formatArg] = 1

        stringsDict[name] = stringDict
    return stringsDict

# walk the full dictionary and print info for debugging
def printMainDict(dict):
    for name in dict.keys():
        print "string: %s" % name
        for formatArg in dict[name].keys():
            print "  formatArg: %s, count: %d" % (formatArg, dict[name][formatArg])

# walk a dictionary for a specific string and print info for debugging
def printStringDict(dict):
    for formatArg in dict.keys():
        print "   %s: %d" % (formatArg, dict[formatArg])

# compare two dictionaries
def compareDict(masterDict, overrideDict, masterFile, overrideFile):
    print "[Comparing master: %s with override: %s]" % (masterFile, overrideFile)
    for masterString in masterDict.keys():
        try:
            overrideStringDict = overrideDict[masterString]
            masterStringDict = masterDict[masterString]
            if overrideStringDict != masterStringDict:
                print "*** Found mismatched string: %s ***" % masterString
                print "  master dict:"
                printStringDict(masterStringDict)
                print "  override dict:"
                printStringDict(overrideStringDict)
        except:
            continue

# return dict with master and override directories
# return empty dict if values doesn't exist
def fileList(dir, type):
    overrideList=[]
    # check for values dir
    if not os.path.isfile('%s/values/%s.xml' % (dir, type)):
        return {}

    # find all instances of values- dirs
    for f in os.listdir(dir):
        m = re.match('values-', f)
        if None != m:
            f = '%s/%s/%s.xml' % (dir, f, type)
            if os.path.isfile(f):
                overrideList.append(f)
    dict={'master':'%s/values/%s.xml' % (dir, type),
          'overrides': overrideList }
    return dict

def main():
    # handle options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:t:h")
    except:
        usage()
        sys.exit(1)

    type='strngs'
    for opt,arg in opts:
        if opt == "-h":
            ()
        elif opt == "-d":
            basedir=arg
        elif opt == "-t":
            type=arg

    # make sure basedir is set
    try:
        basedir
    except:
        usage()
        sys.exit(1)

    # get the list of files to parse
    fileDict = fileList(basedir, type)
    if fileDict == {}:
        print "No values/%s.xml file in the directory %s" % (type, basedir)
        usage()
        sys.exit(1)

    # get master file
    masterFile = fileDict['master']
    masterDom = parse(masterFile)
    master = genDict(getStringsByType(masterDom, type))

    # get override file list
    overrideList = fileDict['overrides']

    # walk each override file and compare
    for overrideFile in overrideList:
        overrideDom = parse(overrideFile)
        override = genDict(getStringsByType(overrideDom, type))
        compareDict(master, override, masterFile, overrideFile)

main()
