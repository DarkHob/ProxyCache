import time
from typing import Tuple

class MusicService:
    def get_song(self, song_name: str) -> str:
        raise NotImplementedError

class RealMusicService(MusicService):
    def get_song(self, song_name: str) -> str:
        # Simula operación costosa o remota
        print(f"Buscando la canción '{song_name}' en el servidor...")
        time.sleep(2)  # Latencia simulada
        return f"🎵 Datos de la canción: {song_name}"

class MusicServiceCacheProxy(MusicService):
    def __init__(self):
        self.real_service = RealMusicService()
        self.cache: dict[str, str] = {}

    def get_song_with_source(self, song_name: str) -> Tuple[str, str]:
        if song_name in self.cache:
            return self.cache[song_name], "cache"
        data = self.real_service.get_song(song_name)
        self.cache[song_name] = data
        return data, "server"
    """
    Devuelve (data, source):
      - source = "cache" si se obtuvo de caché
      - source = "server" si se consultó el servidor real
    """