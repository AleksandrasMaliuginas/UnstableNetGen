import csv
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
baseDatasetDirectory = ""
compressionToImages = {}


class Resolution(Enum):
    S_256 = "256x256"
    S_480 = "640x480"
    S_720 = "1280x720"
    HD_1k = "1920x1080"
    HD_2k = "2560x1440"
    HD_4k = "3840x2160"
    HD_8k = "7680x4320"


class CompressionLevel(Enum):
    NONE = "original"
    LOW = "HiFiC low"
    MEDIUM = "HiFiC medium"
    HIGH = "HiFiC high"


class DatasetImage:

    def __init__(self, filename: str, compression: CompressionLevel = CompressionLevel.NONE):
        self.filename = filename
        self.compression = compression

        self.__readFiles()

    def __readFiles(self):
        global baseDatasetDirectory
        global compressionToImages

        self.imageTiles = []
        self.totalImageSize = 0

        fileDir = Path(baseDatasetDirectory, self.compression.value)

        if self.compression == CompressionLevel.NONE:
            path = Path(fileDir, f"{self.filename}.jpg")
            self.__readFile(path)
            return

        # Compressed  less than 2k
        if not Resolution.HD_4k.value in self.filename and not Resolution.HD_8k.value in self.filename:
            path = Path(fileDir, f"{self.filename}_compressed.hfc")
            self.__readFile(path)
            return

        # Compressed high resolution
        imageId = compressionToImages[self.compression][self.filename]

        for path in Path(fileDir).glob(f"tile{imageId}*.*"):
            self.__readFile(path)

        return

    def __readFile(self, path: Path | str):
        with open(path, "rb") as file:
            fileBytes = file.read()
            self.imageTiles.append((file.name.split("/")[-1], fileBytes))
            self.totalImageSize += len(fileBytes)


class Dataset:

    def __init__(self, datasetPath: Path):
        self.datasetPath = datasetPath
        self.buildIndex()
        self.setCompressedResolver()

    def readAll(
        self,
        imageConsumer: Callable[[DatasetImage], None],
        resolution: Resolution = None,
        compression: CompressionLevel = CompressionLevel.NONE,
    ):
        # limit = 3

        for filename in self.images:

            if resolution != None and not resolution.value in filename:
                continue

            datasetImage = DatasetImage(filename, compression)
            imageConsumer(datasetImage)

            # limit -= 1
            # if limit == 0:
            #     break

    def buildIndex(self):
        global baseDatasetDirectory
        baseDatasetDirectory = self.datasetPath

        self.images = set()
        self.imageSizes = set()

        originalImagePaths = Path(self.datasetPath, "original").glob("*.*")

        for path in originalImagePaths:
            self.baseDatasetDirectory = "/".join(str(path).split("/")[:-1])

            filename = str(path).split("/")[-1]
            filenameWithoutExtension = filename.split(".")[0]

            self.images.add(filenameWithoutExtension)

    def setCompressedResolver(self):
        global baseDatasetDirectory
        global compressionToImages

        compressionToImages[CompressionLevel.LOW] = {}
        compressionToImages[CompressionLevel.MEDIUM] = {}
        compressionToImages[CompressionLevel.HIGH] = {}

        for compressionLevel in CompressionLevel:
            if compressionLevel == CompressionLevel.NONE:
                continue

            imageToId = compressionToImages[compressionLevel]

            with open(Path(baseDatasetDirectory, compressionLevel.value, "data.csv"), newline="") as file:
                reader = csv.reader(file, delimiter=",", quotechar='"')
                for row in reader:
                    imageId = row[0]
                    imageFilename = row[-1].replace("_compressed.png", "")
                    imageToId[imageFilename] = int(imageId)

        # print(compressionToImages)

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


def appendIfAbsent(targetDict: dict, entryKey: str, computeFunction: Callable[[str], dict]):
    if entryKey not in targetDict:
        targetDict[entryKey] = computeFunction(entryKey)

    return targetDict[entryKey]
