from PIL import Image
import subprocess
import os

#Steps to take before running:
#Set TESSDATA_PREFIX to correct directory
#Put image and box files together in the same directory
#Label each corresponding file with the same filenames

CLEANED_DIR = 'cleaned'
BOX_DIR = 'box'
EXP_DIR = 'exp'

class TesseractTrainer():
	def __init__(self, languageName, fontName, directory='data'):
		self.languageName = languageName
		self.fontName = fontName
		self.directory = directory

	def runAll(self):
		os.chdir(self.directory)
		self.createDirectories()
		self.createFontProperties()
		prefixes = self.renameFiles()
		self.createTrainingFiles(prefixes)
		self.extractUnicode()
		self.runShapeClustering()
		self.runMfTraining()
		self.runCnTraining()
		self.createTessData()

	def createDirectories(self):
		if not os.path.exists(CLEANED_DIR):
			os.mkdir(CLEANED_DIR)
		if not os.path.exists(EXP_DIR):
			os.mkdir(EXP_DIR)

	def createFontProperties(self):
		with open(f'{EXP_DIR}/font_properties', 'w') as f:
			f.write('f{self.fontName} 0 0 0 0 0')

	def cleanImages(self):
		images_dir = 'images'
		print("CLEANING IMAGES...")
		for fileName in os.listdir(images_dir):
			root, ext = os.path.splitext(fileName)
			if ext in ['.jpg', '.jpeg', '.png']:
				image = Image.open(f'{images_dir}/{fileName}')
				#Set a threshold value for the image, and save
				image = image.point(lambda x: 0 if x<250 else 255)
				image.save(f'{CLEANED_DIR}/{root}.tiff')

	#Looks for box files, uses the box filename to find the corresponding
	#.tiff file. Renames all files with the appropriate "<language>.<font>.exp<N>" filename
	def renameFiles(self):
		file_prefixes = []
		for i, boxFile in enumerate([f for f in os.listdir(BOX_DIR) if f.endswith('.box')]):
			root, _ = os.path.splitext(boxFile)
			os.system(f'cp {CLEANED_DIR}/{root}.tiff {EXP_DIR}/{self.languageName}.{self.fontName}.exp{i}.tiff')
			os.system(f'cp {BOX_DIR}/{root}.box {EXP_DIR}/{self.languageName}.{self.fontName}.exp{i}.box')
			file_prefixes.append(f'{self.languageName}.{self.fontName}.exp{i}')

		return file_prefixes

	#Creates a training file for a single tiff/box pair
	def createTrainingFiles(self, prefixes):
		print("CREATING TRAINING DATA...")
		os.chdir(EXP_DIR)
		for prefix in prefixes:
			p = subprocess.Popen(["tesseract", prefix+".tiff", prefix, "nobatch", "box.train"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			returnValue = stdout_value = p.communicate()[1]
			returnValue = returnValue.decode("utf-8")
			print(prefix)
			print(returnValue)
			if "Empty page!!" in returnValue:
				print(returnValue)
				subprocess.call(["tesseract", "-psm", "7", prefix+".tiff", prefix, "nobatch", "box.train"])
		os.chdir('..')

	def extractUnicode(self):
		print("EXTRACTING UNICODE...")
		extractCommand = ['unicharset_extractor'] + [f for f in os.listdir(EXP_DIR) if f.endswith('.box')]
		os.chdir(EXP_DIR)
		p = subprocess.Popen(extractCommand)
		p.wait()
		os.chdir('..')

	def runShapeClustering(self):
		print("RUNNING SHAPE CLUSTERING...")
		#shapeclustering -F font_properties -U unicharset eng.captchaFont.exp0.tr...
		shapeCommand = ['shapeclustering', '-F', 'font_properties', '-U', 'unicharset']
		shapeCommand = shapeCommand + self.getTrainingFileList()
		os.chdir(EXP_DIR)
		p = subprocess.Popen(shapeCommand)
		p.wait()
		os.chdir('..')


	def runMfTraining(self):
		#mftraining -F font_properties -U unicharset eng.captchaFont.exp0.tr...
		print("RUNNING MF CLUSTERING...")
		mfCommand = ['mftraining', '-F', 'font_properties', '-U', 'unicharset']
		mfCommand = mfCommand + self.getTrainingFileList()
		os.chdir(EXP_DIR)
		p = subprocess.Popen(mfCommand)
		p.wait()
		os.chdir('..')

	def runCnTraining(self):
		#cntraining -F font_properties -U unicharset eng.captchaFont.exp0.tr...
		print('RUNNING MF CLUSTERING...')
		cnCommand = ['cntraining', '-F', 'font_properties', '-U', 'unicharset']
		cnCommand = cnCommand + self.getTrainingFileList()
		os.chdir(EXP_DIR)
		p = subprocess.Popen(cnCommand)
		p.wait()
		os.chdir('..')


	def createTessData(self):
		print("CREATING TESS DATA...")
		os.chdir(EXP_DIR)
		#Rename all files and run combine_tessdata <language>.
		os.rename('unicharset', self.languageName+'.unicharset')
		os.rename('shapetable', self.languageName+'.shapetable')
		os.rename('inttemp', self.languageName+'.inttemp')
		os.rename('normproto', self.languageName+'.normproto')
		os.rename('pffmtable', self.languageName+'.pffmtable')

		p = subprocess.Popen(['combine_tessdata', self.languageName+'.'])
		#mv captcha.traineddata $TESSDATA_PREFIX/captcha.traineddata 
		p.wait()
		os.chdir('..')


	#Retrieve a list of created training files
	def getTrainingFileList(self):
		return [f for f in os.listdir(EXP_DIR) if f.endswith('.tr')]

trainer = TesseractTrainer('captcha', 'captchaFont')
trainer.runAll()

