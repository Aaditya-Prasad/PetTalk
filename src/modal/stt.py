import modal
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

stub = modal.Stub(image=modal.Image.debian_slim().pip_install("openai~=0.27.0"))


@stub.webhook(method="POST", secret=modal.Secret.from_name("my-openai-secret") )
def stt(file: UploadFile = File(...)):
    import openai
    audio_file = open(file, "rb")
    response = openai.Audio.transcribe("whisper-1", audio_file)
    return response
