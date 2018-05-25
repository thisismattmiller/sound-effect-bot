from pydub import AudioSegment
import glob
from PIL import Image, ImageDraw
import os
import multiprocessing
import tqdm
import json
import numpy as np

in_path = '/Volumes/AGENTCASHEW/sound-effects-output/'

def process_clip(wave_file_name):

  print(wave_file_name)
  if os.path.isdir(wave_file_name+'/waveform'):
    return None

  meta = json.load(open(wave_file_name+'/meta.json'))
  print(meta)

  audio = AudioSegment.from_file(wave_file_name+'/audio.mp3')
  data = np.fromstring(audio._data, np.int16)
  fs = audio.frame_rate

  BARS = 600
  BAR_HEIGHT = 120
  LINE_WIDTH = 1

  length = len(data)
  RATIO = length/BARS

  count = 0
  maximum_item = 0
  max_array = []
  highest_line = 0

  for d in data:
    if count < RATIO:
      count = count + 1

      if abs(d) > maximum_item:
        maximum_item = abs(d)
    else:
      max_array.append(maximum_item)

      if maximum_item > highest_line:
        highest_line = maximum_item

      maximum_item = 0
      count = 1

  line_ratio = highest_line/BAR_HEIGHT
  print(meta['type'],len(max_array))

  # each tick is x number of milliseconds
  tick = int(meta['length']/len(max_array))
  print('tick is',tick)


  im = Image.new('RGBA', (BARS * LINE_WIDTH, BAR_HEIGHT), (255, 255, 255, 0))
  draw = ImageDraw.Draw(im)

  current_x = 1
  for item in max_array:
    item_height = item/line_ratio
    current_y = (BAR_HEIGHT - item_height)/2
    draw.line((current_x, current_y, current_x, current_y + item_height), fill=(158, 158, 158), width=0)
    current_x = current_x + LINE_WIDTH

  os.mkdir(wave_file_name+'/waveform')


  current_x = 1
  for idx, item in enumerate(max_array):
    item_height = item/line_ratio
    current_y = (BAR_HEIGHT - item_height)/2
    draw.line((current_x, current_y, current_x, current_y + item_height), fill=(255, 87, 34), width=0)
    current_x = current_x + LINE_WIDTH

    im.save(f"{wave_file_name}/waveform/{idx}.png")


the_pool = multiprocessing.Pool(8)

path, dirs, files = os.walk(in_path).__next__()

for result in tqdm.tqdm(the_pool.imap_unordered(process_clip, glob.iglob(in_path+'*')), total=len(files)):  
  pass



