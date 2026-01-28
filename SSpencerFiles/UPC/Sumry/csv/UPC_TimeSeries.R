# Annual time series for UPC stations P1, P5, PB, PC, PJ, PK and PL
# Solar Reflect Tave Tmax Tmin RHave RHmin Wind	WindMax Precip SnowD Tsnow IRTSurfA	IRTSurfX IRTSurfN	Tsoil005 Tsoil15 Tsoil50 SoilH2O Vapres vpdX ClrSky
# Last edit 2/01/26
#
library(ggplot2)
library(gridExtra)
library(dplyr)
# Clear workspace
rm(list=ls())
# Input data for graph
P1_in <- read.csv("P1.csv")
P5_in <- read.csv("P5.csv")
PB_in <- read.csv("PB.csv")
PC_in <- read.csv("PC.csv")
PJ_in <- read.csv("PJ.csv")
PK_in <- read.csv("PK.csv")
PL_in <- read.csv("PL.csv")
# Combine data
data_used <- rbind(P1_in, P5_in, PB_in, PC_in, PJ_in, PK_in, PL_in)
# Select variable to compare between sites
# Solar	Reflect	Tave	Tmax	Tmin	RHave	RHmin	Wind	WindMax
# Precip	SnowD		Tsnow	IRTSurfA	IRTSurfX	IRTSurfN	
# Tsoil005  Tsoil15	Tsoil50	SoilH2O	Vapres	vpdX	ClrSky
title1 <- "Tave"
ylab1 <-"C"
xlab1 <- " "
theme_set(theme_bw())
plot1 <- ggplot() + 
  geom_line(data=data_used, aes(x=Dy, y=Tave, colour=Site), size=0.7) + 
#  geom_line(data=data_used, aes(x=Dy, y=ClrSky), colour="black", size=0.7) +
  labs(title=title1,y=ylab1, x=xlab1)+
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_blank()) +
  theme(plot.title = element_text(vjust = - 10, hjust=0.05, size=10))+
  theme(legend.position="bottom") +
  theme(legend.title = element_blank()) +
  theme(axis.ticks.length=unit(-0.15,"cm"), 
   axis.text.y=element_text(margin = unit(c(t = 0, r = 0.25, b = 0, l = 0),"cm")),
   axis.text.x=element_text(margin = unit(c(t = 0.25, r = 0, b = 0, l = 0),"cm"))) +
  theme(axis.title.x  = element_text(size=8), axis.title.y  = element_text(size=8)) +
  theme(axis.text.x  = element_text(size=8), axis.text.y  = element_text(size=8)) +
   scale_x_continuous(breaks=seq(1, 2555, 365),  
   labels=c("                    2019", "                    2020","                    2021", "                    2022",
   "                    2023","                    2024","                    2025"))
plot1
# Output
#ggsave(file="variable.png", plot1, height = 10, width=15, units="cm",dpi=600)
#




