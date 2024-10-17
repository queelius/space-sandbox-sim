from audio.audio_queue import AudioQueue
from events.event_bus import EventBus
from typing import Callable
from pygame.math import Vector2 as vec2

class AudioManager:
    def __init__(self,
                 event_bus: EventBus,
                 stereo: bool = True,
                 min_vol: float = 0.1,
                 max_workers: int = 10):
        self.audio_queue = AudioQueue(min_vol=min_vol,
                                      stereo=stereo,
                                      max_workers=max_workers)
        
        #event_bus.subscribe('spring_break', self.handle_spring_break)

    def handle_spring_break(self, data):
        get_source_pos = data.get('get_source_pos', lambda: vec2(0,0))
        get_listener_pos = data.get('get_listener_pos', lambda: vec2(0,0))
        cutoff_distance = data.get('get_cutoff_distance', float('inf'))
        delay = data.get('delay', 0.0)
        self.audio_queue.add('assets/wav/mixkit-arcade-retro-game-over-213.wav',
                             get_source_pos, get_listener_pos, cutoff_distance, delay)

    def stop(self):
        self.audio_queue.stop()