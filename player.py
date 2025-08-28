import yt_dlp
import pygame
import os

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_music = None
        self.music_volume = 0.5  # Volume inicial (50%)
        self.is_playing = False
        self.music_length = 0
        self.current_time = 0  # Tempo acumulado

    def load_music(self, music_file):
        """Carrega a música para o player."""
        self.current_music = music_file
        pygame.mixer.music.load(music_file)
        self.music_length = self.get_music_length()

    def download_music_from_youtube(self, search_query):
        """Baixa a música do YouTube com base na consulta de pesquisa."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'ffmpeg-location': 'C:/ffmpeg/bin'  # Caminho para o binário do FFmpeg (verifique se o caminho está correto)
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{search_query}", download=True)
        
        # Retorna o título da música que foi baixada
        return info_dict['title']

    def get_music_length(self):
        """Retorna a duração da música carregada."""
        if self.current_music is None:
            return 0
        return pygame.mixer.Sound(self.current_music).get_length()

    def play_music(self, start_time=0):
        """Inicia a reprodução da música a partir do tempo especificado."""
        pygame.mixer.music.play(start=start_time)
        self.is_playing = True
        self.current_time = start_time  # Armazena o tempo de início

    def pause_music(self):
        """Pausa a reprodução da música."""
        pygame.mixer.music.pause()
        self.is_playing = False

    def resume_music(self):
        """Retoma a reprodução da música."""
        pygame.mixer.music.unpause()
        self.is_playing = True

    def stop_music(self):
        """Para a reprodução da música."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_time = 0

    def set_position(self, time):
        """Define a posição da música no tempo especificado."""
        pygame.mixer.music.set_pos(time)
        self.current_time = time

    def get_current_time(self):
        """Retorna o tempo total considerando pausas e reproduções."""
        if self.is_playing:
            current_time = self.current_time + pygame.mixer.music.get_pos() / 1000
            return current_time
        else:
            return self.current_time

    def set_volume(self, volume):
        """Define o volume da música."""
        self.music_volume = volume
        pygame.mixer.music.set_volume(self.music_volume)
