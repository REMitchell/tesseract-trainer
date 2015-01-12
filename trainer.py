from PIL import Image
import subprocess
import os
import numpy
import time

#Steps to take before running:
#Set TESSDATA_PREFIX to correct directory
#Put image and box files together in the same directory
#Label each corresponding file with the same filenames

class TesseractTrainer():
	def __init__(self):
		self.languageName = "cpa"
		self.fontName = "captchaFont"
		self.directory = "/Users/ryan/Documents/newCaptchas"
		self.trainingList = None

	def main(self):
		global languageName
		global fontName
		global directory
		languageName = "cpa"
		fontName = "captchaFont"
		directory = "/Users/ryan/Documents/newCaptchas"

	def runAll(self):
		self.createFontFile()
		self.cleanImages()
		boxString = self.renameFiles()
		self.extractUnicode(boxString)
		#self.runShapeClustering()
		#self.runMftTraining()
		#self.runCntTraining()
		#self.createTessData()

	def cleanImages(self):
		global directory
		files = os.listdir(self.directory)

		for fileName in files:
			if fileName.endswith("jpg") or fileName.endswith("jpeg") or fileName.endswith("png"):
				image = Image.open(self.directory+"/"+fileName)
				#Set a threshold value for the image, and save
				image = image.point(lambda x: 0 if x<143 else 255)
				(root, ext) = os.path.splitext(fileName)

				newFilePath = root+".tiff"
				image.save(self.directory+"/"+newFilePath)

				#call tesseract to do OCR on the newly-created image
				#subprocess.call(["tesseract", newFilePath, "output"])


	#Looks for box files, uses the box filename to find the corresponding
	#.tiff file. Renames all files with the appropriate "<language>.<font>.exp<N>" filename
	def renameFiles(self):
		global languageName
		global fontName
		global directory

		files = os.listdir(self.directory)
		boxString = ""
		i = 0
		for fileName in files:
			if fileName.endswith(".box"):
				(root, ext) = os.path.splitext(fileName)
				print("Root is: "+root)
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
		global directory
		currentDir = os.getcwd()
		os.chdir(self.directory)
		p = subprocess.Popen(["tesseract", prefix+".tiff", prefix, "nobatch", "box.train"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		returnValue = stdout_value = p.communicate()[1]
		returnValue = returnValue.decode("utf-8")
		print("Return value: ")
		print(returnValue)
		if "Empty page!!" in returnValue:
			print("TRYING AGAIN")
			print("tesseract -psm 7 "+prefix+".tiff "+prefix+" nobatch box.train")
			os.chdir(self.directory)
			subprocess.call(["tesseract", "-psm", "7", prefix+".tiff", prefix, "nobatch", "box.train"])
		os.chdir(currentDir)


	def extractUnicode(self, boxString):
		global directory
		currentDir = os.getcwd()
		print("EXTRACTING UNICODE...")
		#print(boxString)
		boxList = boxString.split(" ")
		boxList.insert(0, "unicharset_extractor")
		boxList = [i for i in boxList if i != '']
		print(boxList)
		os.chdir(self.directory)
		p = subprocess.Popen(boxList)
		p.wait()
		os.chdir(currentDir)
		#subprocess.call(numpy.asarray(boxList))
		#time.sleep(5)

	def createFontFile(self):
		global fontName
		global directory
		currentDir = os.getcwd()
		os.chdir(self.directory)
		fname = self.directory+"/font_properties"
		with open(fname, 'w') as fout:
		    fout.write(self.fontName+" 0 0 0 0 0")
		os.chdir(currentDir)

	def runShapeClustering(self):
		#shapeclustering -F font_properties -U unicharset eng.captchaFont.exp0.tr...
		trainingList = self.getTrainingFileList()
		subprocess.call([""])
		print("Write me!")

	def runMftTraining(self):
		#mftraining -F font_properties -U unicharset eng.captchaFont.exp0.tr...
		print("Write me!")

	def runCntTraining(self):
		#cntraining -F font_properties -U unicharset eng.captchaFont.exp0.tr...
		print("Write me!")

	def createTessData(self):
		print("Write me!")

	#Retrieve a list of created training files, caches 
	#the list, so this only needs to be done once.
	def getTrainingFileList(self):
		global trainingList

		if trainingList is not None:
			return trainingList

		trainingList = ""

		files = os.listdir(directory)
		commandString = "unicharset_extractor"
		filesFound = False

		for fileName in files:
			if fileName.endswith(".tr"):
				filesFound = True
				filesFound += " "+fileName

		if not filesFound:
			trainingList = None

		return trainingList

#if __name__ == "__main__":
#  main()

trainer = TesseractTrainer()
trainer.runAll()

#Rename box file to tla.test_font.exp0.box
#Rename tif to tla.test_font.exp0.tif

#Run over each pair:
#tesseract tla.test_font.exp0.tif tla.test_font.exp0 nobatch box.train


#Finally:
#unicharset_extractor tla.test_font.exp0.box tla.test_font.exp1.box ... tla.test_font.exp31.box
#cleanFile("text_2.png", "text_2_clean.png")

#Open the data file
#outputFile = open("output.txt", 'r')

#print(outputFile.read())
#outputFile.close()
