#!/usr/bin/env python
##########################################################################################
# parsexsams.py
#
# parses a VAMDC xsams file and prints radiative transition information in csv format
#
# version 1.0
# Author: Margarida Castro Neves (mcneves@ari.uni-heidelberg.de)
#
#########################################################################################
import xml.etree.cElementTree as ET
import sys

prefix=''

# define dictionaries for easier search

elem_dict={}    # speciesID : elementSymbol
mass_dict={}	# speciesID : massNumber
state_dict={}   # stateID   : state element
ion_dict={}     # speciesID : isotope ion
method_dict={}  # methodID  : method
source_dict={}  # sourceID  : source

def parseXSAMS(file_name):

   global prefix
   global atoms
   global state
   global radtrans
   global methods
   global sources

   # Parse XML with ElementTree
   tree = ET.ElementTree(file=file_name)
   print(tree.getroot())
   root = tree.getroot()
   print("tag=%s, attrib=%s" % (root.tag, root.attrib))
   prefix = './/'+root.tag.replace('XSAMSData','')
   print prefix

   # get list of atoms
   atoms = root.findall(prefix+'Atom')

   # get list of methods
   methods=root.findall(prefix+'Method')

   # get list of sources
   sources=root.findall(prefix+'Source')

   # create dictionaries to optimise search
   createDicts()

   # get list of Processes/RadiativeTransitions

   radtrans = root.findall('.//{http://vamdc.org/xml/xsams/1.0}RadiativeTransition')

   # Parse and print as csv

   print "WL;WLUnit;WLMethod;Elem;Mass;Charge;upperEnergy;upperConfig;LowerEnergy;lowerConfig; einsteinA; oscStrehgth; weightedOscStrength; lineStrength; doi; uri" 
   for transition in radtrans:
	#probEl= transition.find(prefix+'TransitionProbability')
	species=transition.find(prefix+'SpeciesRef').text
        wavelengths = getWavelengths(transition)
        for wavelength in wavelengths: 
	    print "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (getWavelengthInfo(wavelength),getElement(species), getMass(species), getCharge(species), getUpperStateInfo(transition), getLowerStateInfo(transition), getProbabilities(transition), getInChI(species), getInChIKey(species), getPublicationInfo(species))

############################
# 
def getText(elem):
    if elem is None:
	return ''
    return elem.text

#
def getValue(elem):
    if elem is None:
	return ''
    return elem.find(prefix+'Value').text

# 
def getUnit(elem):
    if elem is None:
	return ''
    val = elem.find(prefix+'Value')
    unit= val.get('units')
    if unit=='A':
	unit='Angstrom'
    return unit

#
def getMethod(elem):
    if elem is None:
	return ''
    id = elem.get('methodRef')
    if id is None:
	return ''
    return method_dict[id]

#
def createDicts():

   for m in methods:
      method_dict[m.get('methodID')]=getText(m.find(prefix+'Category'))
       
   for s in sources:
      source_dict[s.get('sourceID')]=s
   print sources


   for atom in atoms:
      massNumber=''
      symbol=getText(atom.find(prefix+'ElementSymbol'))
      isotopes=atom.find(prefix+'Isotope')
      for isotope in isotopes:
         tag=isotope.tag
	 if tag.endswith('IsotopeParameters'):
	    massNumber = getText(isotope.find(prefix+'MassNumber'))
         else: #Ion
	 # ions: needed ipncharge, atomic state
	    ioncharge= getText(isotope.find(prefix+'IonCharge'))
	    speciesID=isotope.get('speciesID')
	    elem_dict[speciesID]=symbol
	    mass_dict[speciesID]=massNumber
	    ion_dict[speciesID]=isotope
	   # print "charge: "+ioncharge.text+ "ID= "+speciesID
	    states= isotope.findall(prefix+'AtomicState')
	    for stateEl in states:
	   #    print stateEl.get('stateID')
	       state_dict[stateEl.get('stateID')]=stateEl


#
def getWavelengths ( transition ):
   wlElem = transition.find(prefix+'EnergyWavelength')
   return wlElem.findall(prefix+'Wavelength')

#
def getWavelengthInfo ( wavelength ):
   ## TO DO check if air/vacuum flag is there, if yes convert vacElem = transition.find(prefix+'RadTransWavelengthVacuum')
   wl = getValue(wavelength)
   unit = getUnit(wavelength)
   method=getMethod(wavelength)
   return " %s;%s;%s" % (wl, unit, method)

#
def getElement(species):
   return elem_dict[species]

#
def getMass(species):
   return mass_dict[species]

#
def getCharge(species):
   return getText(ion_dict[species].find(prefix+'IonCharge'))

#
def getInChI(species):
   return getText(ion_dict[species].find(prefix+'InChI'))

#
def getInChIKey(species):
   return getText(ion_dict[species].find(prefix+'InChIKey'))

#
def getUpperStateInfo(transition):
    state = transition.find(prefix+'UpperStateRef').text
    return getStateInfo(state)

#
def getLowerStateInfo(transition):
    state = transition.find(prefix+'LowerStateRef').text
    return getStateInfo(state)

#
def getStateInfo(stateref):
    #print stateref
    state = state_dict[stateref]
    #print state
    energy= getValue(state.find(prefix+'StateEnergy'))
    config = getText(state.find(prefix+'ConfigurationLabel'))
    # return also energy unit ?
    stateinfo="%s;%s" % (energy,config)
    return stateinfo 

#
def getProbabilities(transition):
    prob=transition.find(prefix+'Probability')
    einsteinA = getValue(prob.find(prefix+'TransitionProbabilityA'))
    oscStrength = getValue(prob.find(prefix+'OscillatorStrength'))
    woscStrength = getValue(prob.find(prefix+'WeightedOscillatorStrength'))
    lineStrength = getValue(prob.find(prefix+'TransitionLineStrength'))
    return "%s;%s;%s;%s" % (einsteinA, oscStrength, woscStrength, lineStrength)

#
def getPublicationInfo(speciesID):
    doi=''
    uri=''
    sourceRef = getText(ion_dict[speciesID].find(prefix+'SourceRef'))
    if sourceRef in source_dict:   # not all species have a source
        doi=getText(source_dict[sourceRef].find(prefix+'DigitalObjectIdentifier'))
        uri=getText(source_dict[sourceRef].find(prefix+'UnifiedResourceIdentifier'))
    return "%s;%s" % (doi, uri)

########

if __name__ == "__main__":
    if len(sys.argv) <> 2:
        print "usage: "+sys.argv[0]+" <xsams_filename>"
    else:
        parseXSAMS(sys.argv[1])
