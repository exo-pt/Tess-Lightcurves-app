import logging,warnings, time
import lightkurve as lk
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from astroquery.mast import Catalogs
import multiprocessing as mp
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
			.splash {
				font-size: 0.85rem;
				padding: 0;
				margin: 0;
				line-height: 1rem;
			}
			.vspc{
				font-size: 13px;
				padding-bottom: 1rem;
			}
			.stFormSubmitButton button{
				float:right;
				color: navy;
			}
			div[data-testid="stExpander"] details summary p{
				font-size: 1rem;
			}
			div[data-testid="stExpander"] summary{
				padding: 0.15rem 0.5rem;
			}
			[data-testid="stSidebar"][aria-expanded="true"]{
				min-width: 300px;
				max-width: 300px;
			}
			div[data-testid="stSidebarUserContent"] h1{
				font-size: 2.7rem;
				text-align: center;
			}
			div[data-testid="stHeader"]{
				height: 3rem !important;
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
				padding: 3.2rem 2.5rem 0 2.5rem;
				padding-top: 3.2rem;
				padding-bottom: 0;
			}
			div[data-testid="stMarkdownContainer"] p{
				font-size: 1.1rem;
			}
			div[data-testid="stVerticalBlock"]{
				gap: 0rem;
			}
			div[data-testid="stMainBlockContainer"] h1{
				padding-top: 0;
				padding-bottom: 0.6rem;
				font-size: 2.5rem;
				line-height: 2.7rem;
			}
			div[data-testid="stMainBlockContainer"] h2{
				padding-top: 0;
				padding-bottom: 1.4rem;
			}
		</style>
		""", unsafe_allow_html=True)

def get_splash_text(mom_date):
	html = """
		<p class="splash">&#8226;&nbsp;&nbsp;For the selected TIC number, the lightcurve of each sector available on MAST, is displayed.</p>
		<p class="splash">&#8226;&nbsp;&nbsp;If  more than one author is available for a single sector, the displayed lightcurve, in availability order, is:<br/>
		&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; SPOC (2 min) -> TESS-SPOC -> QLP -> ELEANOR.</p>
		<p class="splash">&#8226;&nbsp;&nbsp;It's possible to choose between PDCSAP and SAP flux (in SPOC and TESS-SPOC), and interact with the plots.</p>
		<p class="splash">&#8226;&nbsp;&nbsp;Vertical red bars in the lightcurves mark the spacecraft momentum dumps. (<b>Last: {mdate}</b>)
		</p>
		<p class="splash">&nbsp;</p>
		""".format(mdate=mom_date)
	return html

def plot(df, dumps):
	fig = px.scatter(df, x='time', y='flux', color_discrete_sequence=['darkslategrey']) #, render_mode="SVG")
	fig.update_traces(marker={'size': 3.3})
	fig.update_layout(yaxis = dict(fixedrange = True))
	minx = min(df['time']) - 0.7
	maxx = max(df['time']) + 0.7
	fig.update_xaxes(range=[minx-0.05, maxx+0.05])
	fig.update_xaxes(showline=True,
		 linewidth=0.5,
		 linecolor='black',
		 mirror=True)
	miny = min(df['flux'])
	maxy = max(df['flux'])
	min2y = miny-(maxy-miny)/10
	max2y = maxy+(maxy-miny)/10
	fig.update_yaxes(range=[min2y, max2y])
	fig.update_yaxes(showline=True,
		 linewidth=0.5,
		 linecolor='black',
		 mirror=True)
	fig.update_layout(plot_bgcolor='white')
	fig.update_layout(margin=dict(l=60, r=10, t=30, b=80))

	fig.update_layout(title=dict(text=tit, x=0, y=0.98, font=dict(size=17, color='black')))
	fig.update_layout(yaxis = dict(tickfont = dict(size=13), tickformat = '.4f'), xaxis = dict(tickfont = dict(size=13)))
	fig.update_layout(yaxis_title=None, xaxis_title=None)
	fig.update_xaxes(showgrid=True, gridcolor='#ddd',title_standoff = 1, minor=dict(ticklen=4, tickcolor="grey", nticks=5))
	fig.update_yaxes(showgrid=True, gridcolor='#ddd')
	y0 = min2y
	y1 = (max2y-min2y)/3.7+min2y
	for x in dumps:
		fig.add_shape(type="line",
			x0=x, y0=y0, x1=x, y1=y1,
			line=dict(color="pink",width=2) #, dash="dashdot")
		)
	fig.update_layout(height=240)
	st.plotly_chart(fig, use_container_width=True, theme=None)

@st.cache_data(max_entries=200, show_spinner=False)
def get_catalog(TICstr):
	cat=[]
	res=''
	try:
		cat = Catalogs.query_object(TICstr, radius=0.0003, catalog="TIC")
		cat['rad'] = cat['rad'].round(3)
		cat['ra'] = cat['ra'].round(5)
		cat['dec'] = cat['dec'].round(5)
		cat['Tmag'] = cat['Tmag'].round(2)
		cat['d'] = cat['d'].round(2)
		cat['logg'] = cat['logg'].round(3)
		cat['MH'] = cat['MH'].round(2)
		rho = round(cat['rho'][0]*1.41, 3)

		linha = '&nbsp;<b>RA</b>: ' + str(cat['ra'][0]) + '  .  <b>Dec</b>:' + str(cat['dec'][0]) + '  .  <b>Tmag</b>: ' + str(cat['Tmag'][0]) +'  .  <b>Rad</b>: ' + str(cat['rad'][0]) +  \
			'  .  <b>Mass</b>: ' + str(cat['mass'][0]) + '  .  <b>Teff</b>: ' + str(cat['Teff'][0]) + '  .  <b>Logg</b>: '+ str(cat['logg'][0]) + '  .  <b>MH</b>: '+ str(cat['MH'][0])+'  .  <b>rho</b>: ' + \
			str(round(rho,5)) +  '  .  <b>Dist</b>(pc): ' +str(cat['d'][0])+'<br/>'
		del cat
		linha = linha.replace('nan', '?')
		linha = linha.replace(' . ', '&nbsp;&nbsp;&nbsp;')
	except:
		linha = 'Error getting star data.'
	return linha

def get_catalog_mp(slist, TICstr):
	linha = get_catalog(TICstr)
	slist.append(linha)

@st.cache_data(ttl='1d', show_spinner=False)
def get_search_result(TICstr):
	ph2 = st.empty()
	with ph2:
		st.html('<div class="spc"><i>Retrieving available sectors...</i></div>')
	try:
		res=lk.search_lightcurve(TICstr, mission='TESS')
	except:
		res = ''
	ph2.empty()
	return res

def get_line(TICstr):
	ph = st.empty()
	if 'tic' not in st.session_state:
		st.session_state.tic = TICstr
		with ph:
			st.html('<div class="spc">&nbsp;</i></div>')
	else:
		if st.session_state.tic != TICstr:
			with ph:
				st.html('<div class="spc">&nbsp;</i></div>')
			if 'linha' in st.session_state:
				del st.session_state['linha']
		else:
			if 'linha' in st.session_state:
				linha = st.session_state.linha
				with ph:
					st.html('<div class="spc">'+linha+'</i></div>')
			else:
				with ph:
					st.html('<div class="spc">&nbsp;</i></div>')
	return ph

@st.cache_resource(ttl='1d')
def load_mdumps():
	if 'mdumps' in st.session_state:
		mdumps = st.session_state.mdumps
	else:
		try:
			df = pd.read_csv('https://tess.mit.edu/public/files/Table_of_momentum_dumps.csv', comment='#')
			last_mdump = df.iloc[-1,0][:16]
			mdumps = df.iloc[:,1].values
			np.save('data/mom_dumps.npy', mdumps)
		except:
			mdumps = np.load('data/mom_dumps.npy')
		if len(mdumps):
			st.session_state.mdumps = mdumps
	return mdumps

def check_mp():
	if 'linha' not in st.session_state:
		if not process.is_alive():
			if len(slist):
				linha = slist[0]
				if linha[:5] != 'Error':
					st.session_state.linha = linha
				with ph:
					st.html('<div class="spc">'+linha+'</i></div>')

def exit_mp():
	if 'linha' not in st.session_state:
		if process.is_alive():
			process.join(timeout=10)
		check_mp()
		if process.is_alive():
			process.terminate()
			process.join()
			with ph:
				st.html('<div class="spc">Timeout getting star parameters.</i></div>')

if __name__ == '__main__':
	st.set_page_config(page_title="Tess Lightcurves", layout="wide")
	set_css()
	try:
		xticid = st.query_params.tic #  ?tic=165795955
	except:
		xticid = ''

	ticid = 0

	mdumps = load_mdumps()

	with st.sidebar:
		st.title('**TESS Lightcurves**', anchor=False)
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
		st.html('<div align="right">v'+__version__+'</div>')
		st.markdown('<div class="credits">Github source code: <a href="https://github.com/exo-pt/Tess-Lightcurves-app">Tess Lightcurves</a><br>Using <a href="https://github.com/lightkurve/lightkurve">Lightkurve</a>' +\
				' and <a href="https://github.com/plotly/plotly.py">Plotly</a> Python packages.</div>', unsafe_allow_html=True)

	splash = st.empty()
	if ticid < 1:
		jdate = 2457000 + mdumps[-1]
		t = pd.to_datetime(jdate, origin='julian', unit='D').strftime('%Y-%m-%d')
		html = get_splash_text(t)
		with splash.container():
			st.header('Tess Lightcurves', anchor=False)
			with st.columns([1,40,1])[1]:
				st.html(html)
			with st.columns([1,30,1])[1]:
				st.image('data/prt_scr.png')
			st.html('<hr>')
	else:
		splash.empty()
		#if ticid != 0:
		TICstr = 'TIC '+ str(ticid)
		st.title(TICstr, anchor=False)
		cat=[]
		res=''
		#
		ph = get_line(TICstr)
		if not 'linha' in st.session_state:
			slist = mp.Manager().list()
			process = mp.Process(target=get_catalog_mp, args=(slist, TICstr,))
			process.start()
		#
		res = get_search_result(TICstr)
		#
		if len(res) == 0:
			get_search_result.clear(TICstr)
			if res=='':
				st.error('Error in lk.search_lightcurve... Try again.')
			else:
				st.error('No available lightcurve data at MAST from SPOC, TESS_SPOC, QLP or ELEANOR.')
			exit_mp()
			st.stop()

		df = res.table.to_pandas()
		authors = ['SPOC', 'TESS-SPOC', 'QLP', 'GSFC-ELEANOR-LITE']
		sectors = df[(df['author'].isin(authors)) & (df['exptime'] > 100)]['sequence_number'].drop_duplicates().sort_values().to_list()
		if sectors == []:
			get_search_result.clear(TICstr)
			st.error('No available lightcurve data at MAST from SPOC, TESS_SPOC, QLP or ELEANOR.')
			exit_mp()
			st.stop()
		#
		d = {}
		secs_auth = {0:[], 1:[], 2:[], 3:[]}
		for s in sectors:
			for auth in range(4):
				idx = df.index[(df['sequence_number'] == s) & (df['author']==authors[auth]) & (df['exptime'] > 100)]
				if len(idx):
					secs_auth[auth].append(s)
					if s not in d:
						d[s] = [idx[0], auth]

		txt = '**Available Sectors: ' + str(sectors) + '**'
		with st.expander(txt):
			table = '<table><tr><td>SPOC: </td><td>'+ str(secs_auth[0]) + '</td></tr>' +\
				'<tr><td>TESS-SPOC: </td><td>'+ str(secs_auth[1]) + '</td></tr>' +\
				'<tr><td>QLP: </td><td>'+ str(secs_auth[2]) + '</td></tr>' +\
				'<tr><td>ELEANOR: </td><td>'+ str(secs_auth[3]) + '</td></tr></table>'
			st.html(table)
		maxlen = 8
		revsectors = sectors.reverse()
		groups = [sectors[x:x+maxlen] for x in range(0, len(sectors), maxlen)] #[::-1]
		oplist = []
		if len(groups) > 1:
			p = 0
			for gr in groups:
				p += 1
				oplist.append('Page '+ str(p) +' (sectors '+str(gr[::-1])[1:-1]+')')
			idx = 0
			option = st.selectbox(
				".",
				oplist, idx,
				label_visibility="collapsed",
			)
			secs = groups[oplist.index(option)]
		else:
			secs = groups[0]

		st.html('<div class="vspc">&nbsp;</div>')

		warnings.simplefilter("ignore")
		logging.getLogger("lightkurve").setLevel(logging.ERROR)
		done = False
		time.sleep(0.1)
		check_mp()

		for sec in secs:
			auth = d[sec][1]
			sauth = authors[auth]
			idx = d[sec][0]
			err = False
			try:
				tit = 'Sector ' + str(sec) + ' (' + sauth +')'
				match sauth:
					case 'SPOC' | 'TESS-SPOC':
						if tipo == 'SAP flux':
							lc0 = res[idx].download(flux_column='sap_flux').remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
						else:
							lc0 = res[idx].download().remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
					case 'QLP':
						lc0 = res[idx].download(quality_bitmask=1073749231).remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
					case _:
						lc0 = res[idx].download(quality_bitmask=1073749231).remove_outliers(sigma_lower=20, sigma_upper=3).normalize().remove_nans()
			except:
				st.write(':red[Error] reading '+ tit)
				continue

			df = lc0.to_pandas().reset_index()
			df = df[['time', 'flux']]
			ini = min(lc0.time.value)
			fim = max(lc0.time.value)
			del lc0
			x = np.where(np.logical_and(mdumps>ini, mdumps<fim))
			dumps= mdumps[x].tolist()
			plot(df, dumps)
			check_mp()

		exit_mp()
