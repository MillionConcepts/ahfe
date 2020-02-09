# Apollo HFE collected data bundle documentation

## Introduction

This bundle collects all available calibrated data from the Apollo 15 and 17
Heat Flow Experiments (AHFE), addresses several errors and artifacts in these
data, and presents them in several reduced formats designed for compatibility
and ease of access. This document is intended to serve as high-level
documentation for these new reduced data sets. It is not a detailed description
of the AHFE as such. We recommend that readers unfamiliar with the AHFE begin by
reading David R. Williams' excellent overviews of the Apollo 15 and 17 Apollo
Lunar Surface Experiment Packages (ALSEP) and HFEs [^1] [^2] [^3] [^4] (included
in the /hfe subdirectory of this collection) .

**Note to PDS reviewer: this paragraph is a placeholder reference to a 
forthcoming publication by our team in P&SS which provides a narrative of the
data's history and our ingestion processes that is more detailed than we
consider desirable for primary documentation [^5] which can be updated with
doi after assigned. If preferable, we could alternatively link to a version on 
arXiv.**

A variety of other useful references are included later in this document. 

## Data sources

There are two primary sources for the data in this bundle.

### Lamont-NSSDC data

First, data sent by Johnson Space Center to Lamont-Doherty Observatory of
Columbia University, processed and analyzed under the direction of instrument PI
Marcus Langseth, and subsequently sent to the National Space Science Data Center
(NSSDC) for archival. These data were only available as binary data in a custom
filesystem on magnetic tape until 2005, when an effort led by H. Kent Hills
converted them to fixed-width ASCII tables. These tables are archived in the PDS
[^6] [^7] and copied in this bundle, with PDS4 labels, in the
``document_source`` collection. We refer to these data as the 'Lamont data' or
'Lamont-NSSDC data.' More detail about the structure and format of these data
can be found in [^8], [^9], and [^10], copied in this collection in
/lamont-nssdc. These data cover the period from 1971-1974. Lamont does not
appear to have processed any data after the end of 1974; none are mentioned in
Langseth's subsequent publications. They certainly ceased archival at the end of
1974.

### Nagihara data

Our second primary source is data not archived by the original instrument team.

Researchers involved in ALSEP data recovery have found two additional sources
for this data: "ARCSAV tapes" produced by Johnson Space Center from February
1973 to March 1976 and "work tapes" produced by the Passive Seismic Experiment
group at the University of Texas from March 1976 to ALSEP termination (although
HFE data were not recorded between August 1976 and April 1977). Most ARCSAV
tapes have not survived; Yosio Nakamura preserved all work tapes.

Some of these data have been recovered, paired with relevant (also previously
lost) calibration data, and processed in recent efforts led by Seiichi Nagihara.
For this reason, we refer to these data collectively as the 'Nagihara data.' See
[^11] for a more complete narrative of these recovery efforts. 

Some data recovered by Nagihara et al. were released with [^11]. The portions of
these data from 1975 have subsequently been released in enhanced versions with
additional components in four PDS bundles [^12] [^13] [^14] [^15]--one raw and
one calibrated for each mission. We include data from [^13], [^15], and [^11] in
this bundle. Data from [^13] and [^15] supersede data from [^11]; in other
words, data in this bundle from 1975 is sourced from [^13] and [^15], and data
in this bundle from 1976 and 1977 is sourced from [^11]. Data descriptions from
[^13] and [^15] are included in the /nagihara subdirectory of this bundle. We
have also provided copies of all of these data sets in the ``document_source``
collection of this bundle.

## Data contents and organization

Each probe included twelve separate thermometers: eight organized into four
differential pairs, and four individual thermocouples. There was also a shared
reference thermometer (TREF) in the central HFE electronics package. For more
detail on the physical probe apparatus, including thermometer architecture and
tolerances, see [^14] and [^15]. [^16] provides a monograph-length science and
engineering narrative for the probes and [^17] provides their official
engineering description and technical specifications. All of these documents are
included in the /hfe subdirectory of this collection.

The data were intended for reduction into five separate data sections or 'files'
per probe, giving twenty total files for the entire AHFE. Each of these files
correspond to a set of probe thermometers. 

We provide an simplified schematic in the /hfe subdirectory of this collection
(probe_geometry.jpg) that displays thermometer layout and file membership, and
also list them here:

* file 1: The upper gradient bridge (TG11 for probe 1, TG21 for probe 2) file 2:
* the lower gradient bridge (TG12 for probe 1, TG22 for probe 2) file 3: TREF,
* thermocouples (far to near: TC11, TC12, TC13, and TC14 for probe 1; TC21,
* TC22, TC23, and TC24 for probe 2), and 'heater state' (HTR). file 4: the upper
* ring bridge (TR11 for probe 1, TR21 for probe 2) file 5: the lower ring bridge
* (TR21 for probe 1, TR22 for probe 2).

The differential thermometers are further named 'A' and 'B' to distinguish the
elements of each pair. A is the upper and B the lower. For instance, the upper
thermometer of the upper gradient bridge of probe 1 is named TG11A.

(Note that an alternate nomenclature exists for the thermocouples in some
(mission documentation. It names them, far to near, TC2, TC3, TC4, and TC1.)

We frequently use the following convenient abbreviated format to refer to these
files, particularly in filenames and code, taken from older versions of [^6] and
[^7]:

``a[mission number: 15 or 17]p[probe number: 1 or 2]f[file number: 1-5]``; for
instance, data from the Apollo 15 probe 1 upper gradient bridge is called
a15p1f1.

### Lamont-NSSDC format

In files 1, 2, 4, and 5 (the differential thermometer files), the instrument
team reduced data into time, average bridge temperature ``T``, and temperature
difference between the thermometers of the bridge ``dT``. They chose a sign
convention for dT such that dT was positive when the lower thermometer was
warmer than the upper thermometer.

In file 3, they reduced data into temperature values for the reference
thermometer and each thermocouple ``TREF, TC1, TC2, TC3, TC4``, along with
'heater state' ``HTR``.

They archived these numbers in IBM 1130 floating-point format: 1 sign bit, 23
bits of mantissa, and 8 bits of exponent. (This resulted in many temperature
records with spurious precision.) Hills' 2005 program converted these numbers to
base-10 exponential notation: a ``-`` if negative, seven digits after the
decimal point, an ``E,`` an exponent sign, and 2 digits of exponent, like
``-1.0000000E+00.`` The value ``-9.9990000E+03`` is used as a special constant
to denote missing records.

The instrument team recorded time using a unique scale we call 'mission epoch:'
milliseconds (without leap seconds) from midnight on December 31st of the year
preceding the first year of the mission. Time 0 is thus 1970-12-31T00:00:00.000Z
for the Apollo 15 probes and 1971-12-31-T00:00:00.000Z for the Apollo 17 probes.
Despite the fact that milliseconds are the measurement unit, mission epoch
expressed in IBM 1130 floating-point format gives at best second precision for
all time measurements contained in their archived data.

It is also important to recognize that, for unknown reasons, the instrument team
temporally downsampled their archived data. The sampling intervals for the
various 'modes' listed in mission documentation are much denser than those
actually contained in the Lamont data.

### Nagihara JGR format

In [^11], Nagihara et al. give data from Apollo 15 TG11, TG12, and TG22; and
from Apollo 17 TG11 and TG21. They give explicit temperature values for
thermometers A and B of each bridge to millikelvin precision. They give time in
DOY UTC. They do not downsample the data, so unlike the Lamont data, this time
series is given to millisecond precision and at a sampling density generally
reflective of the density listed in mission documentation.

### Nagihara PDS format

The calibrated PDS data from Nagihara et al. give data from all Apollo 15
gradient bridges, as well as Apollo 17 TG11 and TG21. They give time in DOY UTC
to millisecond precision. They give temperature and dT for each bridge to
millikelvin precision. They give two separate dT fields: ``dTH,`` for the
bridge's high-sensitivity measurement, and ``dTL,`` for the bridge's
low-sensitivity measurement (see mission documentation for more details on these
separate sensitivities). They use an opposite dT sign convention from the
Lamont-NSSDC data: their dT values is positive if the upper thermometer is
warmer. 

They also calculate explicit temperature values for each thermometer, using the
most appropriate dT value, which is generally dTH unless it is saturated. dTL
saturates / soft-clips at +30/-20 K, while dTH saturates / soft-clips at +3/-2 K
(using their sign convention). 
 
## Data Sets

We provide three different data sets, formatted  for varying use cases.

### ``Clean``

This set follows the basic table and number format of [^6] and [^7] for maximum
compatibility with existing AHFE workflows. It provides time, T, and dT for
files 1, 2, 4, and 5; and time, reference thermometer temperature, thermocouple
temperatures, and heater state for file 3. It also adds one or two additional
columns per file: ``flags`` and sometimes also ``dT_corr.`` ``flags`` is a
binary bitmask marking special features of some data points, such as the
presence of a missing data constant or an artifact. See section 'Bitmask Values'
below for an index to this bitmask and a brief discussion of how to use it, and
section 'Errors and Artifacts' for an explanation of some of the features it
flags. ``dT_corr`` contains dT values after correction for numerical errors that
appear in some of the Lamont data: see 'Bitflips' and 'Saturated Bridges and
Sensitivity Selection' below.

It ingests [^11], [^13], and [^15] and converts them to this table and number
format, organizing them by file but keeping 1975, 1976, and 1977 data separate
from one another and from the Lamont data. It also converts time units in these
files from DOY UTC to mission epoch. It deviates from the number format of [^6]
and [^7] by adding several additional digits to the ``Time`` field in order to
retain the millisecond precision of the Nagihara sets. It generates only one dT
column from the Nagihara PDS sets: at each point, it selects the dT measurement
that the Nagihara team used to calculate per-thermometer temperature values from
average temperature. It converts data from [^11] to T and dT by, respectively,
averaging and computing the difference of the explicitly-given thermometer
temperatures.

### ``Split``

This set presents the data in a more user-friendly fashion, with the following
features:

* retains the distinction between files 1, 2, 3, 4, and 5, but concatenates data
	from [^6], [^7], [^11], [^13], and [^15]. For instance, a17p1f1 contains 
	data from 1972-1977. 
* presents time as YMD UTC rather than mission epoch. 
* substitutes the ``dT_corr`` field for ``dT.``  
* discards most flagged points from ``clean,`` pruning impulsive outliers and 
	missing data to reduce data cleaning time  
* discards the mangled ``HTR`` field from file 3. 
* gives explicit temperature values at each differential thermometer rather than
	 T and dT (it takes explicit temperatures from [^11], [^13], and [^15] and 
	 computes them from [^6] and [^7]).

Note that both ``split`` and ``depth,`` taken along with the reduction code
copied for user convenience in the ``document_source`` collection of this
bundle, may be viewed as *templates* for the assembly of various versions of the
AHFE data. For instance, users who wish to retain impulsive outliers might wish
to examine the ``forbidden_flags`` variable in hfe_utils.py.

### ``Depth``

This set is basically ``split`` further reduced for ease of use in some
workflows, with the following features:

* file and probe distinction is discarded: temperature, time, and depth are
	given in one table per mission 
* this set *only* includes depth values for sensors below the surface and 
	discards values for TC4 to avoid ambiguity with topmost gradient thermometer
* see 'Thermometer Positions' below for a table of the thermometer depth values
	we use in this set

## Errors and Artifacts

Here is a partial list of major known errors and artifacts in the data, along
with ways in which we have addressed some of them.

### 'Bitflip' error

All negative dT values in the Lamont data--values in which the upper thermometer
of a bridge is warmer than the lower--are subject to a numerical error. This
affects many files, but is especially significant in files subject to a great
deal of diurnal variation, such as a15p1f1. Hills and Williams coined the term
'bitflip' to describe this error. Its source is not known, but is likely due to
a bug in archival preparation related to conversion to exponential form at
Lamont. It is not present in the Nagihara data or in documents published by the
original instrument team.

Formally, ``bitflip(n),`` the bitflipped representation of ``n,`` can be
described as such: 

Express ``n`` as a binary exponential; ``n = -2^a * (1 + m)`` for a unique
integer ``a`` and real ``m`` with ``0 <= m < 1.`` Then ``bitflip(n) = -2^a *
(1-m).`` 

This error can be numerically reversed if the correct ``a`` is known; however,
``bitflip(n)`` is not one-to-one and is therefore potentially lossy. 

We have reversed the bitflip in all Lamont data using our best available
heuristics. However, we believe that its potential lossiness makes some of these
corrections ambiguous, particularly when ``n - bitflip(n)`` is small compared to
the time-series variation in ``n``. We have given apparently-ambiguous bitflip
reversals the value '2' in our flag bitmask. Users wishing to replicate or
extend our corrections may examine our selections of ``a`` for each negative dT
in the script 'hfe_corrections.py' included as supplementary material in the
document_source collection of this bundle.

### 'HTR'

File 3 contains a field labeled 'HTR,' described in [^10] as 'an integer
between 1 and 16 converted to real mode.' Although it is impossible to say
with certainty, this could reasonably be understood to refer to a decimal
conversion of the four 'DH-93' bits described on p. C-73 of [^20]. We suspect
it was written to disk incorrectly, as the field contains only missing data
flags and intermittent '1s' that do not obviously correspond to heater
activations, or indeed to anything else. Additionally, the description of File
3 in [^19] describes it, somewhat cryptically, as "time, blank, reference
bridge and thermocouple temperatures," suggesting the possibility that nothing
was intended to be written in this field at all and that the '1s' are an
artifact of tape-writing or -reading processes; however, this explanation
raises the serious question of why other mission personnel gave a
specification for the field. In response to this mystery, we have discarded
this field in ``split`` and ``depth.``

### Impulsive Outliers

All data sets contain a number of impulsive outliers. They result from unknown
sources but do not appear to be related to a specific implementation of the data
reduction pipeline, as they appear in both the Lamont and Nagihara data. Our
general heuristic for identifying impulsive outliers was to examine points that
exhibited dT / time or T / time variation greater than about five times the
average variation of similar regions of the data set, determine whether any
clear physical explanation existed for their presence, and flag them as outliers
if no such explanation was found. We flag these with the bitmask values 0b100
(for T) and 0b1000 (for dT) in ``clean`` and discard them in ``split`` and
 ``depth.``

### Thermal Noise and Spurious Diurnal Variation in Thermocouples

The Apollo 17 thermocouples are subject to a great deal of thermal noise. We do
not attempt to correct it, but urge caution with these data, especially during
lunar day. Subsurface thermocouples are also subject to some spurious diurnal
variation, likely due to thermally-induced EMF production in thermocouples.

### Saturated Bridges and Sensitivity Selection

Gradient bridges were capable of two separate dT measurements:
'high-sensitivity,' which saturated or soft-clipped at +2/-3 K, and
'low-sensitivity,' which saturated or soft-clipped at +20/-30 K. Ring bridges
were only capable of one dT measurement, which saturated or soft-clipped at
+2/-3 K. Two bridges are frequently saturated: The Apollo 15 probe 2 upper
gradient and ring bridges. dT values from these bridges, and thermometer
temperatures derived from them, should not be taken as representative of actual
temperature. Some other bridges may have temporarily saturated during heater
activation or initial emplacement, though this is only obviously the case for
the Apollo 17 probe 1 lower ring bridge during a partial high-mode heater
activation attempt.

The Lamont data include only one dT field for the gradient bridges. We believe
this is generally high-sensitivity except for points at which the
high-sensitivity measurement would saturate; these occur most frequently in
a15p1f1 and a15p2f1. There is one notable exception to this: many positive
values in the first seven lunations of a15p2f1 appear to incorrectly use the
high-sensitivity measurement, perhaps due to a bug in a software routine
intended to select the correct dT sensitivity during archival. We crudely
correct these points by scaling them by a factor of 10. Please note that this
merely makes the dT values from this bridge *consistently* saturated, not
accurately representative of physical temperatures.

## Thermometer Positions

See our simplified schematic in this collection (/hfe/probe_geometry.jpg) for
positions of these thermometers relative to the probe body. Positions relative
to the lunar surface varied by probe. The Apollo 15 probes were buried much more
shallowly than the desired depth due to deficiencies in the drilling apparatus;
the drill was improved for Apollo 17. The Apollo 17 probe positions vary only
slightly from one another. We give their depths relative to the lunar surface
below for reference; we also use subsurface positions to generate our 'depth'
set. All values are given in centimeters. (Note that depth values differ by a
centimeter between different mission documents, and different values are
sometimes even given within a single publication. We use values from the table
on p. 102 of [^18] to resolve ambiguities.)

### Apollo 15 probe 1 

* TC11: on surface  
* TC12: on surface 
* TC13: above surface 
* TC14: 35 
* TG11A: 35
* TR11A: 45 
* TR11B: 73 
* TG11B: 84 
* TG12A: 91 
* TR12A: 101 
* TR12B: 129 
* TG12B: 139

### Apollo 15 probe 2

* TC11: on surface  
* TC12: on surface 
* TC13: on surface 
* TC14: above surface 
* TG11A: -6 (above surface) 
* TR11A: 3 
* TR11B: 32 
* TG11B: 41 
* TG12A: 49 
* TR12A: 59 
* TR12B: 87
* TG12B: 97

### Apollo 17 probe 1

* TC11: on surface  
* TC12: 14 
* TC13: 66 
* TC14: 130 
* TG11A: 130 
* TR11A: 140 
* TR11B: 167
* TG11B: 177 
* TG12A: 185 
* TR12A: 195 
* TR12B: 223 
* TG12B: 233
 
### Apollo 17 probe 2

* TC11: on surface  
* TC12: 15 
* TC13: 67 
* TC14: 131 
* TG11A: 131 (above surface)
* TR11A: 141 
* TR11B: 168 
* TG11B: 178 
* TG12A: 186 
* TR12A: 196 
* TR12B: 224 
* TG12B: 234

## Bitmask 

The 'flags' field contains a binary bitmask expressed in decimal form. A
binary bitmask provides a simple numerical way to mark points in a data set.
The indices of any named features at a given data point are simply added
together to produce the value of the 'flags' field at that point. For
instance, a point that contained both an outlier in T and an outlier in dT
would be given the flags value 0b100 + 0b1000 = 0b1100: in standard decimal,
12, and in the exponential notation of the 'clean' set, 1.2000000E+01.

Users may subject bitmask values to elementary binary operations in order to 
search for features within a data file. For instance, if a user were
interested in removing any points flagged either as T/dT outliers or ambiguous
bitflip corrections from a data file, they might write a routine that followed
this pseudocode description: 
```
Let the variable 'bad_flags' be equal to the sum of (0b10, 0b100, 0b1000).

Loop over the rows of the data file.

At each row, perform a bitwise AND operation between 'bad_flags' 
and the current row's 'flags' field.   

If the result of this AND operation is nonzero, delete the current row. 

```
### Complete Index to Bitmask Values

* 0b1: missing data 

*only used in files 1,2,4,5:*

* 0b10: ambiguous bitflip correction 
* 0b100: outlier in dT 
* 0b1000: outlier in T

*only used in file 3:*

* 0b10000: outlier in HTR (placeholder; not used due to mangled HTR values)
* 0b100000: outlier in TREF 
* 0b1000000: outlier in TC1 
* 0b10000000: outlier in TC2
* 0b100000000: outlier in TC3 
* 0b1000000000: outlier in TC4 
* 0b10000000000: time discrepancy

*only used in a15p2f1:*

* 0b100000000000: cycle change spikes 
* 0b1000000000000: presumed sensitivity error
* 0b10000000000000: bit-flipped eclipse events

## Citations

[^1]: "Overview of the Apollo 15 Lunar Surface Experiments Package (ALSEP)."
David R. Williams, 2017. NASA: Planetary Data System. LID
urn:nasa:pds:apollodoc:a15doc:a15a_alsep_overview. Included in this collection
as /hfe/a15a_alsep.txt.

[^2]: "Overview of the Apollo 17 Lunar Surface Experiments Package (ALSEP)."
David R. Williams, 2017. NASA: Planetary Data System. LID
urn:nasa:pds:apollodoc:a17doc:a17a_alsep_overview. Included in this collection
as /hfe/a17a_alsep.txt.

[^3]: "Overview of the Apollo 15 Heat Flow Experiment (HFE)." David R. Williams,
2017. NASA: Planetary Data System. LID
urn:nasa:pds:apollodoc:a15doc:a15a_hfe_overview. Included in this collection as
/hfe/a15a_hfe.txt.

[^4]: "Overview of the Apollo 17 Heat Flow Experiment (HFE)." David R. Williams,
2017. NASA: Planetary Data System. LID
urn:nasa:pds:apollodoc:a17doc:a17a_hfe_overview. Included in this collection as
/hfe/a17a_hfe.txt.

[^5]: **placeholder reference to a forthcoming P&SS publication**

[^6]: "APOLLO 15 HEAT FLOW THERMAL CONDUCTIVITY RDR SUBSAMPLED V1.0,
A15A-L-HFE-3-THERMAL-CONDUCTIVITY-V1.0." Langseth, M. G. S., Jr., S. J. Keihm,
J. L. Chute, Jr., H. K. Hills, and D. R. Williams. NASA: Planetary Data System,
2014. Data portions included in this bundle in /document_source/a15.

[^7]:  "APOLLO 17 HEAT FLOW THERMAL CONDUCTIVITY RDR SUBSAMPLED V1.0,
A17A-L-HFE-3-THERMAL-CONDUCTIVITY-V1.0." Langseth, M. G. S., Jr., S. J. Keihm,
J. L. Chute, Jr., H. K. Hills, and D. R. Williams. NASA: Planetary Data System,
2014. Data portions included in this bundle in /document_source/a17.

[^8]: PDS3 catalog file from "APOLLO 15 HEAT FLOW THERMAL CONDUCTIVITY RDR
SUBSAMPLED V1.0, A15A-L-HFE-3-THERMAL-CONDUCTIVITY-V1.0." D.R. Williams and
K.H. Hills (ed. S.A. Mclaughlin). NASA: Planetary Data System, 2014. Included
in this collection as /hfe/a15_dataset.cat.

[^9]: PDS3 catalog file from "APOLLO 17 HEAT FLOW THERMAL CONDUCTIVITY RDR
SUBSAMPLED V1.0, A17A-L-HFE-3-THERMAL-CONDUCTIVITY-V1.0." D.R. Williams and
K.H. Hills (ed. S.A. Mclaughlin). NASA: Planetary Data System, 2014. Included
in this collection as /hfe/a17_dataset.cat.

[^10]: "Description of Apollo Heat Flow Experiment Data Tapes." Lamont-Doherty
Observatory of Columbia University, 1973. 

[^11]: "Examination of the Long-Term Subsurface Warming Observed at the Apollo
15 and 17 Sites Utilizing the Newly Restored Heat Flow Experiment Data From
1975 to 1977." S. Nagihara, W.S. Kiefer, P.T. Taylor, and Y. Nakamura. JGR
Planets, April 2018. doi:10.1029/2018JE005579.

[^12]: "Apollo 15 ALSEP ARCSAV Heat Flow Experiment Raw Cleaned ASCII Data
Bundle." Y. Nakamura and S. Nagihara (eds. D.R. Williams and S.A. Mclaughlin).
NASA: Planetary Data System, 2018. urn:nasa:pds:a15hfe_raw_arcsav

[^13]: "Apollo 15 ALSEP ARCSAV Heat Flow Experiment Calibrated Gradient Bridge
Temperatures Bundle." Y. Nakamura and S. Nagihara (eds. D.R. Williams and S.A.
Mclaughlin). NASA: Planetary Data System, 2018.
urn:nasa:pds:a15hfe_calibrated_arcsav. Data collection included in this bundle
in /document_source collection.

[^14]: "Apollo 17 ALSEP ARCSAV Heat Flow Experiment Raw Cleaned ASCII Data
Bundle." Y. Nakamura and S. Nagihara (eds. D.R. Williams and S.A. Mclaughlin).
NASA: Planetary Data System, 2018. urn:nasa:pds:a17hfe_raw_arcsav

[^15]: "Apollo 17 ALSEP ARCSAV Heat Flow Experiment Calibrated Gradient Bridge
Temperatures Bundle." Y. Nakamura and S. Nagihara (eds. D.R. Williams and S.A.
Mclaughlin). NASA: Planetary Data System, 2018.
urn:nasa:pds:a17hfe_calibrated_arcsav. Data collection included in this bundle
in /document_source collection.

[^16]: "Heat Flow Experiment." In *Apollo 15 Preliminary Science Report,* ch.
11. Marcus Langseth et al. NASA: 1972. Included in this collection as
/hfe/a15_psr_ch11_hfe.pdf.

[^17]: "Heat Flow Experiment." In *Apollo 17 Preliminary Science Report*, ch. 9.
Marcus Langseth et al. NASA: 1973. Included in this collection as
/hfe/a15_psr_ch11_hfe.pdf.

[^18]: *Lunar Heat-Flow Experiment: Final Technical Report.* Marcus Langseth.
Lamont-Doherty Observatory of Columbia University, September 1977. Included in
this collection as /hfe/final_technical_report.pdf.

[^19]: *Apollo Scientific Experiments Data Handbook,* Section 10 (1976
revision). W.W. Lauderdale and W.F. Eichelman. NASA: Lyndon B. Johnson Space
Center, August 1976. Included in this collection as
/hfe/ase_data_handbook_10.pdf.

[^20]: *Apollo Lunar Surface Experiment Package Archive Tape Description
Document.* Lockheed Electronics Company. NASA: Lyndon B. Johnson Space Center,
May 1975.
