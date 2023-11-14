import struct
import time
from typing import List
import llm


class Embedding:
    @classmethod
    def from_bytes(cls, bytes: bytes):
        emb = Embedding()
        emb.__embedding_floats = cls.__bytes2f(bytes)
        return emb

    @staticmethod
    def from_floats(floats: List[float]):
        emb = Embedding()
        emb.__embedding_floats = floats
        return emb

    def as_floats(self) -> List[float]:
        return self.__embedding_floats

    def as_bytes(self) -> bytes:
        return self.__f2bytes(self.__embedding_floats)

    def __f2bytes(floats: List[float]):
        return struct.pack("<" + "f" * len(floats), *floats)

    def __bytes2f(bytes: bytes):
        return struct.unpack("<" + "f" * (len(bytes) // 4), bytes)


class Embedder:
    def __init__(self, model_name='ada-002'):
        self.model = llm.get_embedding_model(model_name)

    def embed(self, text):
        def embed_single(text):
            return self.model.embed(text)
        # retry in case of rate limiting
        result = self._retry(embed_single, text)
        return Embedding.from_floats(result)

    def similarity(self, emb1: Embedding, emb2: Embedding):
        return llm.cosine_similarity(emb1.as_floats(), emb2.as_floats())

    def _retry(self, func, *args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f'failed to {func.__name__}: {e}')
                time.sleep(2**i)
        raise Exception('failed to execute function')
