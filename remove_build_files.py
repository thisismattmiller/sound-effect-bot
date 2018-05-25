import shutil
import os
import multiprocessing
import tqdm
import glob

in_path = '/Volumes/AGENTCASHEW/sound-effects-output/'

def delete_files(wave_file_name):


  shutil.rmtree(wave_file_name+'/gif_frames/')
  shutil.rmtree(wave_file_name+'/waveform/')
  os.remove(wave_file_name+'/audio.mp3')

the_pool = multiprocessing.Pool(8)

path, dirs, files = os.walk(in_path).__next__()

for result in tqdm.tqdm(the_pool.imap_unordered(delete_files, glob.iglob(in_path+'*')), total=len(files)):  
  pass



