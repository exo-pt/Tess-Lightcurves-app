# TESS Lightcurves app

Tess lightcurve viewer for all available sectors of a target in TIC catalog<br/><br/>
This is a small webapp currently hosted in Streamlit Cloud. You can access it at<br>
https://tess-lightcurves.streamlit.app

For a selected TIC number, one lightcurve is displayed for each available sector.
If  more than one author available for a sector, the displayed lightcurve, in availability order, is:
&nbsp;&nbsp; SPOC (2 min cadence) -> TESS-SPOC -> QLP.

The user can choose between PDCSAP and SAP flux 

![Image](https://github.com/exo-pt/Tess-Lightcurves-app/blob/main/Tess-Lightcurves-app.png?raw=true)

## Dependencies:
- numpy
- pandas
- matplotlib
- lightkurve
- streamlit


## Contributors
Rafael Rodrigues
