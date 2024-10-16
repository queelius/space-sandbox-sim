import pygame
import math
from pygame.math import Vector2 as vec2
from collections import deque
import threading
import time
from typing import Callable, Tuple
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

class AudioQueue:
    """
    A queue of audio samples to play simultaneously with a listener point of view.
    """

    def __init__(self,
                 get_viewport: Callable[[], Tuple[float, float, float, float]],
                 stereo: bool = True,
                 max_workers: int = 10):
        """
        Initialize the AudioQueue.
        
        Args:
            get_viewport: A function that returns a 4-tuple representing the
                          viewport (left, right, top, bottom) of simulation.
            stereo: Whether to use stereo sound (default is True).
            max_workers: Maximum number of threads in the pool (default is 10).
        """
        self.stereo = stereo
        self.queue: deque = deque()
        self.lock = threading.Lock()
        self.get_viewport = get_viewport
        self.running = True
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.playback_thread.start()
    
    def add(self, sound_file: str, get_source_pos: Callable[[], vec2], delay: float = 0.0):
        """
        Add a sound to the queue.
        
        Args:
            sound_file: The path to the sound file.
            get_source_position: A function that returns the current position of the sound source as a vec2.
            delay: Time delay before playing the sound (default is 0.0 seconds).
        """
        with self.lock:
            if self.running:
                self.queue.append((sound_file, get_source_pos, delay))
            else:
                logging.info("AudioQueue is stopped. Cannot add new sounds.")
    
    def _playback_loop(self):
        """
        Continuously play sounds from the queue.
        """
        while self.running:
            with self.lock:
                if not self.queue:
                    sounds_to_play = None
                else:
                    sounds_to_play = list(self.queue)
                    self.queue.clear()

            if sounds_to_play:
                for sound_file, get_source_pos, delay in sounds_to_play:
                    self.executor.submit(self._play_sound, sound_file, get_source_pos, delay)
            else:
                time.sleep(0.01)  # Sleep briefly to prevent busy waiting

    def _play_sound(self, sound_file: str, get_source_pos: Callable[[], vec2], delay: float):
        """
        Play a single sound with a potential delay and adjust volume and spatial effects based on listener position.
        
        Args:
            sound_file (str): The path to the sound file.
            get_source_pos (function): A function that returns the current position of the sound source.
            delay (float): Delay before playing the sound.
        """
        if delay > 0:
            # Instead of sleeping for the entire delay, check periodically if running is still True
            end_time = time.time() + delay
            while time.time() < end_time:
                if not self.running:
                    return
                time.sleep(min(0.1, end_time - time.time()))
        
        if not self.running:
            return

        try:
            sound = pygame.mixer.Sound(sound_file)
            channel = sound.play()  # Play the sound immediately without waiting for others to finish
            if channel is None:
                return  # If the channel couldn't be allocated, exit early
            while channel.get_busy():
                if not self.running:
                    channel.stop()
                    break
                source_pos = get_source_pos()
                _, left_vol, right_vol = self._calculate_vol(source_pos)
                channel.set_volume(left_vol, right_vol)
                time.sleep(0.01)
        except pygame.error as e:
            logging.error(f"Error playing sound: {e}")

    def _calculate_vol(self, source_pos: vec2) -> Tuple[float, float, float]:
        """
        Calculate the volume and stereo balance of the sound based on the viewport.
        The listener is assumed to be at the center of the viewport.

        Args:
            source_pos (vec2): The position of the sound source.

        Returns:
            tuple: The overall volume level (between 0 and 1), left channel volume, and right channel volume.
        """

        # Get viewport boundaries
        viewport = self.get_viewport()
        x_min, x_max, y_min, y_max = viewport

        # Return zero volume if the source is outside the viewport
        if not (x_min <= source_pos.x <= x_max and y_min <= source_pos.y <= y_max):
            return 0.0, 0.0, 0.0

        # Listener is at the center of the viewport
        listener_pos = vec2((x_min + x_max) / 2, (y_min + y_max) / 2)

        # Calculate maximum distance (from listener to viewport corner)
        half_width = 0.5 * (x_max - x_min)
        half_height = 0.5 * (y_max - y_min)
        max_dist = math.hypot(half_width, half_height)

        # Distance from source to listener
        distance = (listener_pos - source_pos).length()

        # Calculate volume using inverse square law with a minimum volume threshold
        min_vol = 0.1  # Minimum volume at max distance
        vol = max(min_vol, 1 - (distance / max_dist) ** 2)

        if not self.stereo:
            return vol, vol, vol

        # Calculate pan value (-1 for left, 1 for right)
        dx = source_pos.x - listener_pos.x
        pan = self._project(dx, -half_width, half_width, -1, 1)

        # Compute the angle for equal power panning
        angle = (pan + 1) * (math.pi / 4)  # Maps pan from [-1,1] to [0, π/2]
        left_vol = vol * math.cos(angle)
        right_vol = vol * math.sin(angle)

        return vol, left_vol, right_vol
    
    @staticmethod
    def _project(x: float, x_min: float, x_max: float, z_min:float=0, z_max: float=1):    
        """
        Project a value x from the range [x_min, x_max] to the range [z_min, z_max].
        """
        return z_min + (x - x_min) * (z_max - z_min) / (x_max - x_min)
        
    
    def stop(self):
        """
        Stop the playback thread, clear the queue, stop all playing sounds, and shutdown the thread pool.
        """
        self.running = False
        with self.lock:
            self.queue.clear()
        self.executor.shutdown(wait=False)  # Do not wait for running tasks to finish
        pygame.mixer.stop()  # Stop all currently playing sounds
        self.playback_thread.join()

# # Example listener position function
# def get_viewport():
#     # 4-tuple representing the viewport (left, right, top, bottom)
#     return -10.0, 10.0, -10.0, 10.0

# start_time = time.time()
# # Example source position function
# def get_source_position():
#     current_time = time.time()
#     dt = current_time - start_time
#     x = 10.0 - dt
#     y = dt - 10
#     return vec2(x, y)

# # Example Usage
# if __name__ == "__main__":
#     audio_queue = AudioQueue(get_viewport, stereo=True)
    
#     audio_queue.add('../assets/wav/OSR_us_000_0016_8k.wav', get_source_position)
#     audio_queue.add('../assets/wav/mixkit-cinematic-laser-gun-thunder-1287.wav', get_source_position)
#     audio_queue.add('../assets/wav/mixkit-fast-rocket-whoosh-1714.wav', get_source_position)
#     audio_queue.add('../assets/wav/mixkit-cinematic-laser-gun-thunder-1287.wav', get_source_position, delay=2)
#     audio_queue.add('../assets/wav/mixkit-cinematic-laser-gun-thunder-1287.wav', get_source_position, delay=10)
    
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         logging.info("Stopping AudioQueue...")
#     finally:
#         # Stop the audio queue when done (e.g., on program exit)
#         audio_queue.stop()
#         logging.info("AudioQueue stopped.")