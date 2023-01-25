import grpc
import audio_pb2
import audio_pb2_grpc
from concurrent import futures
import pyaudio
import gzip


PORT = 1080

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

COMPRESSLEVEL = 2


class AudioService(audio_pb2_grpc.PlayAudioServicer):
    def __init__(self) -> None:
        pass

    def StartListening(self, request, context):
        print(request.sig)

        audioSource = AudioSource(FORMAT, CHANNELS, RATE, CHUNK)

        for data in audioSource.getAudio():
            data = gzip.compress(data, compresslevel=COMPRESSLEVEL)
            yield audio_pb2.Chunk(wave=data)
            # yield audio_pb2.Chunk(wave=data)


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


def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    audio_pb2_grpc.add_PlayAudioServicer_to_server(
        servicer=AudioService(), server=server)
    server.add_insecure_port('[::]:' + str(PORT))
    server.start()

    print("started")

    server.wait_for_termination()


def serveSecure():

    with open('./ssl/ca.crt', 'rb') as f:
        ca = f.read()

    with open('./ssl/server.key', 'rb') as f:
        private_key = f.read()

    with open('./ssl/server.crt', 'rb') as f:
        server_cert = f.read()

    credentials = grpc.ssl_server_credentials(
        [(private_key, server_cert)],
        root_certificates=ca,
        require_client_auth=True
    )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    audio_pb2_grpc.add_PlayAudioServicer_to_server(
        servicer=AudioService(), server=server)
    server.add_secure_port('[::]:' + str(PORT), credentials)
    server.start()

    print("started")

    server.wait_for_termination()


if __name__ == '__main__':

    serveSecure()

    # serve()
