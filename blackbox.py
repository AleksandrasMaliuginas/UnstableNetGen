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
        for filename in os.listdir(self.img_path):
            file_path = os.path.join(self.img_path, filename)
            if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in ['.jpg', '.png']):
                with Image.open(file_path) as img:
                    width, height = img.size
                    if width*height>3700000:
                        Image_splitter.split_image(file_path, self.prepared, self.tile_size)
                    else:
                        shutil.copy(file_path, self.prepared)
        self.data_loader=prepare_dataloader(self.args, self.prepared, self.output_path)
        compress_and_save(self.model, self.args, self.data_loader, self.output_path)
    def get_bpp(self, image_dimensions, num_bytes):
        w, h = image_dimensions
        return num_bytes * 8 / (w * h)
    def decompress(self):
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
mycompressor.compress()
#The other will use decompress
mycompressor.decompress()
#When a new model is to be used, use del to remove the previous one from memory
del mycompressor