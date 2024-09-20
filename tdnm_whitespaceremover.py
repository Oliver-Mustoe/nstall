#!/usr/bin/env python3
def fileGenerator(nixString):
    newString = nixString.read().replace('\n','')


with open("configuration.nix", 'r') as file:
    newString = file.read().replace('\n','')
    print(newString)
