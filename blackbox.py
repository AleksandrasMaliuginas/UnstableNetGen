import torch
import numpy as np
import os
import glob
import collections
from PIL import Image
from compress import prepare_model, prepare_dataloader, compress_and_save, load_and_decompress
import shutil
import Image_splitter
class HIFIC:
    def __init__(self, img_path, output_path,log_path, compression_level):
        self.prepared='tobecompressed'
        if not os.path.exists(self.prepared):
            os.makedirs(self.prepared)
        self.img_path=img_path
        self.output_path=output_path
        self.logs=log_path
        self.tile_size = 1900
        if compression_level>0 and compression_level<3:
            self.weights=compression_level
        else: self.weights=1
        self.weightpath=""
        if self.weights==0:
            #no model just move images directly to output
            shutil.copy(self.img_path, self.output_path)
        elif self.weights==1:
            self.weightpath='weights/hific_hi.pt'
        elif self.weights==2:
            self.weightpath='weights/hific_med.pt'
        elif self.weights==3:
            self.weightpath='weights/hific_low.pt'
        print("hello")
        self.model, self.args = prepare_model(self.weightpath, self.logs) #output path is just to make a log
        
    def compress(self):
        #Checks every given image if it is the correct format and the size of the image, if its too large it iwll be split.
        resolutions={}
        split_images=0
        for filename in os.listdir(self.img_path):
            file_path = os.path.join(self.img_path, filename)
            if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in ['.jpg', '.png']):
                with Image.open(file_path) as img:
                    width, height = img.size
                    if width*height>3700000:
                        resolutions[split_images] = img.size
                        Image_splitter.split_image(file_path, self.prepared, self.tile_size, split_images)
                        split_images+=1
                    else:
                        shutil.copy(file_path, self.prepared)
        self.data_loader=prepare_dataloader(self.args, self.prepared, self.output_path)
        compress_and_save(self.model, self.args, self.data_loader, self.output_path)
        for file_name in os.listdir(self.prepared):
            file_path = os.path.join(self.prepared, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return resolutions
    def get_bpp(self, image_dimensions, num_bytes):
        w, h = image_dimensions
        return num_bytes * 8 / (w * h)
    def decompress(self, resolutions):
        File = collections.namedtuple('File', ['output_path', 'compressed_path',
                                       'num_bytes', 'bpp'])
        all_outputs = []

        for compressed_file in glob.glob(os.path.join(self.output_path, '*.hfc')):
            file_name, _ = os.path.splitext(compressed_file)
            output_path = os.path.join(self.output_path, f'{file_name}.png')

            # Model decode
            reconstruction = load_and_decompress(self.model, compressed_file, output_path)
            
            all_outputs.append(File(output_path=self.output_path,
                                    compressed_path=compressed_file,
                                    num_bytes=os.path.getsize(compressed_file),
                                    bpp=self.get_bpp(Image.open(output_path).size, os.path.getsize(compressed_file))))
        #Check for how many split images there are:
        output_path='outputimg'
        out_path = os.path.join(output_path, output_path)
        file_count=0
        tile_path = f"tile{file_count}_0_0"
        split_imgs=[]
        for root, dirs, files in os.walk(out_path):
            for file_name in files:
                if file_name.startswith(tile_path):
                    file_count+=1
                    tile_path = f"tile{file_count}_0_0"
                    split_imgs.append(file_name)

        for i in range(len(split_imgs)):
            img_gatherer=[]
            horizontal=0
            vertical=0
            for w in range(10):
                horizontal_flag=0
                for h in range(10):
                    tile_path = f"tile{i}_{w}_{h}_compressed.png"
                    img_path = os.path.join(out_path, tile_path)   
                    if os.path.exists(img_path): 
                        img_gatherer.append(img_path)
                        if h>vertical:
                            vertical=h 
                        horizontal_flag+=1
                    else:
                        break
                if horizontal_flag>0:
                    horizontal+=1
            resolution=resolutions[i]
            img_name=os.path.join(out_path, f"img{i}.png")
            Image_splitter.merge_images(tiles=img_gatherer, num_tiles_horizontal=horizontal-1, num_tiles_vertical=vertical, output_path=img_name, final_res=resolution)
#print(os.system("nvidia-smi")) #I dont know why but sometimes its necessary to run this.
#A new objects needs to be instantiated each time we need a different compression model, which takes a few seconds, so should be limited.
#Because of how big the models are, system memory cannot fit more than one (from my tests)
#Both sides need to instantiate the same model
device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
mycompressor=HIFIC(img_path='pepeimg',output_path='outputimg',log_path='logs', compression_level=1) 
#mycompressor1=HIFIC(img_path='pepeimg',output_path='outputimg',log_path='logs', compression_level=2) 
#mycompressor2=HIFIC(img_path='pepeimg',output_path='outputimg',log_path='logs', compression_level=3) 
#mycompressor1.model.to('cpu')
#mycompressor2.model.to('cpu')
#One side will use compress
resolutions=mycompressor.compress()
#The other will use decompress
mycompressor.decompress(resolutions)
#When a new model is to be used, use del to remove the previous one from memory
del mycompressor