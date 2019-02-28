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

class Mutation:
	def __init__(self, type, from_, to_):
		self.type = type
		self.from_ = from_
		self.to = to_

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

	def apply_mutation(self, mutation):
		if mutation.type == 'slide':
			new_slide_1 = Slide(mutation.from_.id, mutation.to.photos)
			new_slide_2 = Slide(mutation.to.id, mutation.from_.photos)

			for photo in new_slide_1.photos:
				photo.slide_id = new_slide_1.id

			for photo in new_slide_2.photos:
				photo.slide_id = new_slide_2.id

			self.slideshow[new_slide_1.id] = new_slide_1
			self.slideshow[new_slide_2.id] = new_slide_2
		else:
			slide_1 = self.slideshow[mutation.from_.slide_id]
			slide_2 = self.slideshow[mutation.to.slide_id]

			new_slide_1 = Slide(slide_1.id, [photo for photo in slide_1.photos if photo.id != mutation.from_.id] + [mutation.to])
			new_slide_2 = Slide(slide_2.id, [photo for photo in slide_2.photos if photo.id != mutation.to.id] + [mutation.from_])

			for photo in new_slide_1.photos:
				photo.slide_id = new_slide_1.id

			for photo in new_slide_2.photos:
				photo.slide_id = new_slide_2.id

			self.slideshow[new_slide_1.id] = new_slide_1
			self.slideshow[new_slide_2.id] = new_slide_2

	def mutate(self):
		photo1_idx = random.randint(0, len(self.collection) -1)
		photo1 = self.collection[photo1_idx]
		if photo1.is_horizontal:
			# swzp with other
			slide2_idx = random.randint(0, len(self.slideshow)-1)
			while slide2_idx == photo1.slide_id:
				slide2_idx = random.randint(0, len(self.slideshow)-1)

			return Mutation('slide', self.slideshow[photo1.slide_id], self.slideshow[slide2_idx])
		else:
			photo2_idx = random.randint(0, len(self.vert_photos) -1)
			photo2 = self.vert_photos[photo2_idx]
			
			if len(self.vert_photos) < 3:
				return

			while photo2.slide_id == photo1.slide_id :
				photo2_idx = random.randint(0, len(self.vert_photos) -1)
				photo2 = self.vert_photos[photo2_idx]

			return Mutation('photo', photo1, photo2)

	def score_diff(self, mutation):
		if mutation.type == 'slide':
			slide1 = mutation.from_
			slide2 = mutation.to
		else:
			slide1 = self.slideshow[mutation.from_.slide_id]
			slide2 = self.slideshow[mutation.to.slide_id]

		score_diff = 0
		if slide1.id > 0:
			score_diff -= self.compute_transition(self.slideshow[slide1.id - 1], slide1)
			score_diff += self.compute_transition(self.slideshow[slide1.id - 1], slide2)

		if slide2.id > 0:
			score_diff -= self.compute_transition(self.slideshow[slide2.id - 1], slide2)
			score_diff += self.compute_transition(self.slideshow[slide2.id - 1], slide1)

		if slide1.id < len(self.slideshow) - 1:
			score_diff -= self.compute_transition(slide1, self.slideshow[slide1.id + 1])
			score_diff += self.compute_transition(slide2, self.slideshow[slide1.id + 1])

		if slide2.id < len(self.slideshow) - 1:
			score_diff -= self.compute_transition(slide2, self.slideshow[slide2.id + 1])
			score_diff += self.compute_transition(slide1, self.slideshow[slide2.id + 1])

		return score_diff

	def compute_transition(self, slide1, slide2):
			score_intersect = len(slide1.tags.intersection(slide2.tags))
			score_diff_1 = sum([1 for tag in slide1.tags if tag not in slide2.tags])
			score_diff_2 = sum([1 for tag in slide2.tags if tag not in slide1.tags])
			logging.debug('score_intersect ' +str(score_intersect))
			logging.debug('score_diff_1 ' +str(score_diff_1))
			logging.debug('score_diff_2 ' + str(score_diff_2))

			return min(score_intersect, score_diff_1, score_diff_2)

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

	def process(self, iteration=1000):
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
			mutation = self.mutate()
			if not mutation:
				continue
			score_diff = self.score_diff(mutation)

			if score_diff > 0:
				self.apply_mutation(mutation)
				max_score = max_score + score_diff

		self.score = max_score

		# print(len(self.slideshow))
		# for slide in self.slideshow:
		# 	print(' '.join([str(photo.id) for photo in slide.photos]))

		

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
	plop.process(args.iteration)
	plop.print()

if __name__ == '__main__':
	run_extract()
	