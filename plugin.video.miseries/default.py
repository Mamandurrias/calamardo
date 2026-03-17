import sys
import urllib.parse
import urllib.request
import json
import xbmcgui
import xbmcplugin
import xbmcaddon

ADDON = xbmcaddon.Addon()
BASE_URL = "http://89.167.81.214:8080"
HANDLE = int(sys.argv[1])

def get_series():
    url = f"{BASE_URL}/api/series"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read().decode())

def menu_principal():
    db = get_series()
    tiene_colecciones = any(data.get('coleccion') for data in db.values())

    item = xbmcgui.ListItem("🎭 Géneros")
    item.setInfo('video', {'title': 'Géneros', 'mediatype': 'tvshow'})
    xbmcplugin.addDirectoryItem(HANDLE, f"{sys.argv[0]}?action=generos", item, True)

    if tiene_colecciones:
        item = xbmcgui.ListItem("📦 Colecciones")
        item.setInfo('video', {'title': 'Colecciones', 'mediatype': 'tvshow'})
        xbmcplugin.addDirectoryItem(HANDLE, f"{sys.argv[0]}?action=colecciones", item, True)

    xbmcplugin.setContent(HANDLE, 'tvshows')
    xbmcplugin.endOfDirectory(HANDLE)

def listar_generos():
    db = get_series()
    generos = {}
    for nombre, data in db.items():
        gs = data.get('generos', [])
        genero = gs[0] if gs else 'Sin género'
        if genero not in generos:
            generos[genero] = []
        generos[genero].append(nombre)
    for genero in sorted(generos.keys()):
        item = xbmcgui.ListItem(genero)
        item.setInfo('video', {'title': genero, 'mediatype': 'tvshow'})
        url = f"{sys.argv[0]}?action=series_por_genero&genero={urllib.parse.quote(genero)}"
        xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
    xbmcplugin.setContent(HANDLE, 'tvshows')
    xbmcplugin.endOfDirectory(HANDLE)

def listar_colecciones():
    db = get_series()
    colecciones = {}
    for nombre, data in db.items():
        col = data.get('coleccion')
        if col:
            if col not in colecciones:
                colecciones[col] = []
            colecciones[col].append(nombre)
    for col in sorted(colecciones.keys()):
        item = xbmcgui.ListItem(col)
        item.setInfo('video', {'title': col, 'mediatype': 'tvshow'})
        url = f"{sys.argv[0]}?action=series_por_coleccion&coleccion={urllib.parse.quote(col)}"
        xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
    xbmcplugin.setContent(HANDLE, 'tvshows')
    xbmcplugin.endOfDirectory(HANDLE)

def listar_series_por_genero(genero):
    db = get_series()
    for nombre, data in sorted(db.items()):
        # Si tiene coleccion, no aparece en generos
        if data.get('coleccion'):
            continue
        gs = data.get('generos', [])
        genero_serie = gs[0] if gs else 'Sin género'
        if genero_serie != genero:
            continue
        poster = data.get('poster', '')
        art = {'poster': poster, 'thumb': poster, 'fanart': poster, 'icon': poster}
        item = xbmcgui.ListItem(nombre)
        item.setArt(art)
        item.setInfo('video', {'title': nombre, 'mediatype': 'tvshow'})
        url = f"{sys.argv[0]}?action=temporadas&serie={urllib.parse.quote(nombre)}"
        xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
    xbmcplugin.setContent(HANDLE, 'tvshows')
    xbmcplugin.endOfDirectory(HANDLE)

def listar_series_por_coleccion(coleccion):
    db = get_series()
    for nombre, data in sorted(db.items()):
        if data.get('coleccion') != coleccion:
            continue
        poster = data.get('poster', '')
        art = {'poster': poster, 'thumb': poster, 'fanart': poster, 'icon': poster}
        item = xbmcgui.ListItem(nombre)
        item.setArt(art)
        item.setInfo('video', {'title': nombre, 'mediatype': 'tvshow'})
        url = f"{sys.argv[0]}?action=temporadas&serie={urllib.parse.quote(nombre)}"
        xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
    xbmcplugin.setContent(HANDLE, 'tvshows')
    xbmcplugin.endOfDirectory(HANDLE)

def listar_temporadas(serie):
    db = get_series()
    data = db[serie]
    temporadas = sorted(set(ep['temporada'] for ep in data['episodios']))
    poster = data.get('poster', '')
    for t in temporadas:
        nombre = f"Temporada {int(t)}"
        art = {'poster': poster, 'thumb': poster, 'icon': poster}
        item = xbmcgui.ListItem(nombre)
        item.setArt(art)
        item.setInfo('video', {'title': nombre, 'mediatype': 'season', 'season': int(t)})
        url = f"{sys.argv[0]}?action=episodios&serie={urllib.parse.quote(serie)}&temporada={t}"
        xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
    xbmcplugin.setContent(HANDLE, 'seasons')
    xbmcplugin.endOfDirectory(HANDLE)

def listar_episodios(serie, temporada):
    db = get_series()
    data = db[serie]
    episodios = sorted(
        [ep for ep in data['episodios'] if ep['temporada'] == temporada],
        key=lambda x: x['episodio']
    )
    import base64
    for ep in episodios:
        titulo = ep['titulo']
        poster = ep.get('poster', data.get('poster', ''))
        url = ep['url']
        if '.m3u8' in url:
            stream_url = url
        else:
            encoded = base64.b64encode(url.encode()).decode()
            stream_url = f"{BASE_URL}/play/{encoded}"
        art = {'poster': poster, 'thumb': poster, 'icon': poster}
        item = xbmcgui.ListItem(titulo)
        item.setArt(art)
        item.setInfo('video', {
            'title': titulo,
            'mediatype': 'episode',
            'season': int(temporada),
            'episode': int(ep['episodio']),
            'plot': ep.get('sinopsis', '')
        })
        item.setProperty('IsPlayable', 'true')
        url = f"{sys.argv[0]}?action=play&url={urllib.parse.quote(stream_url)}"
        xbmcplugin.addDirectoryItem(HANDLE, url, item, False)
    xbmcplugin.setContent(HANDLE, 'episodes')
    xbmcplugin.endOfDirectory(HANDLE)

def play(url):
    item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(HANDLE, True, item)

params = dict(urllib.parse.parse_qsl(sys.argv[2].lstrip('?')))
action = params.get('action', '')

if action == '':
    menu_principal()
elif action == 'generos':
    listar_generos()
elif action == 'colecciones':
    listar_colecciones()
elif action == 'series_por_genero':
    listar_series_por_genero(urllib.parse.unquote(params['genero']))
elif action == 'series_por_coleccion':
    listar_series_por_coleccion(urllib.parse.unquote(params['coleccion']))
elif action == 'temporadas':
    listar_temporadas(urllib.parse.unquote(params['serie']))
elif action == 'episodios':
    listar_episodios(urllib.parse.unquote(params['serie']), params['temporada'])
elif action == 'play':
    play(urllib.parse.unquote(params['url']))
