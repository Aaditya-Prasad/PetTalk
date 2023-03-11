import modal
import os

stub = modal.Stub(image=modal.Image.debian_slim().pip_install("openai~=0.27.0"))


@stub.function(secret=modal.Secret.from_name("my-openai-secret"))
def complete_text(prompt):
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
    )
    print(response["choices"][0]["message"]["content"])


if __name__ == "__main__":
    with stub.run():
        print(complete_text.call("Say the word blue back to me please."))
