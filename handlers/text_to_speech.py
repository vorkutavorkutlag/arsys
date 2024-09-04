import edge_tts


class TextSpeech:
    @staticmethod
    async def tts(text: str, filename: str, rate=20) -> None:
        voice = "Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)"
        input_path = f"{filename}.wav"
        rates = f"+{rate}%" if rate >= 0 else f"{rate}%"

        await edge_tts.Communicate(text,
                                   voice=voice,
                                   rate=rates,).save(input_path)




