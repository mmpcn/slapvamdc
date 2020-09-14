<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns:xsams="http://vamdc.org/xml/xsams/1.0">
    
    <xsl:output method="text" indent="no"/>
    <xsl:strip-space elements="*"/>
   
   <xsl:decimal-format name="fixnan" NaN="" />

    <xsl:key name="atomicState" match="/xsams:XSAMSData/xsams:Species/xsams:Atoms/xsams:Atom/xsams:Isotope/xsams:Ion/xsams:AtomicState" use="@stateID"/>
    <xsl:key name="molecularState" match="/xsams:XSAMSData/xsams:Species/xsams:Molecules/xsams:Molecule/xsams:MolecularState" use="@stateID"/>
    <xsl:key name="methodId" match="/xsams:XSAMSData/xsams:Methods/xsams:Method" use="@methodID"/>
    <xsl:key name="sourceId" match="/xsams:XSAMSData/xsams:Sources/xsams:Source" use="@sourceID"/>

    <xsl:variable name="newline"><xsl:text>
</xsl:text></xsl:variable>

    <xsl:template match="/xsams:XSAMSData/xsams:Processes/xsams:Radiative">

       <xsl:variable name="the_max">
         <xsl:for-each select="./xsams:RadiativeTransition/xsams:EnergyWavelength/xsams:Wavelength/xsams:Value">
           <xsl:sort data-type="number" order="descending"/>
           <xsl:if test="position()=1"><xsl:value-of select="."/></xsl:if>
         </xsl:for-each>
       </xsl:variable>
       <xsl:variable name="the_min">
         <xsl:for-each select="./xsams:RadiativeTransition/xsams:EnergyWavelength/xsams:Wavelength/xsams:Value">
           <xsl:sort data-type="number" order="ascending"/>
           <xsl:if test="position()=1"><xsl:value-of select="."/></xsl:if>
         </xsl:for-each>
       </xsl:variable>

        <xsl:value-of select="format-number($the_min,'###0000.0000')"/>
        <xsl:text>, </xsl:text>
        <xsl:value-of select="format-number($the_max,'###0000.0000')"/>
        <xsl:text>, </xsl:text>
        <xsl:value-of select="count(//xsams:RadiativeTransition)"/>
        <xsl:text>,Wavelength region, lines selected, lines processed, Vmicro</xsl:text>
        <xsl:value-of select="$newline"/>
        <xsl:text>                                        Damping parameters   Lande Central</xsl:text>
        <xsl:value-of select="$newline"/>
        <xsl:text>Title, WL, WLUnits, WLMethod,  Speci, Ion, MassNumber, InCgI, InChIKey, LowerStateEnergy(eV),LowerStateUnit, LowerStateConfig, UpperStateEnergy, UpperStateUnit, UpperStateConfig, EinsteinA, OscTrength, WeightedOscStrength, LineStrength, doi, uri</xsl:text>
        <xsl:value-of select="$newline"/>

        <xsl:apply-templates/>
    </xsl:template>
    <xsl:template match="xsams:RadiativeTransition">
        <xsl:variable name="wlUnits" select="./xsams:EnergyWavelength/xsams:Wavelength/xsams:Value/@units"/> 
        <xsl:variable name="methodRef" select="./xsams:EnergyWavelength/xsams:Wavelength/@methodRef"/>
        <xsl:variable name="lowerStateId" select="xsams:LowerStateRef"/>
        <xsl:variable name="upperStateId" select="xsams:UpperStateRef"/>
                <xsl:variable name="lowerState" select="key('atomicState', $lowerStateId)"/>
                <xsl:variable name="upperState" select="key('atomicState', $upperStateId)"/>
                <xsl:variable name="method" select="key('methodId', $methodRef)"/>
                <xsl:variable name="sourceRef" select="$lowerState/xsams:SourceRef"/>
                <xsl:variable name="source" select="key('sourceId', $sourceRef)"/>

                <xsl:text>'</xsl:text>
                <xsl:value-of select="$lowerState/../../../xsams:ChemicalElement/xsams:ElementSymbol"/>
                <xsl:text> </xsl:text>
                <xsl:value-of select="1 + $lowerState/../xsams:IonCharge"/>
                <xsl:text>', </xsl:text>
                <xsl:value-of select='format-number(./xsams:EnergyWavelength/xsams:Wavelength/xsams:Value, "###0000.0000", "fixnan")'/>
                <xsl:text>, </xsl:text>
		<xsl:choose>
                    <xsl:when test="$wlUnits='A'">
                	<xsl:text>Angstrom, </xsl:text>
         	    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="$wlUnits"/>
                        <xsl:text>, </xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:value-of select="$method"/>
                <xsl:text>, </xsl:text>
                <xsl:value-of select="$lowerState/../../../xsams:ChemicalElement/xsams:ElementSymbol"/>
                <xsl:text>, </xsl:text>
                <xsl:value-of select="$lowerState/../xsams:IonCharge"/>
                <xsl:text>, </xsl:text>
                <xsl:value-of select="$lowerState/../../../xsams:Isotope/xsams:IsotopeParameters/xsams:MassNumber"/>
                <xsl:text>, </xsl:text>
                <xsl:value-of select="$lowerState/../xsams:InChI"/>
                <xsl:text>, </xsl:text>
                <xsl:value-of select="$lowerState/../xsams:InChIKey"/>
                <xsl:text>, </xsl:text>
                <xsl:value-of select='format-number(1.239841930E-4 * $lowerState/xsams:AtomicNumericalData/xsams:StateEnergy/xsams:Value, "00.0000", "fixnan")'/>
                <xsl:text>,  </xsl:text>
                <xsl:value-of select="$lowerState/xsams:AtomicNumericalData/xsams:StateEnergy/xsams:Value/@units"/>
                <xsl:text>,  </xsl:text>
                <xsl:value-of select="$lowerState/xsams:AtomicComposition/xsams:Component/xsams:Configuration/xsams:ConfigurationLabel"/>
                <xsl:text>, </xsl:text>
                <xsl:value-of select='format-number(1.239841930E-4 * $upperState/xsams:AtomicNumericalData/xsams:StateEnergy/xsams:Value, "00.0000", "fixnan")'/>
                <xsl:text>,  </xsl:text>
                <xsl:value-of select="$upperState/xsams:AtomicNumericalData/xsams:StateEnergy/xsams:Value/@units"/>
                <xsl:text>,  </xsl:text>
                <xsl:value-of select="$upperState/xsams:AtomicComposition/xsams:Component/xsams:Configuration/xsams:ConfigurationLabel"/>
                <xsl:text>, </xsl:text>
                <xsl:value-of select='format-number(./xsams:Probability/xsams:TransitionProbabilityA/xsams:Value, "0.000", "fixnan")'/>
                <xsl:text>,</xsl:text>
                <xsl:value-of select='format-number(./xsams:Probability/xsams:OscillatorStrength/xsams:Value, "0.000", "fixnan")'/>
                <xsl:text>,</xsl:text>
                <xsl:value-of select='format-number(./xsams:Probability/xsams:WeightedOscillatorStrength/xsams:Value, "0.000", "fixnan")'/>
                <xsl:text>,</xsl:text>
                <xsl:value-of select='format-number(./xsams:Probability/xsams:LineStrength/xsams:Value, "0.000", "fixnan")'/>
                <xsl:text>,</xsl:text>
                <xsl:value-of select="$source/xsams:DigitalObjectIdentifier"/>
                <xsl:text>,</xsl:text>
                <xsl:value-of select="$source/xsams:UniformResourceIdentifier"/>
                <xsl:text>, </xsl:text>
                <xsl:value-of select="$newline"/>
    </xsl:template>
    <xsl:template match="text()|@*"/>
</xsl:stylesheet>
