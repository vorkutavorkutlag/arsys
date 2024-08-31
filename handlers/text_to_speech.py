from gtts import gTTS
from pydub import AudioSegment
from os import remove


class TTS:
    @staticmethod
    def tts(text: str, raw_filename: str, octaves: float = 0.15) -> None:
        # CREATES A WAV FILE WITH TTS,
        # PITCH CHANGEABLE
        filename = raw_filename.replace('"', '')
        google_tts = gTTS(text)
        google_tts.save(f"tts\\temp_{filename}.mp3")
        converter = AudioSegment.from_mp3(f"tts\\temp_{filename}.mp3")
        converter.export(f"tts\\temp_{filename}.wav", format="wav")

        sound = AudioSegment.from_file(f"tts\\temp_{filename}.wav", format='wav')
        new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
        hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
        hipitch_sound = hipitch_sound.set_frame_rate(44100)
        hipitch_sound.export(f"tts\\{filename}.wav", format="wav")

        remove(f"tts\\temp_{filename}.mp3")
        remove(f"tts\\temp_{filename}.wav")




