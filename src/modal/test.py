import modal
import os
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import tempfile
import json

stub = modal.Stub("test", image=modal.Image.debian_slim().pip_install("openai~=0.27.0", "python-multipart"))

context = [{"role": "user", "content": f"Say hi to me."}]
@stub.function(secret=modal.Secret.from_name("my-openai-secret"))
def test():
    import openai
    
    species = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."}] + context
        )
    print(species)
