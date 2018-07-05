##!/usr/bin/env python3
## -*- coding: utf-8 -*-
#"""
#Created on Thu Jul  5 11:13:16 2018
#
#@author: kavisha
#"""
#
import json
import jsonschema
import os
#import validictory

filename =  r'example-datasets/extensions/noiseexample2.json'
schemaname = r'extensions/noiseade2.json'

script_dir = os.path.abspath('..')
filepath = os.path.join(script_dir, filename)
schemapath = os.path.join(script_dir, schemaname)

print ("Input File: ",filepath)
print ("Input Schema: ", schemapath)
print ()

fin = open(filepath)
data = fin.read()
j = json.loads(data)
#print (j)

fins = open(schemapath)
schema = fins.read()
js = json.loads(schema)
#print (js)


resolver = jsonschema.RefResolver('file://%s/' % os.path.abspath('..') +"/schema/v07/", None)
#print resolver
try:
    jsonschema.validate(j,js, resolver=resolver)
    print("Passed derived schema.")
except jsonschema.ValidationError as e:
    print (e.message)
except jsonschema.SchemaError as e:
    print (e)


