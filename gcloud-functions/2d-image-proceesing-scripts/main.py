# [START functions_labeling_setup]
import base64
import json
import os

from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud import vision

vision_client = vision.ImageAnnotatorClient()
publisher = pubsub_v1.PublisherClient()
storage_client = storage.Client()

project_id = os.environ["GCP_PROJECT"]
# [END functions_labeling_setup]

# [START functions_detect_labels]
def process_image(file, context):
    """Cloud Function triggered by Cloud Storage when a file is changed.
    Args:
        file (dict): Metadata of the changed file, provided by the triggering
                                 Cloud Storage event.
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to stdout and Stackdriver Logging
    """
    bucket = validate_message(file, "bucket")
    name = validate_message(file, "name")

    detect_text(bucket, name)

    print("File {} processed.".format(file["name"]))



def detect_text(bucket, filename):
    print("trying to identify object {}".format(filename))

    futures = []

    image = vision.Image(
        source=vision.ImageSource(gcs_image_uri=f"gs://{bucket}/{filename}")
    )
    image_labeling_response = vision_client.label_detection(image=image)
    labels = image_labeling_response.text_annotations

    if len(labels) > 0:
        text = labels[0].description
    else:
        text = ""
    print("Extracted annotation {} of image ({} chars).".format(text, len(text)))

    # Submit a message to the bus for each target language

    topic_name = os.environ["RESULT_TOPIC"]
    message = {
        "text": text,
        "filename": filename,
    }
    message_data = json.dumps(message).encode("utf-8")
    topic_path = publisher.topic_path(project_id, topic_name)
    future = publisher.publish(topic_path, data=message_data)
    futures.append(future)
    for future in futures:
        future.result()
# [END functions_labeling_setup]

# [START message_validatation_helper]
def validate_message(message, param):
    var = message.get(param)
    if not var:
        raise ValueError(
            "{} is not provided. Make sure you have \
                          property {} in the request".format(
                param, param
            )
        )
    return var


# [END message_validatation_helper]

# [START functions_save_labels]
def save_result(event, context):
    if event.get("data"):
        message_data = base64.b64decode(event["data"]).decode("utf-8")
        message = json.loads(message_data)
    else:
        raise ValueError("Data sector is missing in the Pub/Sub message.")

    text = validate_message(message, "text")
    filename = validate_message(message, "filename")

    print("Received request to save file {}.".format(filename))

    bucket_name = os.environ["RESULT_BUCKET"]
    result_filename = "{}.txt".format(filename)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(result_filename)

    print("Saving result to {} in bucket {}.".format(result_filename, bucket_name))

    blob.upload_from_string(text)

    print("File saved.")
# [END functions_save_labels]