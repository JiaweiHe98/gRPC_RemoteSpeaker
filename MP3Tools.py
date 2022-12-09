from io import BytesIO
from pydub import AudioSegment


class MP3FrameHelper:
    def __init__(self) -> None:
        pass

    def encode(self, raw, sampleRate, channels):
        seg = AudioSegment(data=raw,
                           sample_width=2,
                           frame_rate=sampleRate,
                           channels=channels)
        mp3IO = BytesIO()
        seg.export(mp3IO, format='mp3')
        return mp3IO.getvalue()

    def decode(self, wave):
        seg = AudioSegment.from_mp3(BytesIO(wave))
        return seg.raw_data
