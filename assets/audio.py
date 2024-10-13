import numpy as np
import pygame

# Initialize pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

def generate_snap_sound(frequency1=1500, frequency2=1000, duration=0.3, sample_rate=22050):
    """
    Generate an improved snap sound effect using layered sine waves and noise.
    
    Args:
        frequency1 (float): The base frequency of the snapping sound.
        frequency2 (float): A secondary frequency to layer.
        duration (float): Duration of the sound in seconds.
        sample_rate (int): The sample rate (default 44100 Hz).
        
    Returns:
        numpy array: The generated audio signal.
    """
    # Time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate layered sine waves
    amplitude = np.exp(-10 * t)  # Sharper decay for a quick snap
    wave1 = amplitude * np.sin(2 * np.pi * frequency1 * t)
    wave2 = amplitude * np.sin(2 * np.pi * frequency2 * t)
    
    # Add noise component (white noise to simulate the snap)
    noise = amplitude * np.random.normal(0, 0.5, len(t))
    
    # Combine the two waves and the noise
    combined_wave = wave1 + wave2 + noise
    
    # Normalize the sound
    combined_wave = combined_wave / np.max(np.abs(combined_wave))
    
    # Convert the sound wave to 16-bit data for pygame
    sound_data = np.int16(combined_wave * 32767)
    stereo_sound = np.column_stack([sound_data, sound_data])  # Convert to stereo
    return stereo_sound

def play(sound_data):
    """
    Play the generated sound using pygame.
    
    Args:
        sound_data (numpy array): The generated sound data.
    """
    pygame.sndarray.make_sound(sound_data).play()
