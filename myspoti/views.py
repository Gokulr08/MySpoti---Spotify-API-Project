from xhtml2pdf import pisa
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.cache import cache
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

SCOPE = 'user-top-read'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, 
                                               client_secret=SPOTIPY_CLIENT_SECRET, 
                                               redirect_uri=SPOTIPY_REDIRECT_URI, 
                                               scope=SCOPE))

def get_track_features(track_id):
    meta = sp.track(track_id)
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    spotify_url = meta['external_urls']['spotify']
    album_cover = meta['album']['images'][0]['url'] if meta['album']['images'] else ''  # Check if images exist
    popularity = meta['popularity']
    release_date = meta['album']['release_date']
    duration_ms = meta['duration_ms']
    duration_min = round(duration_ms / 60000, 2)
    return [name, album, artist, spotify_url, album_cover, duration_min, popularity, release_date]

def fetch_spotify_data():
    top_tracks = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
    track_ids = [track['id'] for track in top_tracks['items']]
    tracks = [get_track_features(track_id) for track_id in track_ids]
    return tracks

def index(request):
    return render(request, 'index.html')


def download_pdf(request):
    tracks = cache.get('spotify_tracks')
    if not tracks:
        top_tracks = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
        track_ids = [track['id'] for track in top_tracks['items']]
        tracks = [get_track_features(track_id) for track_id in track_ids]
        cache.set('spotify_tracks', tracks, timeout=3600)  # Cache for 1 hour

    html = render_to_string('pdf_template.html', {'tracks': tracks})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="spotify_tracks.pdf"'

    # Created PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors while generating the PDF.')
    return response
