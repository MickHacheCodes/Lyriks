import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import re

app = FastAPI(title="Lyriks Backend API")

LYRICS_VAULT_DIR = "/vault"
os.makedirs(LYRICS_VAULT_DIR, exist_ok=True)

@app.get("/lyrics")
async def get_lyrics(artist: str, track: str):
    safe_artist = re.sub(r'[/%0]', '', artist).strip()
    safe_track = re.sub(r'[/%0]', '', track).strip()
    file_name = f"{safe_artist} - {safe_track}.lrc"
    file_path = os.path.join(LYRICS_VAULT_DIR, file_name)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/plain", filename=file_name)

    lrclib_url = "https://lrclib.net/api/get"
    params = {"artist_name": artist, "track_name": track}

    async with httpx.AsyncClient() as client:
        response = await client.get(lrclib_url, params=params)

    if response.status_code == 200:
        data = response.json()
        synced_lyrics = data.get("syncedLyrics")
        if synced_lyrics:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(synced_lyrics)
            return FileResponse(file_path, media_type="text/plain", filename=file_name)
        else:
            raise HTTPException(status_code=404, detail="Synced lyrics not found on LRCLIB.")
            
    raise HTTPException(status_code=404, detail="Track not found on LRCLIB.")