#!/usr/bin/env python3
################################################################################
# parsexsams.py
#
# parses a VAMDC xsams file and prints radiative transition information in csv 
# format, mapping from VAMDCXSAMS to LineTAP datamodel
#
# version 2.0
# Author: Margarida Castro Neves (mcneves@ari.uni-heidelberg.de)#
#
################################################################################
import xml.etree.cElementTree as ET
import sys
from astropy import units as u

prefix=''

# define dictionaries for easier search

elem_dict={}       # speciesID : elementSymbol
specstate_dict={}  # stateID : speciesID
mass_dict={}         # speciesID : massNumber
state_dict={}      # stateID   : state element
species_dict={}    # speciesID : isotope ion or molecule
method_dict={}     # methodID  : method
source_dict={}     # sourceID  : source

def parseXSAMS(file_name):

   global prefix
   global atoms
   global state
   global radtrans
   global methods
   global sources
   global molecules

   # Parse XML with ElementTree
   tree = ET.ElementTree(file=file_name)
   #print(tree.getroot())
   root = tree.getroot()
   #print("tag=%s, attrib=%s" % (root.tag, root.attrib))
   prefix = './/'+root.tag.replace('XSAMSData','')

   # get list of atoms
   atoms = root.findall(prefix+'Atom')

   # get list of molecules
   molecules = root.findall(prefix+'Molecule')

   # get list of methods
   methods=root.findall(prefix+'Method')

   # get list of sources
   sources=root.findall(prefix+'Source')

   # create dictionaries to optimise search
   createDicts()

   # get list of Processes/RadiativeTransitions

   radtrans = root.findall('.//{http://vamdc.org/xml/xsams/1.0}RadiativeTransition')

   # Parse and print as csv

   print ("title, vacuum_wavelength(unit), vacuum_wavelength_error, method, stoichiometric_formula, mass_number, ion_charge, upper_state_energy, upper_state_configuration, lower_state_energy, lower_state_configuration, einstein_a,  oscillator_strehgth,  weighted_oscillator_strength,  line_strength, inchi, inchikey,  line_reference_doi,  line_reference_uri" )
   for transition in radtrans:
      species=getSpeciesID(transition)
      wavelengths = getWavelengths(transition)
      for wavelength in wavelengths: 
         print ("%s %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (getFormula(species),getCharge(species),getWavelengthInfo(wavelength), getFormula(species), getMass(species), getCharge(species), getUpperStateInfo(transition), getLowerStateInfo(transition), getProbabilities(transition), getInChI(species), getInChIKey(species), getPublicationInfo(species)))


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
    if unit=="A":
      unit="Angstrom"
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
def getAccuracy(elem):
    if elem is None:
      return ''
    acc= elem.find(prefix+'Accuracy')
    if acc is None:
      return ''
    return acc.text

#
def createDicts():

   for m in methods:
      method_dict[m.get('methodID')]=getText(m.find(prefix+'Category'))
       
   for s in sources:
      source_dict[s.get('sourceID')]=s

   for atom in atoms:
      massNumber=''
      formula=getText(atom.find(prefix+'ElementSymbol'))
      isotopes=atom.find(prefix+'Isotope')
      for isotope in isotopes:
         tag=isotope.tag
         if tag.endswith('IsotopeParameters'): 
             massNumber = getText(isotope.find(prefix+'MassNumber'))
         else: #Ion
       # ions: needed ioncharge, atomic state
            ioncharge = getText(isotope.find(prefix+'IonCharge'))
            speciesID=isotope.get('speciesID')
            elem_dict[speciesID]=formula
            mass_dict[speciesID]=massNumber
            species_dict[speciesID]=isotope
            states= isotope.findall(prefix+'AtomicState')
            for stateEl in states:
               stateID =  stateEl.get('stateID')
               if stateID :
                  state_dict[stateID]=stateEl
                  specstate_dict[stateID]=speciesID
   for molecule in molecules:
      massNumber=''
      formula=getText(molecule.find(prefix+'StoichiometricFormula'))
      ioncharge= getText(molecule.find(prefix+'IonCharge'))
      speciesID=molecule.get('speciesID')
      elem_dict[speciesID]=formula
      mass_dict[speciesID]=massNumber
      species_dict[speciesID]=molecule
   # print "charge: "+ioncharge.text+ "ID= "+speciesID
      states= molecule.findall(prefix+'MolecularState')
      for stateEl in states:
         stateID =  stateEl.get('stateID')
         #print "%s %s" %(stateID, speciesID)
         state_dict[stateID]=stateEl
         specstate_dict[stateID]=speciesID
#
#def is_atom ( species ):
#
#   if  in species_dict:
#      return True
#   else:
#      return False
   
#
def getWavelengths ( transition ):
   wlElem = transition.find(prefix+'EnergyWavelength')
   allWLs = wlElem.findall(prefix+'Wavelength')
   if allWLs != []:
      return allWLs
   else:
        allWLs = wlElem.findall(prefix+'Wavenumber')
   if allWLs != []:
      return allWLs
   else:
      allWLs=wlElem.findall(prefix+'Frequency')
   if allWLs != []:
      return allWLs
   else:
      allWLs=wlElem.findall(prefix+'Wavenumber')
   if allWLs != []:
      return allWLs
   else:
      allWLs=wlElem.findall(prefix+'Energy')
   return allWLs

#
def getWavelengthInfo ( wavelength ):
   wl = getValue(wavelength)
   error= getAccuracy(wavelength) ## TODO Error
   unit = getUnit(wavelength)
   ## UNTESTED! check if air/vacuum flag is there, if yes convert air to vacuum
   if isVacuum(wavelength):
      wl = wl * getAirToVac(wavelength)
   if unit != "Angstrom":
      wl = convertToAngstrom(float(wl), unit)
      unit="Angstrom"
   method=getMethod(wavelength)
   return " %s (%s), %s, %s" % (wl, unit, error, method)

#
def isVacuum(wavelength):
   isvac=wavelength.get('Vacuum')
   if isvac:
      return True
   return False

#
def getAirToVac(wavelength):
   factor=wavelength.find(prefix+'AirToVac')
   if factor:
      return factor
   else:
      return 1.0

#
def getSpeciesID(transition):
   #species=transition.find(prefix+'SpeciesRef')
   # some databases do not have SpeciesRef
   # have to get Species Reference from the states
   #if species is None:
   state = transition.find(prefix+'UpperStateRef').text      
   species=specstate_dict[state]
   #else:
   #   species=species.text
   #print "Species="+species
   return species
      
#
def getFormula(species):
   return elem_dict[species]

#
def getMass(species):
   return mass_dict[species]

#
def getCharge(species):
   # if atom or molecule!!!!!!!!!! TO DO
   return getText(species_dict[species].find(prefix+'IonCharge'))

#
def getInChI(species):
   return getText(species_dict[species].find(prefix+'InChI'))

#
def getInChIKey(species):
   return getText(species_dict[species].find(prefix+'InChIKey'))

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
    config = getText(state.find(prefix+'Description'))
    # return also energy unit ?    
    stateinfo="%s (J), %s" % (getEnergy(state), config)
    return stateinfo 

#
def getEnergy(state):
    stateEnergy=state.find(prefix+'StateEnergy')
    if stateEnergy is None:
       return ''
    energy= getValue(stateEnergy)
    unit= getUnit(stateEnergy)
    if energy is None:
       return ''
    # check if there's  a reference to a ground state
    groundStateID = stateEnergy.get('energyOrigin')
    if groundStateID is None:
       groundStateEnergy=0
    else:
       try:
         groundState=state_dict[groundStateID]
         groundStateEnergy=getValue(groundState.find(prefix+'StateEnergy')) 
           #print "GROUNDSTATE /State Energy: %s  %s" % (groundStateEnergy, energy)
         energy = float(energy) - float(groundStateEnergy)  ### IS THIS CORRECT?
       except KeyError:
         groundstate=0
    #print "------Energy %s %s " % (energy,unit)
    return convertToJ(float(energy),unit)
#
def getProbabilities(transition):
    prob=transition.find(prefix+'Probability')
    einsteinA = getValue(prob.find(prefix+'TransitionProbabilityA'))
    oscStrength = getValue(prob.find(prefix+'OscillatorStrength'))
    woscStrength = getValue(prob.find(prefix+'WeightedOscillatorStrength'))
    lineStrength = getValue(prob.find(prefix+'TransitionLineStrength'))
    return "%s, %s, %s, %s" % (einsteinA, oscStrength, woscStrength, lineStrength)

#
def getPublicationInfo(speciesID):
    doi=''
    uri=''
    sourceRef = getText(species_dict[speciesID].find(prefix+'SourceRef'))
    if sourceRef in source_dict:   # not all species have a source
        doi=getText(source_dict[sourceRef].find(prefix+'DigitalObjectIdentifier'))
        uri=getText(source_dict[sourceRef].find(prefix+'UnifiedResourceIdentifier'))
    return "%s, %s" % (doi, uri)

#
def convertToAngstrom(value, unit):
      v = (value * u.Unit(unit))
      return v.to(u.angstrom, equivalencies=u.spectral())
#
def convertToJ(value, unit):
      v = value * u.Unit(unit)
      return v.to(u.J, equivalencies=u.spectral())

########

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ("usage: "+sys.argv[0]+" <xsams_filename>")
    else:
        parseXSAMS(sys.argv[1])
