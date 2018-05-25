from pydub import AudioSegment
import glob
import os
import multiprocessing
import tqdm
from matplotlib import pyplot as plot
import numpy as np
import json

in_path = '/Volumes/AGENTCASHEW/sound-effects-clips/'


def create_wavedata(wave_dir_path):

  # print(wave_dir_path)

  id = os.path.splitext(os.path.basename(wave_dir_path))[0]
  # if os.path.exists(f"{in_path}{id}/meta.json"):
  #   return None
 
  metadata = {
    'id' : id,
    'segments' : {}
  }

  for file in glob.iglob(wave_dir_path+'/*.mp3'):
    segment = os.path.splitext(os.path.basename(file))[0]

    try:
      audio = AudioSegment.from_file(file)
      data = np.fromstring(audio._data, np.int16)
      fs = audio.frame_rate
    except:
      print('error with ffmpeg on',wave_dir_path,file)
      continue

    try:
      BARS = 100
      BAR_HEIGHT = 60
      LINE_WIDTH = 5

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

      ratio_array = []
      max_array_ints = []
      max_array = list(max_array)
      for item in max_array:
        max_array_ints.append(int(item))
        ratio_array.append("{0:0.1f}".format(item/line_ratio))


      metadata['segments'][segment] = {"id":segment,'values':max_array_ints,'values_ratio':ratio_array,'start':int(max_array_ints[0]),'end':int(max_array_ints[-1]),'start_ratio':ratio_array[0],'end_ratio':ratio_array[-1]}
    except:
      print('error calculating on',wave_dir_path,file)
      continue

    # print(max_array)
    # print(ratio_array)
    # print(ratio_array[0],ratio_array[-1])
  # print(metadata)
  # print('----------')
  if len(metadata['segments']) == 0:
    return None

  return json.dumps(metadata) + '\n'

the_pool = multiprocessing.Pool(multiprocessing.cpu_count())


total_files = 0
for f in glob.iglob(in_path+'*'):
  total_files+=1


data = []
with open('waveform_data.json','w') as out:
  for result in tqdm.tqdm(the_pool.imap_unordered(create_wavedata, glob.iglob(in_path+'*')), total=total_files):  
    
    if result is not None:
      out.write(result)



out.close()


