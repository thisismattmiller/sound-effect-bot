import glob
import os
import multiprocessing
import tqdm
import json
from textgenrnn import textgenrnn

in_path = '/Volumes/AGENTCASHEW/sound-effects-output/'

def create_title(wave_file_name):

  print(wave_file_name)
  meta = json.load(open(wave_file_name+'/meta.json'))

  if 'title' in meta:
    return None

  textgen = textgenrnn()
  textgen.train_from_file(f"{wave_file_name}/titles.txt",num_epochs=5)

  title = textgen.generate(return_as_list=True)[0]
  
  while len(title) > 200:
    title = textgen.generate(return_as_list=True)[0]

  
  meta['title'] = title
  print(meta)
  print(wave_file_name+'/meta.json')
  json.dump(meta,open(wave_file_name+'/meta.json','w'),indent=2)

  return None

the_pool = multiprocessing.Pool(8)

path, dirs, files = os.walk(in_path).__next__()

for result in tqdm.tqdm(the_pool.imap_unordered(create_title, glob.iglob(in_path+'*')), total=len(files)):  
  pass



