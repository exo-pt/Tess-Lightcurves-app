# TESS Lightcurves app

Tess lightcurve viewer for all available sectors of a target in TIC catalog<br/><br/>
This is a small webapp currently hosted in Streamlit Cloud. You can access it at<br/>
https://tess-lightcurves.streamlit.app
<br/>
or start the webapp locally in a Python env:
> streamlit run Tess_Lightcurves.py
The app will open in the default browser

For a selected TIC number, the lightcurve of each sector available on MAST, is displayed.
If  more than one author is available for a single sector, the displayed lightcurve, in availability order, is:
&nbsp;&nbsp; SPOC (2 min) -> TESS-SPOC -> QLP -> ELEANOR.

The user can choose between PDCSAP and SAP flux (for SPOC and TESS-SPOC), and can interact with the plots (thx to [Plotly](https://github.com/plotly/plotly.py) python library)

![Image](https://github.com/exo-pt/Tess-Lightcurves-app/blob/main/Tess-Lightcurves-app.png?raw=true)

## Dependencies:
- numpy
- pandas
- lightkurve
- astroquery
- plotly
- streamlit
