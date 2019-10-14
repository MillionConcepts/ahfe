This is a work in progress. We consider these data sets feature-complete but incompletely documented.

## contents

All data in the 'clean,' 'split,' and 'depth' folders can be reproduced by running hfe_cleaner.py in the root directory of the repository. Dependencies beyond the Python 3 standard library are astropy, pandas, and numpy. The Anaconda distribution is recommended.

### clean

* This set includes data from the NSSDC and Nagihara sets.
* numbers are standardized to a format equivalent to the NSSDC set. This is a direct decimal representation of IBM 1130 binary floating-point format: signed numbers in exponential representation with eight digits of mantissa and two digits of exponent. However, since the 2019 Nagihara data give time to microsecond precision, rather than the second precision given in Nagihara et. al 2018 and in the NSSDC data (it is the maximum precision permitted by mission epoch time represented with an eight-digit mantissa), we print them with eleven digits of mantissa. 
* It organizes the Nagihara sets in folders by mission and year and leaves them separate from the NSSDC sets. 
* It includes flags for erroneous and missing points (see bitmask description below). These are included in a new column named 'flags'. 
* orders all points by time, correcting inversions and displacements that occur in several source files. 
* corrects a 'bitflip' error that occurs in several source files and a factor-of-ten error that occurs in a15p2f1; the corrected dT values are added as a series labeled dT_corr.

### split

* The 'clean' set further reduced for ease of use: 
* discards most of the flagged points from the 'clean' set
* computes explicit temperature readings for each thermometer rather than giving average temperature and temperature difference values at each thermometer bridge
* converts mission epoch time to Gregorian UTC
* concatenates the Nagihara sets with the NSSDC sets, giving all available temperature data in a single series per thermometer. Retains 'file' distinction; in other words, there is still one table per thermometer bridge.

### depth

* The 'split' set further reduced for ease of use, giving temperature, time, and depth in one table per mission. This set *only* includes depth values for sensors below the surface and discards values for TC4 to avoid ambiguity with TG11A. 

## index of flag bitmask:

* 1: missing data 

*only used in files 1,2,4,5:*

* 10: ambiguous bitflip correction
* 100: outlier in dT
* 1000: outlier in T

*only used in file 3:*

* 10000: outlier in HTR (placeholder; not used due to irregularities in HTR values)
* 100000: outlier in TREF
* 1000000: outlier in TC1
* 10000000: outlier in TC2
* 100000000: outlier in TC3
* 1000000000: outlier in TC4
* 10000000000: time discrepancy

*only used in a15p2f1:*

* 100000000000: cycle change spikes
* 1000000000000: factor of 10 error
* 10000000000000: bit-flipped eclipse events

## warnings

* We maintain the numerical precision given in source datasets even when some of this precision is likely spurious or when retaining it results in series with values of mixed precision.
* We make an assumption about leap seconds in the Nagihara data: that they don't include them. If this is incorrect, there may be a one-to-five second discrepancy between Nagihara data and NSSDC data in our reduced sets. We will verify this assumption shortly. 
* a15p2f1 dT values are 'clipped' or saturated at +20/-30K. There are a number of obvious errors in this range in the NSSDC/Lamont a15p2f1 data. We have corrected two of them (not counting outliers): the obvious 'factor-of-ten' error in early lunations that likely results from incorrect choice of high-sensitivity vs. low sensitivity dT, and the bitflip error. However, there is a major ambiguity in the bitflip correction related to sensitivity selection. The data also do not saturate in exactly the same way as the 1975 Nagihara data, perhaps suggesting a significant difference in the Lamont and Nagihara pipelines. 
* a15p2f4 values are also 'clipped' or saturated at +2/-3K.
* All a17 thermocouples are subject to a great deal of thermal noise. a15 thermocouples are not, or to a much smaller degree. All daytime values for these thermocouples should be used with extreme caution.
* The 'HTR' range appears to be so garbled as to be meaningless. The recorded heater schedule can be found in the PDS descriptions for the NSSDC sets: (a15) https://pds-geosciences.wustl.edu/lunar/a15a-l-hfe-3-thermal-conductivity-v1/a15hfe_0001/catalog/dataset.cat , (a17) https://pds-geosciences.wustl.edu/lunar/a17a-l-hfe-3-thermal-conductivity-v1/a17hfe_0001/catalog/dataset.cat
* 'clean' set uses spaces as column separators for parity with NSSDC set; other sets use commas as column separators. 

## sources

Data in the 'source' folder is taken from:

M. G. S. Langseth, S. J. Keihm, J. L. Chute, H. K. Hills, and D. R. Williams. APOLLO 15 HEAT FLOW THERMAL CONDUCTIVITY RDR SUBSAMPLED V1.0, 15A-L-HFE-3-THERMAL-CONDUCTIVITY-V1.0, 2014. NSSDC ID PSPG-00093, NSSDC ID of older tapes 71-063C-06A.

M. G. S. Langseth, S. J. Keihm, J. L. Chute, H. K. Hills, and D. R. Williams.  APOLLO 17 HEAT FLOW THERMAL CONDUCTIVITY RDR SUBSAMPLED V1.0, A17A-L-HFE-3-THERMAL-CONDUCTIVITY-V1.0, 2014b. NSSDC ID PSPG-00022, NSSDC ID of
older tapes 72-096C-01A

S. Nagihara and Y. Nakamura. Apollo 17 ALSEP ARCSAV Heat Flow Experiment Calibrated Gradient Bridge Temperatures Collection (1975-092 to 1975-181), 2019. URL
http://pds-geosciences.wustl.edu/lunar/
urn-nasa-pds-a17hfe_calibrated_arcsav/data/collection.xml .

S. Nagihara and Y. Nakamura. Apollo 15 ALSEP ARCSAV Heat Flow Experiment Calibrated Gradient Bridge Temperatures Collection (1975-092 to 1975-181), 2019. URL
http://pds-geosciences.wustl.edu/lunar/
urn-nasa-pds-a15hfe_calibrated_arcsav/data/collection.xml .

Ancillary material released along with: S. Nagihara, W.S. Kiefer, P.T. Taylor, and Y. Nakamura. Examination of the long-term subsurface warming observed at the apollo 15 and 17 sites utilizing the newly restored heat flow experiment data from 1975 to 1977.
J Geophysical Research: Planets, April 2018. doi: 10.1029/2018JE005579
