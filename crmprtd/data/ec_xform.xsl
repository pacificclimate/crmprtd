<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:om="http://www.opengis.net/om/1.0"
    xmlns:mpo="http://dms.ec.gc.ca/schema/point-observation/2.1" xmlns:gml="http://www.opengis.net/gml"
    xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    exclude-result-prefixes="mpo"
    version="1.0">
    
    <!-- preserve everything as a default -->
    <xsl:template match="@*|node()" priority="0">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

     <xsl:template name="elements_template">
         <!-- combine tendency_characteristic and tendency_amount to be one float -->
        <xsl:variable name="new_element">
            <xsl:element name="element" namespace="http://dms.ec.gc.ca/schema/point-observation/2.1">
                <xsl:attribute name="name">tendency_amount</xsl:attribute>
                <xsl:attribute name="uom">kPa s-1</xsl:attribute>
                <xsl:attribute name="value">
                    <xsl:if test="mpo:element[@name='tendency_characteristic']/@value='falling'">-</xsl:if>
                    <xsl:value-of select="mpo:element[@name='tendency_amount']/@value"/>
                </xsl:attribute> 
            </xsl:element>
        </xsl:variable>
        <xsl:for-each select="mpo:element">
            <xsl:choose>
                <xsl:when test="@name='tendency_characteristic'">
                     <!-- Nothing.  Get rid of it --> 
                </xsl:when>
                <xsl:when test="@name='tendency_amount'">
                    <xsl:copy-of select="$new_element" />
                </xsl:when>

                <!-- convert compass directions to degrees float -->
                <xsl:when test="@name='wind_direction'">
                    <xsl:element name="element" namespace="http://dms.ec.gc.ca/schema/point-observation/2.1">
                        <xsl:attribute name="name">wind_direction</xsl:attribute>
                        <xsl:attribute name="uom">degree</xsl:attribute>
                        <xsl:attribute name="value">
                            <xsl:choose>
                                <xsl:when test="@value = 'N'">0</xsl:when>
                                <xsl:when test="@value = 'NNE'">22.5</xsl:when>
                                <xsl:when test="@value = 'NE'">45</xsl:when>
                                <xsl:when test="@value = 'ENE'">67.5</xsl:when>
                                <xsl:when test="@value = 'E'">90</xsl:when>
                                <xsl:when test="@value = 'ESE'">112.5</xsl:when>
                                <xsl:when test="@value = 'SE'">135</xsl:when>
                                <xsl:when test="@value = 'SSE'">157.5</xsl:when>
                                <xsl:when test="@value = 'S'">180</xsl:when>
                                <xsl:when test="@value = 'SSW'">202.5</xsl:when>
                                <xsl:when test="@value = 'SW'">225</xsl:when>
                                <xsl:when test="@value = 'WSW'">247.5</xsl:when>
                                <xsl:when test="@value = 'W'">270</xsl:when>
                                <xsl:when test="@value = 'WNW'">292.5</xsl:when>
                                <xsl:when test="@value = 'NW'">315</xsl:when>
                                <xsl:when test="@value = 'NNW'">337.5</xsl:when>
                            </xsl:choose>
                        </xsl:attribute>
                    </xsl:element>                   
                </xsl:when>

                <!-- total cloud cover units are mislabeled and should be 'percent' -->
                <xsl:when test="@name='total_cloud_cover' and @uom='code'">
                    <xsl:element name="element" namespace="http://dms.ec.gc.ca/schema/point-observation/2.1">
                        <xsl:attribute name="name">total_cloud_cover</xsl:attribute>
                        <xsl:attribute name="uom">percent</xsl:attribute>
                        <xsl:attribute name="value"><xsl:value-of select="@value"/></xsl:attribute> 
                    </xsl:element>
                </xsl:when>

                <!-- leave everything else unchanged -->
                <xsl:otherwise>
                    <xsl:copy-of select="." />
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="//om:result//mpo:elements" priority="1">
        <xsl:element name="elements" namespace="http://dms.ec.gc.ca/schema/point-observation/2.1">
            <xsl:call-template name="elements_template"/>
        </xsl:element>
    </xsl:template>
 
</xsl:stylesheet>
