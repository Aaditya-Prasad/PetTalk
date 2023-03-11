import modal
from fastapi import FastAPI, File, UploadFile

stub = modal.Stub(image=modal.Image.debian_slim().pip_install("openai~=0.27.0"))

app = FastAPI()

@app.post("/stt")
@stub.function(secret=modal.Secret.from_name("my-openai-secret"))
async def stt(file: UploadFile = File(...)):
    import openai
    contents = await myfile.read()
    audio_file = open(file, "rb")
    response = openai.Audio.transcribe("whisper-1", audio_file)

@stub.function(secret=modal.Secret.from_name("my-openai-secret"))
#def ttt


