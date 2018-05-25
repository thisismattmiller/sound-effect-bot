import csv
import os.path
import os
import json
import tqdm
import secrets
import uuid
from pydub import AudioSegment
import multiprocessing
import tqdm


data_path = '/Volumes/AGENTCASHEW/sound-effects-clips/'

def roundtofive(x, base=5):
    return int(base * round(float(x)/base))

def round_wave_val(val):
	if val > 10000:
		val = round(val, -3)
	elif val > 1000:
		val = round(val, -2)	

	return val

def find_next_segment(end_val):

	try:
		end_val = round_wave_val(end_val)
		possible_starts = waveform_starts[str(end_val)]
		next_start = secrets.choice(possible_starts)
	except:
		return None

	return next_start


def build_narative_clip(index):
	id = secrets.choice(list(all_data.keys()))

	next_start = find_next_segment(all_data[id]['segments']['0']['end_minus_500'])
	chain = [next_start]

	number_of_segments = 14
	overlap_milli = 500

	for x in range(1,number_of_segments):

		id = next_start['id']
		segment_id = next_start['s']

		next_end_val = all_data[id]['segments'][segment_id]['end_minus_500']
		next_start = find_next_segment(next_end_val)
		if next_start == None:
			break
		chain.append(next_start)

	if len(chain) <number_of_segments:
		return None



	audio_out = AudioSegment.silent(duration=number_of_segments*1000*5-(number_of_segments*overlap_milli))
	titles = []
	timestamps={}
	for idx, data in enumerate(chain):

		titles.append(data['t']+'\n')
		timestamps[idx*(5000-overlap_milli)]=data['t']
		tmp = AudioSegment.from_mp3(f"{data_path}{data['id']}/{data['s']}.mp3")
		audio_out = audio_out.overlay(tmp, position=idx*(5000-overlap_milli))

	audio_out=audio_out.fade_in(2000).fade_out(5000)
	# audio_out.export(f"audio.mp3", format="mp3")
	return {'audio':audio_out,'type':'narrative','titles':titles,'timestamps':timestamps, 'length':len(audio_out)}

def build_overlap_clip(index):
	id = secrets.choice(list(waveform_avgs.keys()))
	if len(waveform_avgs[id]) < 24:
		return None

	base_layer = []
	for x in range(1,13):
		base_layer.append(secrets.choice(waveform_avgs[id]))

	layover_layer = []
	for x in range(1,13):
		layover_layer.append(secrets.choice(waveform_avgs[id]))

	print(len(base_layer))
	print(len(layover_layer))

	timestamps= {}
	audio_out = AudioSegment.silent(duration=60*1000)

	titles = []
	for idx, data in enumerate(base_layer):	
		titles.append(data['t']+'\n')
		tmp = AudioSegment.from_mp3(f"{data_path}{data['id']}/{data['s']}.mp3")
		audio_out = audio_out.overlay(tmp, position=idx*5000)

		timestamps[idx*5000]=data['t']


	for idx, data in enumerate(layover_layer):
		titles.append(data['t']+'\n')
		tmp = AudioSegment.from_mp3(f"{data_path}{data['id']}/{data['s']}.mp3")
		tmp = tmp.fade_in(1000).fade_out(1000)
		audio_out = audio_out.overlay(tmp, position=(idx*5000)+2500)
		timestamps[(idx*5000)+2500]=data['t']

	audio_out=audio_out.fade_in(2000).fade_out(3000)

	return {'audio':audio_out,'type':'overlay','titles':titles,'timestamps':timestamps, 'length':len(audio_out)}

waveform_starts = json.load(open('waveform_data_starts.json'))
waveform_ends = json.load(open('waveform_data_ends.json'))
waveform_ends_minus_500 = json.load(open('waveform_data_ends_minus_500.json'))
waveform_avgs = json.load(open('waveform_data_avgs.json'))


metadata = {}
with open('bbc_sound_effect_source.csv') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
  	row = dict(row)
  	metadata[row['location'].replace('.wav','')] = row


all_data = {}
with open('waveform_data.json') as jsondata:
# with open('tmp') as jsondata:	
	for l in tqdm.tqdm(jsondata,total=16010):
		l = json.loads(l)

		for s in l['segments']:
			l['segments'][s]['end_minus_500'] = l['segments'][s]['values'][-10]
			if l['segments'][s]['end_minus_500'] > 10000:
				l['segments'][s]['end_minus_500'] = round(l['segments'][s]['end_minus_500'], -3)
			elif l['segments'][s]['end_minus_500'] > 1000:
				l['segments'][s]['end_minus_500'] = round(l['segments'][s]['end_minus_500'], -2)
			elif l['segments'][s]['end_minus_500'] > 100:
				l['segments'][s]['end_minus_500'] = round(l['segments'][s]['end_minus_500'], -1)
			else:
				l['segments'][s]['end_minus_500'] = roundtofive(l['segments'][s]['end_minus_500'])

		all_data[l['id']] = l



the_pool = multiprocessing.Pool(8)


for r in tqdm.tqdm(the_pool.imap_unordered(build_overlap_clip, range(0,20)), total=len(range(0,10))):

	if r is None:
		continue

	uuid_str = str(uuid.uuid4())
	os.mkdir('/Volumes/AGENTCASHEW/sound-effects-output/'+uuid_str)

	r['audio'].export(f"/Volumes/AGENTCASHEW/sound-effects-output/{uuid_str}/audio.mp3", format="mp3")


	with open('/Volumes/AGENTCASHEW/sound-effects-output/'+uuid_str+'/titles.txt','w') as out:
		out.write(''.join(r['titles']))

	del r['audio']
	json.dump(r,open('/Volumes/AGENTCASHEW/sound-effects-output/'+uuid_str+'/meta.json','w'),indent=2)


for r in tqdm.tqdm(the_pool.imap_unordered(build_narative_clip, range(0,20)), total=len(range(0,10))):

	if r is None:
		continue

	uuid_str = str(uuid.uuid4())
	os.mkdir('/Volumes/AGENTCASHEW/sound-effects-output/'+uuid_str)

	r['audio'].export(f"/Volumes/AGENTCASHEW/sound-effects-output/{uuid_str}/audio.mp3", format="mp3")


	with open('/Volumes/AGENTCASHEW/sound-effects-output/'+uuid_str+'/titles.txt','w') as out:
		out.write(''.join(r['titles']))

	del r['audio']
	json.dump(r,open('/Volumes/AGENTCASHEW/sound-effects-output/'+uuid_str+'/meta.json','w'),indent=2)




# for x in range(0,10):
# 	if x % 2 == 0:
# 		r = build_overlap_clip()
# 	else:
# 		r = build_narative_clip()



