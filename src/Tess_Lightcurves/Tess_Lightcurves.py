import logging,warnings
import lightkurve as lk
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from astroquery.mast import Catalogs
from version import __version__

def set_css():
    st.markdown("""
        <style>
            .js-plotly-plot .plotly, .js-plotly-plot .plotly div {
                margin-bottom: -25px;
            }
            .spc{
                font-size: 13px;
                padding-bottom: 0.2rem;
            }
            .stFormSubmitButton button{
                float:right;
                color: navy;
            }
            div[data-testid="stExpander"] details summary p{
                font-size: 1.1rem;
            }
            div[data-testid="stExpander"] summary{
                padding: 0.15rem 0.5rem;
            }
            div[data-testid="stSidebar"]{
                width: 320px !important;
            }
            div[data-testid="stSidebarUserContent"] h1{
                font-size: 2.7rem;
                text-align: center;
            }
            .credits, a, a:visited {
                font-size: 0.8rem;
                text-align: center;
            }
            a, a:visited {
                color: navy;
                font-weight:bold;
            }

            div[data-testid="stMainBlockContainer"] {
                max-width: 90rem;
                padding: 1.75rem 2.5rem 0 2.5rem;
            }
            div[data-testid="stMarkdownContainer"] p{
                font-size: 1.1rem;
            }
            div[data-testid="stVerticalBlock"]{
                gap: 0rem;
            }
            h1{
                padding-bottom: 0.3rem;
            }
        </style>
        """, unsafe_allow_html=True)


if __name__ == '__main__':
    st.set_page_config(page_title="Tess Lightcurves app", layout="wide")
    set_css()
    try:
        xticid = st.query_params.tic #  ?tic=165795955
    except:
        xticid = ''

    ticid = 0
    with st.sidebar:
        st.title('**TESS Lightcurves**')
        st.html('&nbsp;')
        with st.form("my_form"):
            tic = st.text_input('**TIC number:**', value=xticid, placeholder='', max_chars=10)
            if tic != '':
                try:
                    ticid = int(tic)
                except ValueError:
                    ticid=0
            st.html('&nbsp;')
            tipo = st.selectbox(
                '**Flux type** (spoc/tess-spoc):',
                ('PDCSAP flux', 'SAP flux')
            )
            st.html('<div class="credits">&nbsp;</div>')
            st.form_submit_button('**PLOT**')
        #st.html('&nbsp;')
        st.html('<div align="right">v'+__version__+'</div>')
        st.markdown('<div class="credits">Github source code: <a href="https://github.com/exo-pt/Tess-Lightcurves-app">Tess Lightcurves</a><br>Using <a href="https://github.com/lightkurve/lightkurve">Lightkurve</a>' +\
                ' and <a href="https://github.com/plotly/plotly.py">Plotly</a> Python packages.</div>', unsafe_allow_html=True)

    if ticid != 0:
        TICstr = 'TIC '+ str(ticid)
        st.title(TICstr)
        st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
        cat=[]
        res=''
        try:
            cat = Catalogs.query_object(TICstr, radius=0.0003, catalog="TIC")
        except:
            try:
                cat = Catalogs.query_object(TICstr, radius=0.0003, catalog="TIC")
            except:
                st.error('Could not resolve '+ TICstr)
                st.stop()

        cat['rad'] = cat['rad'].round(3)
        cat['ra'] = cat['ra'].round(5)
        cat['dec'] = cat['dec'].round(5)
        cat['Tmag'] = cat['Tmag'].round(2)
        cat['d'] = cat['d'].round(2)
        cat['logg'] = cat['logg'].round(3)
        rho = round(cat['rho'][0]*1.41, 3)

        linha = '&nbsp;<b>RA</b>: ' + str(cat['ra'][0]) + '  .  <b>Dec</b>:' + str(cat['dec'][0]) + '  .  <b>Tmag</b>: ' + str(cat['Tmag'][0]) +'  .  <b>Rad</b>: ' + str(cat['rad'][0]) +  \
            '  .  <b>Mass</b>: ' + str(cat['mass'][0]) + '  .  <b>Teff</b>: ' + str(cat['Teff'][0]) + '  .  <b>Logg</b>: '+ str(cat['logg'][0]) + '  .  <b>MH</b>: '+ str(cat['MH'][0])+'  .  <b>rho</b>: ' + \
            str(round(rho,5)) +  '  .  <b>Dist</b>(pc): ' +str(cat['d'][0])+'<br/>'
        linha = linha.replace('nan', '?')
        linha = linha.replace(' . ', '&nbsp;&nbsp;&nbsp;')
        st.html('<div class="spc">' + linha +'</div>')
        try:
            res=lk.search_lightcurve(TICstr, mission='TESS')
        except:
            res = ''
        if len(res) == 0:
            if res=='':
                st.error('Error in lk.search_lightcurve... Try again.')
            else:
                st.error('No available lightcurve data at MAST from SPOC, TESS_SPOC, QLP or ELEANOR.')
            st.stop()

        df = res.table.to_pandas()
        authors = ['SPOC', 'TESS-SPOC', 'QLP', 'GSFC-ELEANOR-LITE']
        sectors = df[df['provenance_name'].isin(authors)]['sequence_number'].drop_duplicates().sort_values().to_list()
        sec_spoc = df[df['provenance_name'] == 'TESS-SPOC']['sequence_number'].drop_duplicates().sort_values().to_list()
        sec_2min = df[df['provenance_name'] == 'SPOC']['sequence_number'].drop_duplicates().sort_values().to_list()
        sec_qlp = df[df['provenance_name'] == 'QLP']['sequence_number'].drop_duplicates().sort_values().to_list()
        sec_eleanor = df[df['provenance_name'] == 'GSFC-ELEANOR-LITE']['sequence_number'].drop_duplicates().sort_values().to_list()

        txt = '**Available Sectors: ' + str(sectors) + '**'
        with st.expander(txt):
            table = '<table><tr><td>SPOC: </td><td>'+ str(sec_2min) + '</td></tr>' +\
                '<tr><td>TESS-SPOC: </td><td>'+ str(sec_spoc) + '</td></tr>' +\
                '<tr><td>QLP: </td><td>'+ str(sec_qlp) + '</td></tr>' +\
                '<tr><td>ELEANOR: </td><td>'+ str(sec_eleanor) + '</td></tr></table>'
            #txt = 'SPOC: <b>' + str(sec_2min) + '</b><br>TESS-SPOC: <b>' + str(sec_spoc) + '</b>'
            #txt = txt + '<br>QLP: <b>' + str(sec_qlp) + '</b><br>ELEANOR: <b>' + str(sec_eleanor)
            st.html(table)
        st.html('&nbsp;')
        warnings.simplefilter("ignore")
        logging.getLogger("lightkurve").setLevel(logging.ERROR)
        sectors.reverse()
        tot = 0

        for sec in sectors:
            tot += 1
            try:
                if sec in sec_2min:
                    tit = 'Sector ' + str(sec) + ' (SPOC)'
                    if tipo == 'SAP flux':
                        lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='SPOC', exptime='120').download(flux_column='sap_flux').remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
                    else:
                        lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='SPOC', exptime='120').download().remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
                elif sec in sec_spoc:
                    tit = 'Sector ' + str(sec) + ' (TESS-SPOC)'
                    if tipo == 'SAP flux':
                        lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='TESS-SPOC').download(flux_column='sap_flux').remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
                    else:
                        lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='TESS-SPOC').download().remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
                elif sec in sec_qlp:
                    tit = 'Sector ' + str(sec) + ' (QLP)'
                    lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='QLP').download(quality_bitmask=1073749231).remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
                elif sec in sec_eleanor:
                    tit = 'Sector ' + str(sec) + ' (ELEANOR)'
                    lc0 = lk.search_lightcurve(TICstr, sector=sec, mission='TESS', author='GSFC-ELEANOR-LITE').download().remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
                else:
                    continue
            except:
                st.write(':red[Error] reading '+ tit + '(try again...)')
                continue

            df = lc0.to_pandas().reset_index()
            df = df[['time', 'flux']]
            fig = px.scatter(df, x='time', y='flux', color_discrete_sequence=['darkslategrey'])
            fig.update_traces(marker={'size': 3.3})
            minx = min(df['time']) - 0.7
            maxx = max(df['time']) + 0.7
            fig.update_xaxes(range=[minx-0.05, maxx+0.05])
            fig.add_vrect(x0=minx, x1=maxx, line_width=0.5)
            fig.update_layout(title=dict(text=tit, y=0.9, font=dict(size=17, color='grey')))
            fig.update_layout(yaxis = dict(tickfont = dict(size=13), tickformat = '.4f'), xaxis = dict(tickfont = dict(size=13)))
            fig.update_layout(yaxis_title=None, xaxis_title=None)
            fig.update_xaxes(showgrid=True, gridcolor='#ddd',title_standoff = 1, minor=dict(ticklen=4, tickcolor="grey", nticks=5))
            fig.update_yaxes(showgrid=True, gridcolor='#ddd')
            fig.update_layout(height=285)
            st.plotly_chart(fig, use_container_width=False)
