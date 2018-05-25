import csv
import os.path
import json
import tqdm
import numpy
import math


def roundtofive(x, base=5):
    return int(base * round(float(x)/base))

waveform_starts = {}
waveform_ends = {}
waveform_ends_minus_500 = {}
waveform_avgs = {}
metadata = {}
with open('bbc_sound_effect_source.csv') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
  	row = dict(row)
  	metadata[row['location'].replace('.wav','')] = row


with open('waveform_data.json') as jsondata:
	for l in tqdm.tqdm(jsondata,total=16010):
		l = json.loads(l)

		for s in l['segments']:
			if l['id'] not in metadata:
				continue


			l['segments'][s]['avg'] = int(numpy.mean(l['segments'][s]['values']))
			if l['segments'][s]['avg'] > 10000:
				l['segments'][s]['avg'] = round(l['segments'][s]['avg'], -3)
			elif l['segments'][s]['avg'] > 1000:
				l['segments'][s]['avg'] = round(l['segments'][s]['avg'], -2)
			elif l['segments'][s]['avg'] > 100:
				l['segments'][s]['avg'] = round(l['segments'][s]['avg'], -1)
			else:
				l['segments'][s]['avg'] = roundtofive(l['segments'][s]['avg'])


			if l['segments'][s]['start'] > 10000:
				l['segments'][s]['start'] = round(l['segments'][s]['start'], -3)
			elif l['segments'][s]['start'] > 1000:
				l['segments'][s]['start'] = round(l['segments'][s]['start'], -2)
			elif l['segments'][s]['start'] > 100:
				l['segments'][s]['start'] = round(l['segments'][s]['start'], -1)
			else:
				l['segments'][s]['start'] = roundtofive(l['segments'][s]['start'])

			if l['segments'][s]['end'] > 10000:
				l['segments'][s]['end'] = round(l['segments'][s]['end'], -3)
			elif l['segments'][s]['end'] > 1000:
				l['segments'][s]['end'] = round(l['segments'][s]['end'], -2)
			elif l['segments'][s]['end'] > 100:
				l['segments'][s]['end'] = round(l['segments'][s]['end'], -1)
			else:
				l['segments'][s]['end'] = roundtofive(l['segments'][s]['end'])

			#over writing here
			l['segments'][s]['end_minus_500'] = l['segments'][s]['values'][-10]

			if l['segments'][s]['end_minus_500'] > 10000:
				l['segments'][s]['end_minus_500'] = round(l['segments'][s]['end_minus_500'], -3)
			elif l['segments'][s]['end_minus_500'] > 1000:
				l['segments'][s]['end_minus_500'] = round(l['segments'][s]['end_minus_500'], -2)
			elif l['segments'][s]['end_minus_500'] > 100:
				l['segments'][s]['end_minus_500'] = round(l['segments'][s]['end_minus_500'], -1)
			else:
				l['segments'][s]['end_minus_500'] = roundtofive(l['segments'][s]['end_minus_500'])

			if l['segments'][s]['start'] not in waveform_starts:
				waveform_starts[l['segments'][s]['start']] = []

			waveform_starts[l['segments'][s]['start']].append({'id':l['id'],'s':s, 't':metadata[l['id']]['description']})

			if l['segments'][s]['end'] not in waveform_ends:
				waveform_ends[l['segments'][s]['end']] = []

			waveform_ends[l['segments'][s]['end']].append({'id':l['id'],'s':s, 't':metadata[l['id']]['description']})


			if l['segments'][s]['end_minus_500'] not in waveform_ends_minus_500:
				waveform_ends_minus_500[l['segments'][s]['end_minus_500']] = []

			waveform_ends_minus_500[l['segments'][s]['end_minus_500']].append({'id':l['id'],'s':s, 't':metadata[l['id']]['description']})


			if l['segments'][s]['avg'] not in waveform_avgs:
				waveform_avgs[l['segments'][s]['avg']] = []

			waveform_avgs[l['segments'][s]['avg']].append({'id':l['id'],'s':s, 't':metadata[l['id']]['description']})





for x in waveform_starts:
	print(x, len(waveform_starts[x]))

json.dump(waveform_starts,open('waveform_data_starts.json','w'),indent=2)
json.dump(waveform_ends,open('waveform_data_ends.json','w'),indent=2)
json.dump(waveform_avgs,open('waveform_data_avgs.json','w'),indent=2)
json.dump(waveform_ends_minus_500,open('waveform_data_ends_minus_500.json','w'),indent=2)

