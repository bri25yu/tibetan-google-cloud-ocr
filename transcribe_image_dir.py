import argparse
import os

from tqdm import tqdm

from google.cloud import storage
from google.cloud import vision


parser = argparse.ArgumentParser()
parser.add_argument("--filepath", type=str, help="(google storage) Path to input dir of images", required=True)
parser.add_argument("--output-dir", type=str, help="(local) Path to output dir (defaults to current directory)")
parser.add_argument("--bucket", type=str, help="Google storage bucket name", required=True)

def detect_document_tibetan(args):
    """Detects text in all images in a folder located in Google Cloud Storage.
    """
    book_name = os.path.split(args.filepath)[-1]
    folder_name = os.path.splitext(book_name)[0]
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(args.bucket)
    blob_list = sorted([blob.name for blob in bucket.list_blobs(prefix=folder_name+"/")])

    outputs = []

    for name in tqdm(blob_list, desc="Running document text detection"):
        gcs_uri = "gs://" + args.bucket + "/" + name
        client = vision.ImageAnnotatorClient()
        image = vision.Image()
        image_context = vision.ImageContext(language_hints=["bo"])
        image.source.image_uri = gcs_uri

        response = client.document_text_detection(image=image, image_context=image_context)
        text = response.full_text_annotation.text
        outputs.append(text)

    output_name = os.path.join(args.output_dir, book_name+".txt") if args.output_dir else book_name+".txt"

    print("Writing output file to: {}".format(output_name))
    with open(output_name, "w", encoding="utf-8") as f:
        f.write("".join(outputs))


if __name__ == "__main__":
    args = parser.parse_args()
    detect_document_tibetan(args)
