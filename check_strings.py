#!/usr/bin/env python

import re
import os
import sys
import getopt
from xml.dom.minidom import parse

# usage
def usage ():
    print ""
    print "check_strings.py -d [directory]"
    print "     directory - dir where the values directories"
    print "                 can be found."
    print ""
    sys.exit(0)

# pull all text out of node
def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

# take the dom and return an array with name, string pairs
def handleConfig(dom):
    strings = dom.getElementsByTagName("string")
    return handleStrings(strings)

# take the element with all strings and return array with name, string pairs
def handleStrings(strings):
    parsedArray = []
    for string in strings:
        parsedArray.append(handleString(string))
    return parsedArray

# take a string object and return name, string pair
def handleString(string):
    nameAttr = string.getAttributeNode("name").nodeValue
    stringAttr = getText(string.childNodes)
    return [nameAttr, stringAttr]

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
        for format in dict[name].keys():
            print "  format: %s, count: %d" % (format, dict[name][format])

# walk a dictionary for a specific string and print info for debugging
def printStringDict(dict):
    for format in dict.keys():
        print "   %s: %d" % (format, dict[format])

# compare two dictionaries
def compareDict(masterDict, overrideDict, masterFile, overrideFile):
    match = 0
    print "[Comparing master: %s with override: %s]" % (masterFile, overrideFile)
    for masterString in masterDict.keys():
        try:
            overrideStringDict = overrideDict[masterString]
            masterStringDict = masterDict[masterString]
            if overrideStringDict != masterStringDict:
                if match == 0:
                    print "***Strings files do not match***"
                    match = 1
                print "For string %s, we have a mismatch" % masterString
                print "  master dict:"
                printStringDict(masterStringDict)
                print "  override dict:"
                printStringDict(overrideStringDict)
        except:
            continue

# return dict with master and override directories
# return empty dict if values doesn't exist
def fileList(dir):
    overrideList=[]
    # check for values dir
    if not os.path.isfile('%s/values/strings.xml' % dir):
        return {}

    # find all instances of values- dirs
    for f in os.listdir(dir):
        m = re.match('values-', f)
        if None != m:
            f = '%s/%s/strings.xml' % (dir, f)
            if os.path.isfile(f):
                overrideList.append(f)
    dict={'master':'%s/values/strings.xml' % dir,
          'overrides': overrideList }
    return dict

def main():
    # handle options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h")
    except:
        usage()
        sys.exit(1)

    for opt,arg in opts:
        if opt == "-h":
            ()
        elif opt == "-d":
            basedir=arg

    # make sure basedir is set
    try:
        basedir
    except:
        usage()
        sys.exit(1)

    # get the list of files to parse
    fileDict = fileList(basedir)
    if fileDict == {}:
        print "There is no values/strings.xml file in the directory %s" % basedir
        usage()
        sys.exit(1)

    # get master file
    masterFile = fileDict['master']
    masterDom = parse(masterFile)
    master = genDict(handleConfig(masterDom))

    # get override file list
    overrideList = fileDict['overrides']

    # walk each override file and compare
    for overrideFile in overrideList:
        overrideDom = parse(overrideFile)
        override = genDict(handleConfig(overrideDom))
        compareDict(master, override, masterFile, overrideFile)

main()
