import torch
import numpy as np
import os
import glob
import collections
from PIL import Image
from compress import prepare_model, prepare_dataloader, compress_and_save, load_and_decompress
import shutil
import Image_splitter
from PIL import ImageFile
import csv

resolutions = {}
with open('data.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        key = int(row[0])
        value1 = row[1]
        value2 = row[2]
        resolutions[key] = (value1, value2)
out_path='outputimg/outputimg'
file_count=0
for root, dirs, files in os.walk(out_path):
    for file_name in files:
        if "img" in file_name:
            file_count+=1
for i in range(file_count):
    resolution, filename=resolutions[i]
    old_file_path = os.path.join(out_path, 'img'+str(i)+'.png')
    new_file_path = os.path.join(out_path,filename)
    try:
        # Rename the file
        os.rename(old_file_path, new_file_path)
    except FileNotFoundError:
        print(f"File '{i}' not found.")

