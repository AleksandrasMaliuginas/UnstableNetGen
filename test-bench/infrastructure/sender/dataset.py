import os
import io
import json
from PIL import Image, ImageFile
from enum import Enum
from pathlib import Path
from typing import Callable, Tuple

ORIGINAL = "original"
COMPRESSED = "compressed"
ImageFile.LOAD_TRUNCATED_IMAGES = True

class Size(Enum):
    HD_1k = "1920x1080"
    HD_2k = "2560x1440"
    HD_4k = "3840x2160"
    HD_8k = "7680x4320"

class CompressionLevel(Enum):
    NONE = "uncompressed"
    LOW = "HiFiC low"
    MEDIUM = "HiFiC med"
    HIGH = "HiFiC high"


class Dataset:

    def __init__(self, datasetPath: Path):
        self.datasetPath = datasetPath
        self.buildIndex()

    def readAll(self, imageSize: Size, imageConsumer: Callable[[bytes], None], compression: CompressionLevel = CompressionLevel.NONE):
        # limit = 3

        for imageName in self.imageNames:
            path = Path(self.baseDatasetDirectory, f"{imageName}-{imageSize.value}.jpg")
            
            imageBytes = self.imageToBytes(path)

            if imageBytes:
                imageConsumer(imageBytes)

            # limit -= 1
            # if limit == 0:
            #     break
            

    @staticmethod
    def imageToBytes(image_path: Path) -> bytes | None:

        if not os.path.exists(image_path):
            print("Unknown file: ", image_path)
            return None

        image = Image.open(image_path, mode="r")

        return Dataset.imageToByteArray(image)
    
    @staticmethod
    def imageToByteArray(image: Image) -> bytes:
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        return imgByteArr.getvalue()

    def buildIndex(self):
        self.imageSizes = set()
        self.images = {}
        self.imageNames = set()

        originalImagePaths = Path(self.datasetPath, ORIGINAL).glob("*.*")

        for path in originalImagePaths:
            self.baseDatasetDirectory = "/".join(str(path).split("/")[:-1])

            filename = str(path).split("/")[-1]

            nameParts = filename.split("-")
            imageKey = "-".join(nameParts[0:-1])

            imageSize = nameParts[-1].split(".")[0]
            imageDimensions = [int(x) for x in imageSize.split("x")]
            # print(imageKey, imageSize, imageDimensions)

            self.imageNames.add(imageKey)

            self.imageSizes.add(imageSize)
            imageList: list = appendIfAbsent(self.images, imageKey, lambda key: [])
            imageList.append(filename)


def newImage(filename: str, imageSize: Tuple[int]):
    return {"filename": filename, "imageSize": imageSize}


def appendIfAbsent(targetDict: dict, entryKey: str, computeFunction: Callable[[str], dict]):
    if entryKey not in targetDict:
        targetDict[entryKey] = computeFunction(entryKey)

    return targetDict[entryKey]


if __name__ == "__main__":

    imageSupplier = Dataset()

    print(imageSupplier.imageSizes)
    output = json.dumps(imageSupplier.images, indent=2)
    print(output)
