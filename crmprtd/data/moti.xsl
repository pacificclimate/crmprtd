<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="1.0">
    
    <!-- preserve everything as a default -->
    <xsl:template match="@*|node()" priority="0">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template name="obs_template">
      <xsl:attribute name="type">
	<xsl:choose>
	  <xsl:when test=". = 'air-temperature'">CURRENT_AIR_TEMPERATURE1</xsl:when>
	  <xsl:when test=". = 'atmospheric'">ATMOSPHERIC_PRESSURE</xsl:when>
	  <xsl:when test=". = 'average-scalar-speed-over-60minutes'">MEASURED_WIND_SPEED1</xsl:when>-->
	  <xsl:when test=". = 'average-direction'">MEASURED_WIND_DIRECTION1</xsl:when>
	  <xsl:when test=". = 'standard-deviation-of-direction-over-60minutes'">WIND_DIRECTION_STD_DEVIATION1</xsl:when>
	  <xsl:when test=". = 'dew-point'">DEW_POINT</xsl:when>
	  <xsl:when test=". = 'total-over-hour'">HOURLY_PRECIPITATION</xsl:when>
	  <xsl:when test=". = 'relative-humidity'">RELATIVE_HUMIDITY1</xsl:when>
	  <xsl:when test=". = 'snowfall-accumulation-rate'"></xsl:when>
	  <xsl:when test=". = 'adjacent-snow-depth'">HEIGHT_OF_SNOW</xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="." />
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:attribute>
    </xsl:template>

    <xsl:template name="map_units">
      <xsl:attribute name="units">
	<xsl:choose>
	  <xsl:when test=". = 'degC'">celsius</xsl:when>
	  <xsl:when test=". = 'mb'">millibar</xsl:when>
	  <xsl:when test=". = 'deg'">degrees</xsl:when>
	  <xsl:when test=". = 'km/h'">km h-1</xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="." />
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:attribute>
    </xsl:template>

    <xsl:template match="//observation/*/@type" priority="1">
      <xsl:call-template name="obs_template"/>
    </xsl:template>

    <xsl:template match="//observation/*/value/@units" priority="2">
      <xsl:call-template name="map_units"/>
    </xsl:template>    

</xsl:stylesheet>
