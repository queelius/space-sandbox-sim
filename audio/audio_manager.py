from audio.audio_queue import AudioQueue
from events.event_bus import EventBus
from typing import Callable
from pygame.math import Vector2 as vec2

class AudioManager:
    def __init__(self,
                 event_bus: EventBus,
                 get_viewport: Callable,
                 stereo: bool = True,
                 max_workers: int = 10):
        self.audio_queue = AudioQueue(get_viewport=get_viewport,
                                      stereo=True,
                                      max_workers=max_workers)
        event_bus.subscribe('spring_break', self.handle_spring_break)

    def handle_spring_break(self, data):
        get_source_pos = data.get('get_source_pos', lambda: vec2(0,0))
        delay = data.get('delay', 0.0)
        self.audio_queue.add('assets/wav/mixkit-arcade-retro-game-over-213.wav',
                             get_source_pos, delay)

    def stop(self):
        self.audio_queue.stop()