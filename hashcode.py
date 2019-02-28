#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
	TODO : Description here
"""
__progname__ = "Google_Hash_Code"
__author__ = ""
__version__ = "0.0.1"
__status__ = "Development"


import logging
import argparse
import random
import copy

LOG_FORMAT = '[%(asctime)s]' + '[{}][{}][{}]'.format(__progname__, __version__, __status__) + ' %(message)s'
LOG_VERBOSITY = {
	'DEBUG' : logging.DEBUG,
	'INFO' : logging.INFO,
	'WARNING' : logging.WARNING,
	'ERROR' : logging.ERROR,
	'CRITICAL' : logging.CRITICAL,
}

class HashCode(object):
	"""docstring for Pizza"""
	def __init__(self, file):
		super(HashCode, self).__init__()
		self.file = file
		self.collection = []
		self.vert_photos = []
		self.slideshow = []

	def print(self):
		file_out_name = '{}-{}.out'.format(self.file, self.score)
		with open(file_out_name, 'w') as fout:
			fout.write(str(len(self.slideshow)))
			fout.write('\n')
			for slide in self.slideshow:
				fout.write(' '.join([str(photo.id) for photo in slide.photos]))
				fout.write('\n')


	def mutate(self):
		photo1_idx = random.randint(0, len(self.collection) -1)
		photo1 = self.collection[photo1_idx]
		if photo1.is_horizontal:
			# swzp with other
			slide2_idx = random.randint(0, len(self.slideshow)-1)
			while slide2_idx == photo1.slide_id:
				slide2_idx = random.randint(0, len(self.slideshow)-1)
			slide_2 = self.slideshow[slide2_idx]
			slide_1 = self.slideshow[photo1.slide_id]

			new_slide_1 = Slide(slide_1.id, slide_2.photos)
			new_slide_2 = Slide(slide_2.id, slide_1.photos)

			for photo in new_slide_1.photos:
				photo.slide_id = new_slide_1.id
			for photo in new_slide_2.photos:
				photo.slide_id = new_slide_2.id

			self.slideshow[new_slide_1.id] = new_slide_1
			self.slideshow[new_slide_2.id] = new_slide_2
		else:
			photo2_idx = random.randint(0, len(self.vert_photos) -1)
			photo2 = self.vert_photos[photo2_idx]
			
			if len(self.vert_photos) < 3:
				return

			while photo2.slide_id == photo1.slide_id :
				photo2_idx = random.randint(0, len(self.vert_photos) -1)
				photo2 = self.vert_photos[photo2_idx]

			slide1 = self.slideshow[photo1.slide_id]
			slide2 = self.slideshow[photo2.slide_id]

			newslide_1 = Slide(slide1.id, [photo for photo in slide1.photos if photo.id != photo1.id] + [photo2])
			newslide_2 = Slide(slide2.id, [photo for photo in slide2.photos if photo.id != photo2.id] + [photo1])

			photo2.slide_id = newslide_1.id
			photo1.slide_id = newslide_2.id

			self.slideshow[newslide_1.id] = newslide_1
			self.slideshow[newslide_2.id] = newslide_2

	def score(self):
		previous_tags = set()
		score = 0
		for slide in self.slideshow:
			score_intersect = len(previous_tags.intersection(slide.tags))
			score_diff_1 = sum([1 for tag in previous_tags if tag not in slide.tags])
			score_diff_2 = sum([1 for tag in slide.tags if tag not in previous_tags])
			logging.debug('score_intersect ' +str(score_intersect))
			logging.debug('score_diff_1 ' +str(score_diff_1))
			logging.debug('score_diff_2 ' + str(score_diff_2))

			score += min(score_intersect, score_diff_1, score_diff_2)
			previous_tags = slide.tags

		return score



	def process(self, iteration=100):
		logging.debug('Collection has {} photos'.format(len(self.collection)))

		curr_vert = None
		slide_id = 0
		for photo in self.collection:
			if photo.is_horizontal:
				self.slideshow.append(Slide(slide_id, [photo]))
				slide_id += 1
			elif curr_vert:
				self.slideshow.append(Slide(slide_id, [photo, curr_vert]))
				slide_id += 1
				curr_vert = None
			else:
				curr_vert = photo

		logging.debug('\n'.join([str(x) for x in self.slideshow]))


		# for slide in self.slideshow:
		# 	print(' '.join([str(photo.id) for photo in slide.photos]))
		# print('==============================')

		max_score = self.score()
		for i in range(1, iteration):
			before_mutate = copy.deepcopy(self)
			self.mutate()
			curr_score = self.score()
			if self.score() >= max_score:
				max_score = curr_score
			else:
				self.collection = before_mutate.collection
				self.vert_photos = before_mutate.vert_photos
				self.slideshow = before_mutate.slideshow
			# logging.debug('\n'.join([str(x) for x in self.slideshow]))
			# logging.debug('Score ===> {}'.format(self.score()))
		
		# logging.info('\n'.join([str(x) for x in self.slideshow]))
		# logging.info('==================> {}'.format(max_score))

		self.score = max_score
		logging.info('Having a score of : {}'.format(max_score))


	def parse(self):
		with open(self.file, 'r') as input_file:
			# Read first line
			nb_photos = input_file.readline().strip()
			self.nb_photos = int(nb_photos)

			# Go over the rest of the file
			photo_id = 0
			for line in input_file:
				line = line.strip()
				data = line.split(' ')
				position = data[0]
				nb_tags = int(data[1])
				tags = data[2:]
				# logging.debug('Photo {} is {} and has tags {}'.format(photo_id, position, tags))
				photo = Photo(photo_id, position, tags)
				self.collection.append(photo)
				if photo.is_vertical:
					self.vert_photos.append(photo)
				photo_id += 1

class Slide(object):
	"""docstring for Slide"""
	def __init__(self, id, photos):
		super(Slide, self).__init__()
		self.photos = photos
		self.tags = set()
		self.id = id
		for photo in self.photos:
			photo.slide_id = id
			for tag in photo.tags:
				self.tags.add(tag)

	def __str__(self):
		return 'Slide {} of len {} ({}) with tags {}'.format(self.id, len(self.photos), [x.id for x in self.photos], self.tags) 


class Photo(object):
	"""docstring for Photo"""
	def __init__(self, pid, position, tags):
		super(Photo, self).__init__()
		self.id = pid
		self.is_horizontal = True if position == 'H' else False 
		self.is_vertical = True if position == 'V' else False
		self.tags = tags

		self.slide_id = -1

	def is_in_slide(self):
		return self.slide_id != -1

	def __str__(self):
		return 'Photo {} is {} and has tags {}'.format(self.id, 'horizontal' if self.is_horizontal else 'vertical', self.tags)
		

def run_extract():
	# Handle arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--verbosity", help="increase output verbosity", choices = LOG_VERBOSITY)
	parser.add_argument("-i", "--input", required=True, help="input file")
	parser.add_argument("--iteration", type=int, default=10, help="input file")
	args = parser.parse_args()

	# configure logging
	logging.basicConfig(format=LOG_FORMAT, level=LOG_VERBOSITY.get(args.verbosity, 'INFO'), datefmt='%Y-%m-%d %I:%M:%S')

	plop = HashCode(args.input)
	plop.parse()
	plop.process(iteration=args.iteration)
	plop.print()

if __name__ == '__main__':
	run_extract()
	