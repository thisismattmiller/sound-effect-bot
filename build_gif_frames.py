from pydub import AudioSegment
import glob
from PIL import Image, ImageDraw, ImageFont
import os
import multiprocessing
import tqdm
import json
import numpy as np

in_path = '/Volumes/AGENTCASHEW/sound-effects-output/'
font = ImageFont.truetype('NotoSans-Regular.ttf', 36)

def format_text(text,opacity=100):

  base = Image.new('RGBA', (640, 200), (245,245,245,255))
  txt = Image.new('RGBA', base.size, (255,255,255,0))
  draw = ImageDraw.Draw(txt)

  if font.getsize(text)[0] > 600:

    words = text.split(' ')
    lines = []
    line = ''
    for w in words:

      new_line = line + ' ' + w
      new_line = new_line.strip()

      if font.getsize(new_line)[0] > 600:
        lines.append(line)
        line = w
      else:
        line = line + ' ' + w
        line = line.strip()

    lines.append(line)


    margin_top = (200 - (len(lines) * 36)) /2
    for idx, line in enumerate(lines):
      lx,ly = font.getsize(line)

      margin_left = (640 - lx) / 2


      draw.text((margin_left, idx*36+margin_top), text=line, font=font, fill=(45, 52, 54,opacity))

    combined = Image.alpha_composite(base, txt) 

    

  else:
    text = text.strip()
    lx,ly = font.getsize(text)

    margin_left = (640 - lx) / 2
    margin_top = (200 - (1 * 36)) /2
    draw.text((margin_left, margin_top), text=text, font=font, fill=(45, 52, 54,opacity))
    combined = Image.alpha_composite(base, txt)     


  return combined





def process_clip(wave_file_name):

  print(wave_file_name)

  if not os.path.isdir(wave_file_name+'/waveform'):
    return None

  if os.path.isdir(wave_file_name+'/gif_frames'):
    return None

  meta = json.load(open(wave_file_name+'/meta.json'))

  print(meta)
  tick = int(meta['length']/600)


  frame_direction ={}

  for x in range(0,599):
    current_time = x * tick

    if x not in frame_direction:
      frame_direction[x] = None

    delete = []
    for t in meta['timestamps']:
      if current_time >= int(t):
        # print('Shuld show',t,meta['timestamps'][t])
        if x > 15:
          fadeOut = 255
          for i in range(15,1,-1):
            frame_direction[x-i] = {'action':'fadeout','amount':fadeOut}
            fadeOut=fadeOut-17

        fadeIn = 0
        for i in range(1,15):
          frame_direction[x] = {'action':'fadein','amount':fadeIn,'content':meta['timestamps'][t]}
          fadeIn+=17

        delete.append(t)
    
    for d in delete:
      del meta['timestamps'][d]

  
  os.mkdir(wave_file_name+'/gif_frames')

  last_text_image = None
  last_text_value = None
  for x in range(0,599):
    # print(os.path.isfile(f"{wave_file_name}/waveform/{x}.png"))    
    current_time = x * tick

    base = Image.new('RGB', (640, 420), (245,245,245,1))
    waveform = Image.open(f"{wave_file_name}/waveform/{x}.png")
    base.paste(waveform, (20,40),waveform)


    if frame_direction[x] == None:
      if last_text_image != None:
        base.paste(last_text_image, (0,150),last_text_image)
    else:
      if frame_direction[x]['action'] == 'fadein':
        last_text_image = format_text(frame_direction[x]['content'],frame_direction[x]['amount'])
        base.paste(last_text_image, (0,150),last_text_image)
        last_text_value = frame_direction[x]['content']
      if frame_direction[x]['action'] == 'fadeout':
        last_text_image = format_text(last_text_value,frame_direction[x]['amount'])
        base.paste(last_text_image, (0,150),last_text_image)

      # if frame_direction[x]['action'] == 'fadeout':
      #   # tmp_image = last_text_image.putalpha(frame_direction[x]['amount'])
      #   base.paste(last_text_image, (0,100),last_text_image)        




    base.save(f"{wave_file_name}/gif_frames/{str(x).zfill(3)}.png")

  rate = 599/(meta['length']/1000)
  # build the video
  # print(f"ffmpeg -r {rate} -i '{wave_file_name}/gif_frames/%03d.png' -vcodec mpeg4 -vb 15000k -y {wave_file_name}/video.mp4")
  os.system(f"ffmpeg -r {rate} -i '{wave_file_name}/gif_frames/%03d.png' -vcodec mpeg4 -vb 15000k -y {wave_file_name}/video.mp4")
  os.system(f"ffmpeg -i {wave_file_name}/audio.mp3 -i {wave_file_name}/video.mp4 {wave_file_name}/final.mp4")
# format_text('Stara Sladovna" restaurant',255)



the_pool = multiprocessing.Pool(8)

path, dirs, files = os.walk(in_path).__next__()

for result in tqdm.tqdm(the_pool.imap_unordered(process_clip, glob.iglob(in_path+'*')), total=len(files)):  
  pass



