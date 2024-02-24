import os, io
from PIL import Image

IMAGE_TO_PATH = {0: "../dataset/test-pepe.png"}


def imageKey_to_path(image_key: int) -> str:
    # Can be used to get any image from dataset directory
    return IMAGE_TO_PATH.get(image_key)


def imageToBytes(image_key: int, format: str = "png") -> bytes:

    image_path = imageKey_to_path(image_key)

    if not image_path:
        raise Exception(f"No image found with key ${image_key}")

    img = Image.open(image_path, mode="r")
    io_bytes = io.BytesIO()

    img.save(io_bytes, format)
    return io_bytes.getvalue()


def bytesToImage(image_data: bytes) -> Image:
    io_bytes = io.BytesIO(image_data)

    return Image.open(io_bytes)


if __name__ == "__main__":
    b = imageToBytes(0)
    img = bytesToImage(b)
