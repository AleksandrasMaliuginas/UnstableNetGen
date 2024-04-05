from PIL import Image
import os

def split_image(image_path,out_path='', tile_size=1900, split_number=0):
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        print("Error: File not found.")
        return
    
    width, height = image.size
    num_tiles_horizontal = width // tile_size
    num_tiles_vertical = height // tile_size
    tiles = []

    for i in range(num_tiles_horizontal):
        for j in range(num_tiles_vertical):
            left = i * tile_size
            upper = j * tile_size
            right = (i + 1) * tile_size
            lower = (j + 1) * tile_size
            tile = image.crop((left, upper, right, lower))
            tile_path = f"tile{split_number}_{i}_{j}.jpg"   
            tile_path = os.path.join(out_path, tile_path)
            tile.save(tile_path)
            tiles.append(tile_path)
    if height>num_tiles_vertical*tile_size:
        #Getting the remainder on the bottom
        left=0
        right=width
        upper=num_tiles_vertical*tile_size
        lower=height
        if lower-upper<100:
            lower+=100
        tile = image.crop((left, upper, right, lower))
        tile_path = f"tile{split_number}_{num_tiles_horizontal-1}_{num_tiles_vertical}.jpg"
        tile_path = os.path.join(out_path, tile_path)
        tile.save(tile_path)
        tiles.append(tile_path)
    if width>num_tiles_horizontal*tile_size:
        #Getting the remainder on the right
        left=num_tiles_horizontal*tile_size
        upper=0
        right=width
        if right-left<100:
            right+=100
        lower=num_tiles_vertical*tile_size
        tile = image.crop((left, upper, right, lower))
        tile_path = f"tile{split_number}_{num_tiles_horizontal}_0.jpg"
        tile_path = os.path.join(out_path, tile_path)
        tile.save(tile_path)
        tiles.append(tile_path)
    
    return tiles, num_tiles_horizontal, num_tiles_vertical

def merge_images(tiles, num_tiles_horizontal, num_tiles_vertical, output_path, final_res):
    tile_size = Image.open(tiles[0]).size[0]
    #width = (num_tiles_horizontal+1) * tile_size
    #height = (num_tiles_vertical+1) * tile_size
    width, height = final_res
    new_image = Image.new("RGB", (width, height))
 
    for i in range(num_tiles_horizontal):
        for j in range(num_tiles_vertical):
            index = i * num_tiles_vertical + j
            if (index)>len(tiles)-1:
                break
            tile = Image.open(tiles[index])
            new_image.paste(tile, (i * tile_size, j * tile_size))
    if height>num_tiles_vertical*tile_size:
        index+=1
        tile = Image.open(tiles[index])
        new_image.paste(tile, (0, num_tiles_vertical*tile_size))
    if width>num_tiles_horizontal*tile_size:
        index+=1
        tile = Image.open(tiles[index])
        new_image.paste(tile, (num_tiles_horizontal*tile_size, 0))
    new_image.save(output_path)
    print(f"Image reassembled and saved at {output_path}")