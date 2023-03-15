import modal
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import shelve

stub = modal.Stub("tt", image=modal.Image.debian_slim().pip_install("google-cloud-vision", "opencv-python-headless", "python-multipart", "openai~=0.27.0"))

class Item(BaseModel):
    text: str

context = []

@stub.webhook(method="POST", secret=modal.Secret.from_name("my-openai-secret") )
def tt(item: Item):
    import openai
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
    return {"text": response}

