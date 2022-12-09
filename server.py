import grpc
import audio_pb2
import audio_pb2_grpc
from concurrent import futures
import pyaudio
import gzip

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import hashlib


ADDR = '0.0.0.0:1080'

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

PASSWORD = '123321'

COMPRESSLEVEL = 2


class AudioService(audio_pb2_grpc.PlayAudioServicer):
    def __init__(self, encryptor) -> None:
        self.encryptor = encryptor

    def StartListening(self, request, context):
        print(request.sig)

        audioSource = AudioSource(FORMAT, CHANNELS, RATE, CHUNK)

        for data in audioSource.getAudio():
            # data = gzip.compress(data, compresslevel=COMPRESSLEVEL)
            # yield audio_pb2.Chunk(wave=self.encryptor.encrypt(data))
            yield audio_pb2.Chunk(wave=data)


class AudioSource:
    def __init__(self, format, channels, rate, frames_per_buffer) -> None:
        self.format = format
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def getAudio(self):
        p = pyaudio.PyAudio()

        SPEAKERS = p.get_default_output_device_info()["hostApi"]

        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.frames_per_buffer,
                        input_host_api_specific_stream_info=SPEAKERS)

        while True:
            yield stream.read(CHUNK)


class Encryptor:
    def __init__(self, password) -> None:
        self.key = hashlib.sha256(bytes(password, encoding='utf-8')).digest()

    def encrypt(self, plainText):
        self.cipher = AES.new(self.key, AES.MODE_CBC)
        cipherText = self.cipher.iv + \
            self.cipher.encrypt(pad(plainText, AES.block_size))

        return cipherText


def serve():
    encryptor = Encryptor(PASSWORD)

    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=8))
    audio_pb2_grpc.add_PlayAudioServicer_to_server(
        servicer=AudioService(encryptor), server=server)
    server.add_insecure_port(ADDR)
    server.start()

    print("started")

    server.wait_for_termination()


if __name__ == '__main__':
    serve()
