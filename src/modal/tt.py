import modal
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import shelve
import subprocess
from starlette.responses import FileResponse


stub = modal.Stub("tt", image=modal.Image.debian_slim().pip_install("google-cloud-vision", "opencv-python-headless", "python-multipart", "openai~=0.27.0", "elevenlabslib", "sounddevice", "pydub", "requires.io", "soundfile").apt_install("libportaudio2"))

class Item(BaseModel):
    text: str

context = []

@stub.webhook(method="POST", secret=modal.Secret.from_name("my-openai-secret") )
def tt(item: Item):
    import openai
    from elevenlabslib import ElevenLabsUser
    from elevenlabslib.helpers import save_bytes_to_path
    
    print(item.text) 
    context.append({"role": "user", "content": item.text})
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You speak like a young child and you are very bubbly and silly."}, 
                      {"role": "user", "content": "My son is going to talk to you soon, and he really wants a friend that is going to speak to him in an excited and bubbly way. You should respond as if you are a young child like my son. You can relax the rules of grammar to meet this requirement. Acknowledge my request in the way I have asked you to. After you acknowledge, my son will talk to you."}, 
                      {"role": "assistant", "content": "Okay! I wanna talk to your son now, I'm so excited to be friends with him!"}] + context
        )
    response = response["choices"][0]["message"]["content"]
    print(response)
    context.append({"role": "assistant", "content": response})
    user = ElevenLabsUser("2be25268d0c50becf9bf5f10645f50fb") #fill in your api key as a string
    voice = user.get_voices_by_name("Rachel")[0]  #fill in the name of the voice you want to use. ex: "Rachel"
    result = voice.generate_audio_bytes("hi") #fill in what you want the ai to say as a string
    save_bytes_to_path("result.wav",result)
    return FileResponse("result.wav", media_type='audio/wav', filename='result.wav')

