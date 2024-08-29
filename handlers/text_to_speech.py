from gtts import gTTS
from pydub import AudioSegment
from os import remove


class TTS:
    def __init__(self, text: str, filename: str, octaves: float = 0.1) -> None:
        # CREATES A WAV FILE WITH TTS,
        # PITCH CHANGEABLE
        google_tts = gTTS(text)
        google_tts.save("temp.mp3")
        converter = AudioSegment.from_mp3("temp.mp3")
        converter.export("temp.wav", format="wav")

        sound = AudioSegment.from_file("temp.wav", format='wav')
        new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
        hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
        hipitch_sound = hipitch_sound.set_frame_rate(44100)
        hipitch_sound.export(f"tts\\{filename}.wav", format="wav")

        remove("temp.mp3")
        remove("temp.wav")
