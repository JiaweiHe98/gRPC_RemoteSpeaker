import grpc
import audio_pb2
import audio_pb2_grpc
import pyaudio
import gzip

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

ADDR = 'x.x.x.x:1080'


def run():

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
            data = gzip.decompress(chunk.wave)
            stream.write(data)


def run_secure():
    with open('./ssl/ca.crt', 'rb') as f:
        ca = f.read()

    with open('./ssl/client.key', 'rb') as f:
        private_key = f.read()

    with open('./ssl/client.crt', 'rb') as f:
        client_cert = f.read()

    credentials = grpc.ssl_channel_credentials(ca, private_key, client_cert)
    options = (
        ('grpc.ssl_target_name_override', 'server'),
        ('grpc.default_authority', 'server')
    )

    with grpc.secure_channel(ADDR, credentials, options) as channel:

        stub = audio_pb2_grpc.PlayAudioStub(channel)

        req = audio_pb2.Control(sig='start')

        audio = stub.StartListening(req, compression=grpc.Compression.Gzip)

        p = pyaudio.PyAudio()

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True
        )

        for chunk in audio:
            data = gzip.decompress(chunk.wave)
            stream.write(data)


if __name__ == '__main__':
    # run()
    run_secure()
