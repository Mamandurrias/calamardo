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

    # Opción Géneros con icono
    item = xbmcgui.ListItem("Géneros")
    item.setArt({'icon': 'DefaultGenre.png', 'thumb': 'DefaultGenre.png'})
    item.setInfo('video', {'title': 'Géneros', 'mediatype': 'tvshow'})
    xbmcplugin.addDirectoryItem(HANDLE, f"{sys.argv[0]}?action=generos", item, True)

    if tiene_colecciones:
        item = xbmcgui.ListItem("Colecciones")
        item.setArt({'icon': 'DefaultAddons.png', 'thumb': 'DefaultAddons.png'})
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
        item.setArt({'icon': 'DefaultGenre.png', 'thumb': 'DefaultGenre.png'})
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
        item.setArt({'icon': 'DefaultAddons.png', 'thumb': 'DefaultAddons.png'})
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
        sinopsis = data.get('sinopsis', '')
        anio = data.get('anio', '')
        art = {'poster': poster, 'thumb': poster, 'fanart': poster, 'icon': poster}
        nombre_mostrar = f"{nombre} ({anio})" if anio and anio.isdigit() else nombre
        item = xbmcgui.ListItem(nombre_mostrar)
        item.setArt(art)
        item.setInfo('video', {'title': nombre_mostrar, 'mediatype': 'tvshow', 'plot': sinopsis, 'year': int(anio) if anio and anio.isdigit() else 0})
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
        sinopsis = data.get('sinopsis', '')
        anio = data.get('anio', '')
        art = {'poster': poster, 'thumb': poster, 'fanart': poster, 'icon': poster}
        nombre_mostrar = f"{nombre} ({anio})" if anio and anio.isdigit() else nombre
        item = xbmcgui.ListItem(nombre_mostrar)
        item.setArt(art)
        item.setInfo('video', {'title': nombre_mostrar, 'mediatype': 'tvshow', 'plot': sinopsis, 'year': int(anio) if anio and anio.isdigit() else 0})
        url = f"{sys.argv[0]}?action=temporadas&serie={urllib.parse.quote(nombre)}"
        xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
    xbmcplugin.setContent(HANDLE, 'tvshows')
    xbmcplugin.endOfDirectory(HANDLE)

def listar_temporadas(serie):
    db = get_series()
    data = db.get(serie, {})
    temps = sorted(data.get('temporadas', []), key=lambda x: int(x))
    for temp in temps:
        item = xbmcgui.ListItem(f"Temporada {temp}")
        item.setInfo('video', {'title': f"Temporada {temp}", 'mediatype': 'season'})
        url = f"{sys.argv[0]}?action=episodios&serie={urllib.parse.quote(serie)}&temp={temp}"
        xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
    xbmcplugin.setContent(HANDLE, 'seasons')
    xbmcplugin.endOfDirectory(HANDLE)

def listar_episodios(serie, temp):
    db = get_series()
    data = db.get(serie, {})
    episodios = data.get('episodios', {}).get(temp, [])
    for ep in episodios:
        num = ep.get('episodio', '')
        titulo = ep.get('titulo', '')
        strm_url = ep.get('strm', '')
        if not strm_url:
            continue
        nombre = f"{num} - {titulo}" if titulo else f"Episodio {num}"
        item = xbmcgui.ListItem(nombre)
        item.setInfo('video', {'title': nombre, 'mediatype': 'episode', 'season': int(temp), 'episode': int(num) if num.isdigit() else 0})
        xbmcplugin.addDirectoryItem(HANDLE, strm_url, item, False)
    xbmcplugin.setContent(HANDLE, 'episodes')
    xbmcplugin.endOfDirectory(HANDLE)

def main():
    params = {}
    if len(sys.argv) > 2:
        query = sys.argv[2].lstrip('?')
        if query:
            for p in query.split('&'):
                if '=' in p:
                    k, v = p.split('=', 1)
                    params[k] = urllib.parse.unquote(v)

    action = params.get('action', 'menu')
    if action == 'menu':
        menu_principal()
    elif action == 'generos':
        listar_generos()
    elif action == 'colecciones':
        listar_colecciones()
    elif action == 'series_por_genero':
        genero = params.get('genero', '')
        listar_series_por_genero(genero)
    elif action == 'series_por_coleccion':
        coleccion = params.get('coleccion', '')
        listar_series_por_coleccion(coleccion)
    elif action == 'temporadas':
        serie = params.get('serie', '')
        listar_temporadas(serie)
    elif action == 'episodios':
        serie = params.get('serie', '')
        temp = params.get('temp', '')
        listar_episodios(serie, temp)

if __name__ == "__main__":
    main()
