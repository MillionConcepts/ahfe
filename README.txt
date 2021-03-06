# Apollo 15 and 17 Heat Flow Experiment Concatenated Data Sets Bundle

This bundle contains ASCII tables containing corrected, reduced, and
concatenated versions of all available calibrated data from the Apollo 15 and
17 Heat Flow Experiments, along with supporting documentation and source data.
These tables are based on other data in the PDS and the published literature
(see "sources" below): (1) transcriptions of data sent by the original
instrument team to the NSSDC and (2) data not archived by the instrument team
and recovered much more recently.

The data in this bundle correct several errors in (1), and furthermore place
(1) and (2) into a standardized format for ease of use.

Primary documentation is in this bundle's document collection as
"bundle_documentation.md."

## contents

Reduction code and source data can be found in the /document_source
collection.

Background documents and bundle documentation are in the /document collection.

Processed data is in the /data collection.

The reduction code for this data is stored in a NASA-Planetary-Science
repository on Github: https://github.com/NASA-Planetary-Science/ahfe_scripts.
We have copied it in this bundle for the convenience of users who might wish
to verify, correct errors in, or extend the functionality of these data sets.
Running hfe_cleaner.py in /document_source should generate a tree named
/document_source/data_local that contains identical versions of all data in
the /data collection. Dependencies beyond the Python 3 standard library are
astropy, pandas, and numpy. The Anaconda distribution is recommended.

## sources

Data in the 'document_source' folder is taken from the following sources. More
granular sourcing information can be found in individual labels.

M. G. S. Langseth, S. J. Keihm, J. L. Chute, H. K. Hills, and D. R. Williams.
APOLLO 15 HEAT FLOW THERMAL CONDUCTIVITY RDR SUBSAMPLED V1.0,
15A-L-HFE-3-THERMAL-CONDUCTIVITY-V1.0, 2014. NSSDC ID PSPG-00093, NSSDC ID of
older tapes 71-063C-06A.

M. G. S. Langseth, S. J. Keihm, J. L. Chute, H. K. Hills, and D. R. Williams. 
APOLLO 17 HEAT FLOW THERMAL CONDUCTIVITY RDR SUBSAMPLED V1.0,
A17A-L-HFE-3-THERMAL-CONDUCTIVITY-V1.0, 2014b. NSSDC ID PSPG-00022, NSSDC ID
of older tapes 72-096C-01A.

S. Nagihara and Y. Nakamura. Apollo 17 ALSEP ARCSAV Heat Flow Experiment
Calibrated Gradient Bridge Temperatures Collection (1975-092 to 1975-181),
2019. URL
http://pds-geosciences.wustl.edu/lunar/urn-nasa-pds-a17hfe_calibrated_arcsav/data/collection.xml.

S. Nagihara and Y. Nakamura. Apollo 15 ALSEP ARCSAV Heat Flow Experiment
Calibrated Gradient Bridge Temperatures Collection (1975-092 to 1975-181),
2019. URL
http://pds-geosciences.wustl.edu/lunar/urn-nasa-pds-a15hfe_calibrated_arcsav/data/collection.xml.

Ancillary material released along with: S. Nagihara, W.S. Kiefer, P.T. Taylor,
and Y. Nakamura. Examination of the long-term subsurface warming observed at
the Apollo 15 and 17 sites utilizing the newly restored Heat Flow Experiment
data from 1975 to 1977. J Geophysical Research: Planets, April 2018. doi:
10.1029/2018JE005579.