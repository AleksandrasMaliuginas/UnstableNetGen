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
import time
import multiprocessing as mp
ImageFile.LOAD_TRUNCATED_IMAGES = True
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "caching_allocator"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
class HIFIC:
    def __init__(self, img_path, output_path,log_path, compression_level):
        self.prepared='tobecompressed'
        if not os.path.exists(self.prepared):
            os.makedirs(self.prepared)
        self.img_path=img_path
        self.output_path=output_path
        self.logs=log_path
        self.tile_size = 2100
        if compression_level<1 or compression_level>3:
            compression_level=1
        self.weightpath=""
        if compression_level==1:
            self.weightpath='weights/hific_hi.pt'
        elif compression_level==2:
            self.weightpath='weights/hific_med.pt'
        elif compression_level==3:
            self.weightpath='weights/hific_low.pt'
        self.model, self.args = prepare_model(self.weightpath, self.logs) #output path is just to make a log
        
    def compress(self):
        #Checks every given image if it is the correct format and the size of the image, if its too large it iwll be split.
        #out_of_memory=4410000
        out_of_memory=4420000
        resolutions={}
        split_images=0
        for filename in os.listdir(self.img_path):
            file_path = os.path.join(self.img_path, filename)
            if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in ['.jpg', '.png']):
                with Image.open(file_path) as img:
                    width, height = img.size
                    if width*height>out_of_memory:
                        tilesize=self.tile_size
                        #Check if filter is larger than an image dimension
                        #if so set filter to smallest image dimension
                        if width<self.tile_size or height<self.tile_size:
                            tilesize=min(width,height)

                        #loop that checks if the remainder segments will overflow memory, and if so it lowers
                        #filter size.
                        bot_w=width
                        rig_h=height
                        bot_h=height- (height // tilesize)*tilesize
                        rig_w=width - (width // tilesize)*tilesize
                        while bot_w*bot_h>out_of_memory or rig_w*rig_h>out_of_memory:
                            tilesize-=50
                            bot_h=height-(height // tilesize)*tilesize
                            rig_w=width - (width // tilesize)*tilesize
                        resolutions[split_images] = (img.size, str(filename)[:-4]+'_compressed.png')
                        Image_splitter.split_image(file_path, self.prepared, tilesize, split_images)
                        split_images+=1
                    else:
                        shutil.copy(file_path, self.prepared)
        
        self.data_loader=prepare_dataloader(self.args, self.prepared, self.output_path)
        compress_and_save(self.model, self.args, self.data_loader, self.output_path)
        for file_name in os.listdir(self.prepared):
            file_path = os.path.join(self.prepared, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        with open('data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for key, (value1, value2) in resolutions.items():
                writer.writerow([key, value1, value2])
        return resolutions
    def get_bpp(self, image_dimensions, num_bytes):
        w, h = image_dimensions
        return num_bytes * 8 / (w * h)
    def decompress(self):
        processes=[]
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
        resolutions = {}
        with open('data.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                key = int(row[0])
                value1 = row[1]
                value2 = row[2]
                resolutions[key] = (value1, value2)


        output_path='outputimg'
        out_path = os.path.join(output_path, output_path)
        file_count=0
        tile_path = f"tile{file_count}_0_0"
        split_imgs=[]
        for root, dirs, files in os.walk(out_path):
            for file_name in files:
                if "_0_0" in file_name:
                    file_count+=1

        for i in range(file_count):
            img_gatherer=[]
            horizontal=0
            vertical=0
            more_tiles=1
            while more_tiles:
                tile_path = f"tile{i}_{horizontal}_{0}_compressed.png"
                img_path = os.path.join(out_path, tile_path)   
                if os.path.exists(img_path):
                    more_vertical=1
                    v=0
                    while more_vertical:
                        tile_path = f"tile{i}_{horizontal}_{v}_compressed.png"
                        
                        img_path = os.path.join(out_path, tile_path)   
                        if os.path.exists(img_path): 
                            img_gatherer.append(img_path)
                            if v>vertical:
                                vertical=v 
                            v+=1
                        else: 
                            more_vertical=0
                            break
                    horizontal+=1
                else:
                    more_tiles=0
                    break
            resolution, filename=resolutions[i]
            parts = resolution.split(',')
            height= int(parts[1][:-1])
            width = int(parts[0][1:])
            tempimg=Image.open(img_gatherer[0])
            tilesize, notused=tempimg.size
            #img_name=os.path.join(out_path, f"img{i}.png")
            img_name=os.path.join(out_path, filename)
            if (vertical+1)*tilesize==height:
                vertical+=1
            if horizontal*tilesize>width:
                horizontal-=1
 
            start=time.time()
            #Image_splitter.merge_images(tiles=img_gatherer, num_tiles_horizontal=horizontal, 
            #                            num_tiles_vertical=vertical, output_path=img_name, final_res=[width, height])
            p=mp.Process(target=Image_splitter.merge_images, args=(img_gatherer, horizontal, vertical, img_name, [width, height]))
            processes.append(p)
            p.start()
            stop=time.time()
            print("merging",stop-start)
        # List all files in the folder
        for p in processes:
            p.join()
        files = os.listdir(self.output_path)
        for file_name in files:
            if file_name.endswith(".hfc"):
                file_path = os.path.join(self.output_path, file_name)
                os.remove(file_path)
        files = os.listdir(out_path)
        for file_name in files:
            if file_name.startswith("tile"):
                file_path = os.path.join(out_path, file_name)
                os.remove(file_path)
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

start=time.time()
resolutions=mycompressor.compress()
stop=time.time()
print("compresison time",stop-start)

#The other will use decompress

start=time.time()
mycompressor.decompress()
stop=time.time()
print("decompresison time",stop-start)
#When a new model is to be used, use del to remove the previous one from memory
del mycompressor