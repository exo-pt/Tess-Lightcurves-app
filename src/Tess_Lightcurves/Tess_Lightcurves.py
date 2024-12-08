import logging,warnings
import lightkurve as lk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from version import __version__

if __name__ == '__main__':
    try:
        xticid = st.query_params.tic #  ?tic=165795955
    except:
        xticid = ''
    st. set_page_config(layout="wide")
    st.markdown("""
        <style>
           .block-container {
                padding-top: 1rem;
            }
            div[data-testid="stExpander"] details summary p{
                font-size: 1.1rem;
                color: navy;
            }
            div[data-testid="stSidebarUserContent"] h1{
                font-size: 2.5rem;
                text-align: center;
            }
            div[data-testid="stMarkdownContainer"] p{
                font-size: 1.1rem;
                color: navy;
            }
        </style>
        """, unsafe_allow_html=True)
    ticid = 0
    with st.sidebar:
        st.title('**TESS Lightcurves**')
        with st.form("my_form"):
            tic = st.text_input('**TIC number:**', value=xticid, placeholder='', max_chars=10)
            if tic != '':
                try:
                    ticid = int(tic)
                except ValueError:
                    ticid=0
            tipo = st.selectbox(
                '**Flux type:**',
                ('PDCSAP flux', 'SAP flux')
            )
            st.form_submit_button("**:blue[PLOT]**")
        st.html('<div align="right">v'+__version__+'</div>')

    if ticid != 0:
        TICstr = 'TIC '+ str(ticid)
        st.title(TICstr)
        try:
            res=lk.search_lightcurve(TICstr, mission='TESS')
        except:
            res = ''
        if len(res) == 0:
            if res=='':
                st.write('Error in lk.search_lightcurve... Try again.')
            else:
                st.write('No available lightcurves or TIC number error...')
        else:
            df = res.table.to_pandas()
            sectors = df['sequence_number'].drop_duplicates().sort_values().to_list()
            sec_spoc = df[df['provenance_name'] == 'TESS-SPOC']['sequence_number'].sort_values().to_list()
            sec_2min = df[df['exptime'] == 120]['sequence_number'].sort_values().to_list()
            sec_qlp = df[df['provenance_name'] == 'QLP']['sequence_number'].sort_values().to_list()

            txt = '**Observed Sectors: ' + str(sectors) + '**'
            with st.expander(txt):
                txt = 'SPOC: <b>' + str(sec_2min) + '</b><br>TESS-SPOC: <b>' + str(sec_spoc) + '</b>'
                txt = txt + '<br>QLP: <b>' + str(sec_qlp) + '</b>'
                st.html(txt)

            warnings.simplefilter("ignore")
            logging.getLogger("lightkurve").setLevel(logging.ERROR)

            sectors.reverse()
            for sec in sectors:
                try:
                    if sec in sec_2min:
                        if tipo == 'SAP flux':
                            lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='SPOC', exptime='120').download(flux_column='sap_flux').remove_outliers(sigma_lower=10, sigma_upper=3).normalize().remove_nans()
                        else:
                            lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='SPOC', exptime='120').download().remove_outliers(sigma_lower=10, sigma_upper=3).normalize().remove_nans()
                    else:
                        if sec in sec_spoc:
                            if tipo == 'SAP flux':
                                lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='TESS-SPOC').download(flux_column='sap_flux').remove_outliers(sigma_lower=10, sigma_upper=3).normalize().remove_nans()
                            else:
                                lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='TESS-SPOC').download().remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
                        else:
                            if sec in sec_qlp:
                                lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='QLP').download(quality_bitmask=1073749231).remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
                            else:
                                continue
                except:
                    st.write('Error reading lightcurve sector '+ sec)
                    continue

                fig = plt.figure(figsize=(15, 2.4))
                plt.margins(x=0.02) #, y=0.05)
                if sec in sec_2min:
                    plt.title('Sector ' + str(sec) + ' (SPOC)', loc='left')
                else:
                    if sec in sec_spoc:
                        plt.title('Sector ' + str(sec) + ' (TESS-SPOC)', loc='left')
                    else:
                        plt.title('Sector ' + str(sec) + ' (QLP)', loc='left')
                plt.scatter(lc0.time.value, lc0.flux.value, s=1, color='darkslategrey')
                plt.minorticks_on()
                plt.grid(color='lightgrey', linewidth=0.6)
                st.pyplot(fig)
