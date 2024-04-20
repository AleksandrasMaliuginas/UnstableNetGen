import torch
from torchmetrics.image import StructuralSimilarityIndexMeasure
from torchmetrics.image import MultiScaleStructuralSimilarityIndexMeasure
from torchmetrics.image import  LearnedPerceptualImagePatchSimilarity
#from torchmetrics import SSIM
from PIL import Image
import torchvision.transforms as transforms
import numpy as np
import torchvision.transforms.functional as TF
import os
from PIL import ImageFile
import csv
ImageFile.LOAD_TRUNCATED_IMAGES = True
# Step 1: Open the image using PIL
#original_path = "pepeimg/arnold-schwarzenegger-2560x1440.jpg"
original_path="pepeimg"
#original = Image.open(original_path)

#compressed_path="outputimg/outputimg/arnold-schwarzenegger-2560x1440_compressed.png"
compressed_path="outputimg/outputimg"




SSIM=StructuralSimilarityIndexMeasure(data_range=1,).to('cuda')
MSSSIM= MultiScaleStructuralSimilarityIndexMeasure(data_range=1).to('cuda')
LPIPS = LearnedPerceptualImagePatchSimilarity().to('cuda')#data_range=1.0)

filecount=0
SSIM_sum=0
MSSSIM_sum=0
LPIPS_sum=0

for file_name in os.listdir(original_path):
    filecount+=1
    original = os.path.join(original_path, file_name)
    compressedname=str(file_name)[:-4]+'_compressed.png'
    compressed = os.path.join(compressed_path, compressedname)
    original =Image.open(original)
    compressed= Image.open(compressed)

    originalt=TF.to_tensor(original).unsqueeze(0).to('cuda')
    compressedt=TF.to_tensor(compressed).unsqueeze(0).to('cuda')
    original.close()
    compressed.close()
    
    SSIM_sum+=float(SSIM(originalt, compressedt).to('cpu'))
    MSSSIM_sum+=float(MSSSIM(originalt, compressedt).to('cpu'))
    LPIPS_sum+=float(LPIPS(originalt,compressedt).to('cpu'))
    
    del(originalt)
    del(compressedt)
    print(filecount)

SSIM_sum/=filecount
MSSSIM_sum/=filecount
LPIPS_sum/=filecount

print(SSIM_sum)
print(MSSSIM_sum)
print(LPIPS_sum)  



