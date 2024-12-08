# TESS Lightcurves app

Tess lightcurve viewer for all available sectors of a star in the TIC catalog<br/>
This is a small webapp currently available at Streamlit Community Cloud.
For each selected TIC number, one lightcurve is displayed for each available sector.
If  more than one author available for a sector, the displayed lightcurve, in availability order is :  &nbsp;&nbsp; SPOC (2 min cadence) -> TESS-SPOC -> QLP.
The user can choose between PDCSAP and SAP flux 


## Dependencies:
- numpy
- pandas
- matplotlib
- lightkurve
- streamlit


## Contributors
Rafael Rodrigues