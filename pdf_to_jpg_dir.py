import argparse
import math
import os
import re
import shutil
from posixpath import join

from tqdm import tqdm

from pdf2image_with_logging import convert_from_path
from google.cloud import storage

parser = argparse.ArgumentParser()
parser.add_argument("--filepath", type=str, help="Path to local pdf file", required=True)
parser.add_argument("--bucket", type=str, help="Google storage bucket name", required=True)
parser.add_argument("--output-dir", type=str, help="(google storage) Path to output dir (defaults to book name)")


def convert_to_jpg(args):
    print("Converting file {} to jpg".format(args.filepath))
    path_book_name = os.path.splitext(args.filepath)[0]
    book_name = os.path.split(path_book_name)[-1]
    pages = convert_from_path(args.filepath, 500)   

    n = int(math.ceil(math.log(len(pages)) / math.log(10)))

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(args.bucket)

    gcs_dir = args.output_dir if args.output_dir else book_name

    for i, page in tqdm(enumerate(pages), desc="Uploading", total=len(pages)):
        number_str = "_{num:0{width}}.jpg".format(num=i+1, width=n)
        output_name = os.path.join("tmp_pdf_to_jpg", book_name + number_str)
        page.save(output_name, 'JPEG')

        gcs_path = join(gcs_dir, book_name + number_str)
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(output_name)


if __name__ == "__main__":
    args = parser.parse_args()
    os.mkdir("tmp_pdf_to_jpg")
    try:
        convert_to_jpg(args)
    except Exception as e:
        raise e
    finally:
        shutil.rmtree("tmp_pdf_to_jpg")
