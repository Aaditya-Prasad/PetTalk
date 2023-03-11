import json
import os

import modal

stub = modal.Stub(image=modal.Image.debian_slim().pip_install("google-cloud-vision", "opencv-python-headless"))


@stub.function(secret=modal.Secret.from_name("my-googlecloud-secret"),
                mounts=[modal.Mount.from_local_dir("pictures", remote_path="/root/pictures")])
def query():
    from google.oauth2 import service_account
    from google.cloud import vision
    import numpy as np
    import os
    import cv2 as cv

    service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    # Run a query against a public dataset with name US first name statistics
    def detect_labels(path):
        import io
        import os
        # Imports the Google Cloud client library
        from google.cloud import vision
        # Instantiates a client
        client = vision.ImageAnnotatorClient(credentials = credentials)
        # The name of the image file to annotate
        file_name = os.path.abspath(path)
        # Loads the image into memory
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        # Performs label detection on the image file
        response = client.label_detection(image=image)
        labels = response.label_annotations
        return labels
    
    def localize_objects(path):
        """Localize objects in the local image.

        Args:
        path: The path to the local file.
        """
        from google.cloud import vision
        client = vision.ImageAnnotatorClient(credentials = credentials)

        with open(path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        objects = client.object_localization(
            image=image).localized_object_annotations

        return objects
    
    def labels_to_array(labels):
        return [t.description for t in labels]

    def cutout(path):
        img = cv.imread(path)
        x, y, _ = img.shape
        objs = localize_objects(path)
        ver = objs[0].bounding_poly.normalized_vertices[:]
        x_b = (int(ver[0].x * x), int(ver[1].x * x))
        y_b = (int(ver[1].y * y), int(ver[2].y * y))
        return cutout, img[x_b[0]:x_b[1], y_b[0]:y_b[1]]
  
    def compute(path):
        labels = labels_to_array(detect_labels(path))
        bbox, cut_img = cutout(path)
        return labels, bbox, cut_img
    
    a, b, c = compute('pictures/sammy.jpeg')
    print("hello")
    print(a)
    return a


if __name__ == "__main__":
    with stub.run():
        print("hi")
        print(query.call())
