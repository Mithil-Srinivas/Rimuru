import torch
import torchaudio
import os
import io
from zonos.model import Zonos
from zonos.conditioning import make_cond_dict
from zonos.utils import DEFAULT_DEVICE as device

class TTS:
    def __init__(self):
        self.__project_dir = os.path.join(os.path.dirname(__file__), '..')
        self.__model_path = os.path.join(self.__project_dir, 'models/zonos_transformer.safetensors')
        self.__config_path = os.path.join(self.__project_dir, 'models/zonos_transformer.json')
        self.__embed_path = os.path.join(self.__project_dir, 'embeddings')
        self.model = None
        self.speaker = []
        self.speakers = os.listdir(self.__embed_path)
        self.__check()

    def __check(self):
        if torch.cuda.get_device_name(0) != "NVIDIA GeForce RTX 4060 Laptop GPU":
            quit()

    def load(self):
        self.model = Zonos.from_local(self.__config_path, self.__model_path, device=device)

    def load_speaker(self, name):
        self.speaker[0] = name
        self.speaker[1] = torch.load(f"{name}.pt")


    def save_speaker(self, name, audio_bytes):
        audio_buffer = io.BytesIO(audio_bytes)
        wav, sampling_rate = torchaudio.load(audio_buffer)
        temp_speaker = self.model.make_speaker_embedding(wav, sampling_rate)
        torch.manual_seed(123)
        torch.save(temp_speaker, f"{name}.pt")
        del temp_speaker
        self.speakers = os.listdir(self.__embed_path)


    def gen(self, prompt: str):
        cond_dict = make_cond_dict(text=prompt, speaker=self.speaker, language="en-us")
        conditioning = self.model.prepare_conditioning(cond_dict)

        codes = self.model.generate(conditioning)

        wavs = self.model.autoencoder.decode(codes).cpu()
        torchaudio.save("sample.wav", wavs[0], self.model.autoencoder.sampling_rate)
