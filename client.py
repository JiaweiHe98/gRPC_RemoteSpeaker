import grpc
import audio_pb2
import audio_pb2_grpc
import pyaudio
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

ADDR = '192.168.0.5:1080'

PASSWORD = 'my-password'


class Decryptor:
    def __init__(self, password) -> None:
        self.key = hashlib.sha256(bytes(password, encoding='utf-8')).digest()


    def decrypt(self, cipherText):
        _iv = cipherText[:16]
        cipherText = cipherText[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, _iv)

        return unpad(cipher.decrypt(cipherText), AES.block_size)


def run():

    decryptor = Decryptor(PASSWORD)

    with grpc.insecure_channel(ADDR) as channel:

        stub = audio_pb2_grpc.PlayAudioStub(channel)

        req = audio_pb2.Control(sig='start')

        audio = stub.StartListening(req)

        p = pyaudio.PyAudio()

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True
        )

        for chunk in audio:
            plainWave = decryptor.decrypt(chunk.wave)
            stream.write(plainWave)


if __name__ == '__main__':
    run()
