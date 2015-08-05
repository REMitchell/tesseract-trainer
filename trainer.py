from PIL import Image
import subprocess
import os
import numpy

#Steps to take before running:
#Set TESSDATA_PREFIX to correct directory
#Put image and box files together in the same directory
#Label each corresponding file with the same filenames

class TesseractTrainer():
	def __init__(self):
		self.languageName = "eng"
		self.fontName = "captchaFont"
		self.directory = "/Users/ryan/Documents/tesseract-trainer/images"
		self.trainingList = None
		self.boxList = None


	def runAll(self):
		self.createFontFile()
		self.cleanImages()
		self.renameFiles()
		self.extractUnicode()
		self.runShapeClustering()
		self.runMfTraining()
		self.runCnTraining()
		self.createTessData()

	def cleanImages(self):
		print("CLEANING IMAGES...")
		files = os.listdir(self.directory)

		for fileName in files:
			if fileName.endswith("jpg") or fileName.endswith("jpeg") or fileName.endswith("png"):
				image = Image.open(self.directory+"/"+fileName)
				#Set a threshold value for the image, and save
				image = image.point(lambda x: 0 if x<250 else 255)
				(root, ext) = os.path.splitext(fileName)

				newFilePath = root+".tiff"
				image.save(self.directory+"/"+newFilePath)


	#Looks for box files, uses the box filename to find the corresponding
	#.tiff file. Renames all files with the appropriate "<language>.<font>.exp<N>" filename
	def renameFiles(self):
		files = os.listdir(self.directory)
		boxString = ""
		i = 0
		for fileName in files:
			if fileName.endswith(".box"):
				(root, ext) = os.path.splitext(fileName)
				tiffFile = self.languageName+"."+self.fontName+".exp"+str(i)+".tiff"
				boxFile = self.languageName+"."+self.fontName+".exp"+str(i)+".box"

				os.rename(self.directory+"/"+root+".tiff", self.directory+"/"+tiffFile)
				os.rename(self.directory+"/"+root+".box", self.directory+"/"+boxFile)
				boxString += " "+boxFile
				self.createTrainingFile(self.languageName+"."+self.fontName+".exp"+str(i))
				i += 1

		return boxString

	#Creates a training file for a single tiff/box pair
	#Called by renameFiles
	def createTrainingFile(self, prefix):
		print("CREATING TRAINING DATA...")
		currentDir = os.getcwd()
		os.chdir(self.directory)
		p = subprocess.Popen(["tesseract", prefix+".tiff", prefix, "nobatch", "box.train"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		returnValue = stdout_value = p.communicate()[1]
		returnValue = returnValue.decode("utf-8")
		if "Empty page!!" in returnValue:
			os.chdir(self.directory)
			subprocess.call(["tesseract", "-psm", "7", prefix+".tiff", prefix, "nobatch", "box.train"])
		os.chdir(currentDir)


	def extractUnicode(self):
		currentDir = os.getcwd()
		print("EXTRACTING UNICODE...")
		boxList = self.getBoxFileList()
		boxArr = boxList.split(" ")
		boxArr.insert(0, "unicharset_extractor")
		boxArr = [i for i in boxArr if i != '']
		os.chdir(self.directory)
		p = subprocess.Popen(boxArr)
		p.wait()
		os.chdir(currentDir)

	def createFontFile(self):
		currentDir = os.getcwd()
		os.chdir(self.directory)
		fname = self.directory+"/font_properties"
		with open(fname, 'w') as fout:
		    fout.write(self.fontName+" 0 0 0 0 0")
		os.chdir(currentDir)

	def runShapeClustering(self):
		print("RUNNING SHAPE CLUSTERING...")
		#shapeclustering -F font_properties -U unicharset eng.captchaFont.exp0.tr...
		self.getTrainingFileList()
		shapeCommand = self.trainingList.split(" ")
		shapeCommand.insert(0, "shapeclustering")
		shapeCommand.insert(1, "-F")
		shapeCommand.insert(2, "font_properties")
		shapeCommand.insert(3, "-U")
		shapeCommand.insert(4, "unicharset")
		shapeCommand = [i for i in shapeCommand if i != '']
		currentDir = os.getcwd()
		os.chdir(self.directory)
		p = subprocess.Popen(shapeCommand)
		p.wait()
		os.chdir(currentDir)


	def runMfTraining(self):
		#mftraining -F font_properties -U unicharset eng.captchaFont.exp0.tr...
		print("RUNNING MF CLUSTERING...")
		self.getTrainingFileList()
		mfCommand = self.trainingList.split(" ")
		mfCommand.insert(0, "mftraining")
		mfCommand.insert(1, "-F")
		mfCommand.insert(2, "font_properties")
		mfCommand.insert(3, "-U")
		mfCommand.insert(4, "unicharset")
		mfCommand = [i for i in mfCommand if i != '']

		currentDir = os.getcwd()
		os.chdir(self.directory)
		p = subprocess.Popen(mfCommand)
		p.wait()
		os.chdir(currentDir)

	def runCnTraining(self):
		#cntraining -F font_properties -U unicharset eng.captchaFont.exp0.tr...
		print("RUNNING MF CLUSTERING...")
		self.getTrainingFileList()
		cnCommand = self.trainingList.split(" ")
		cnCommand.insert(0, "cntraining")
		cnCommand.insert(1, "-F")
		cnCommand.insert(2, "font_properties")
		cnCommand.insert(3, "-U")
		cnCommand.insert(4, "unicharset")
		cnCommand = [i for i in cnCommand if i != '']

		currentDir = os.getcwd()
		os.chdir(self.directory)
		p = subprocess.Popen(cnCommand)
		p.wait()
		os.chdir(currentDir)


	def createTessData(self):
		print("CREATING TESS DATA...")
		#Rename all files and run combine_tessdata <language>.
		currentDir = os.getcwd()
		os.chdir(self.directory)
		os.rename("unicharset", self.languageName+".unicharset")
		os.rename("shapetable", self.languageName+".shapetable")
		os.rename("inttemp", self.languageName+".inttemp")
		os.rename("normproto", self.languageName+".normproto")
		os.rename("pffmtable", self.languageName+".pffmtable")

		p = subprocess.Popen(["combine_tessdata", self.languageName+"."])
		p.wait()
		os.chdir(currentDir)


	def getBoxFileList(self):
		if self.boxList is not None:
			return self.boxList
		self.boxList = ""
		files = os.listdir(self.directory)
		commandString = "unicharset_extractor"
		filesFound = False

		for fileName in files:
			if fileName.endswith(".box"):
				filesFound = True
				self.boxList += " "+fileName

		if not filesFound:
			self.boxList = None
		return self.boxList

	#Retrieve a list of created training files, caches 
	#the list, so this only needs to be done once.
	def getTrainingFileList(self):
		if self.trainingList is not None:
			return self.trainingList

		self.trainingList = ""

		files = os.listdir(self.directory)
		commandString = "unicharset_extractor"
		filesFound = False

		for fileName in files:
			if fileName.endswith(".tr"):
				filesFound = True
				self.trainingList += " "+fileName

		if not filesFound:
			self.trainingList = None
		return self.trainingList



trainer = TesseractTrainer()
trainer.runAll()

