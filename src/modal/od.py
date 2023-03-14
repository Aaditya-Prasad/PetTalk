import json
import os

import modal
from fastapi import FastAPI, File, UploadFile

stub = modal.Stub(image=modal.Image.debian_slim().pip_install("google-cloud-vision", "opencv-python-headless"))


@stub.webhook(method="POST", secret=modal.Secret.from_name("my-googlecloud-secret"),
                mounts=[modal.Mount.from_local_dir("pictures", remote_path="/root/pictures")])
def query(file: UploadFile = File(...)):
    from google.oauth2 import service_account
    from google.cloud import vision
    import numpy as np
    import os
    import cv2 as cv

    service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    def detect_labels(content):
        """
        Detects labels in the current file
        This calls the google cloud vision api which is why we need credentials
        Only the label descriptions are returned
        Args: 
        content: the image content.
        """
        import io
        import os
        # Imports the Google Cloud client library
        from google.cloud import vision
        # Instantiates a client
        client = vision.ImageAnnotatorClient(credentials = credentials)
        # The name of the image file to annotate
        # file_name = os.path.abspath(path)
        # # Loads the image into memory
        # with io.open(file_name, 'rb') as image_file:
        #     content = image_file.read()
        image = vision.Image(content=content)
        # Performs label detection on the image file
        response = client.label_detection(image=image)
        labels = response.label_annotations
        return [t.description for t in labels]
    
    def localize_objects(content):
        """
        Localize objects in the local image.

        Args:
        content: the image content.
        """
        from google.cloud import vision
        client = vision.ImageAnnotatorClient(credentials = credentials)

        # with open(path, 'rb') as image_file:
        #     content = image_file.read()
        image = vision.Image(content=content)

        objects = client.object_localization(
            image=image).localized_object_annotations

        return objects
    
    def cutout(content):
        """
        This takes the first detected object in the localized object
        and cuts it out of the image so that we have a cropped picture 
        of just the dog.
        
        Args:
        content: the image content.
        """
        img = cv.imdecode(content)
        x, y, _ = img.shape
        objs = localize_objects(content)
        ver = objs[0].bounding_poly.normalized_vertices[:]
        x_b = (int(ver[0].x * x), int(ver[1].x * x))
        y_b = (int(ver[1].y * y), int(ver[2].y * y))
        return (x_b, y_b), img[x_b[0]:x_b[1], y_b[0]:y_b[1]]
  
    def compute(content):
        #just calls everything
        labels = detect_labels(content)
        bbox, cut_img = cutout(content)
        return labels, bbox, cut_img

    content = file.file.read()
    a, b, c = compute(content)
    print("hello")
    print(a)
    return {"labels": a}

