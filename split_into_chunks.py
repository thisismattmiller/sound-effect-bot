from pydub import AudioSegment
import glob
import os
import multiprocessing
import tqdm

in_path = '/Volumes/AGENTCASHEW/sound-effects/'
out_path = '/Volumes/AGENTCASHEW/sound-effects-clips/'


def process_clip(wave_file_name):

  id = os.path.splitext(os.path.basename(wave_file_name))[0]
  if os.path.isdir(f"{out_path}{id}"):
    print('skip')
    return None
 

  wave = AudioSegment.from_wav(wave_file_name)

  clips = int((len(wave)/1000) / 5) -1

  clip_data = []
  for x in range(0,clips,1):
    # print(clips,x*5000,(x+1)*5000)
    clip_data.append(wave[x*5000:(x+1)*5000])


  # print(wave_file_name,len(clip_data))

  if len(clip_data) == 0:
    clip_data.append(wave[0:5000])

  os.makedirs(f"{out_path}{id}")

  for idx, c in enumerate(clip_data):
    c.export(f"{out_path}{id}/{idx}.mp3", format="mp3")

  return len(clip_data)



the_pool = multiprocessing.Pool(multiprocessing.cpu_count())

path, dirs, files = os.walk(in_path).__next__()


for result in tqdm.tqdm(the_pool.imap_unordered(process_clip, glob.iglob(in_path+'*.wav')), total=len(files)):  
  pass




  # break


