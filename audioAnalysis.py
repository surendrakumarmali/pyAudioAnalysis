import sys, os, audioop, numpy, glob,  scipy, subprocess, wave, cPickle, threading, shutil, ntpath
import matplotlib.pyplot as plt
import audioFeatureExtraction as aF	
import audioTrainTest as aT
import audioSegmentation as aS
import audioVisualization as aV
import audioBasicIO
import utilities as uT
import scipy.io.wavfile as wavfile
import  matplotlib.patches


def main(argv):
	if argv[1] == "-dirMp3toWAV":				# convert mp3 to wav (batch)
		if len(argv)==5:			
			path = argv[2]
			if argv[3] not in ["8000", "16000", "32000", "44100"]:
				print "Error. Unsupported sampling rate (must be: 8000, 16000, 32000 or 44100)."; return
			if argv[4] not in ["1","2"]:
				print "Error. Number of output channels must be 1 or 2"; return
			if not os.path.isdir(path):
				raise Exception("Input path not found!")
			useMp3TagsAsNames = True
			audioBasicIO.convertDirMP3ToWav(path, int(argv[3]), int(argv[4]), useMp3TagsAsNames)
		else:
			print "Error.\nSyntax: " + argv[0] + " -dirMp3toWAV <dirName> <sampling Freq> <numOfChannels>"

	elif argv[1] == "-featureExtractionFile":		# short-term and mid-term feature extraction to files (csv and numpy)
		if len(argv)==7:
			wavFileName = argv[2]
			if not os.path.isfile(wavFileName):
				raise Exception("Input audio file not found!")
			if not (uT.isNum(argv[3]) and uT.isNum(argv[4]) and uT.isNum(argv[5]) and uT.isNum(argv[6])):
				raise Exception("Mid-term and short-term window sizes and steps must be numbers!")
			mtWin = float(argv[3])
			mtStep = float(argv[4])
			stWin = float(argv[5])
			stStep = float(argv[6])
			outFile = wavFileName
			aF.mtFeatureExtractionToFile(wavFileName, mtWin, mtStep, stWin, stStep, outFile, True, True, True)
		else:
			print "Error.\nSyntax: " + argv[0] + " -featureExtractionFile <wavFileName> <mtWin> <mtStep> <stWin> <stStep>"

	elif argv[1] == "-beatExtraction":
		if len(argv)==4:
			wavFileName = argv[2]
			if not os.path.isfile(wavFileName):
				raise Exception("Input audio file not found!")
			if not (uT.isNum(argv[3])):
				raise Exception("PLOT must be either 0 or 1")
			if not ( (int(argv[3]) == 0) or (int(argv[3]) == 1) ):
				raise Exception("PLOT must be either 0 or 1")

			[Fs, x] = audioBasicIO.readAudioFile(wavFileName);
			F = aF.stFeatureExtraction(x, Fs, 0.050*Fs, 0.050*Fs);
			BPM, ratio = aF.beatExtraction(F, 0.050, int(argv[3])==1)
			print "Beat: {0:d} bpm ".format(int(BPM))
			print "Ratio: {0:.2f} ".format(ratio)
		else:
			print "Error.\nSyntax: " + argv[0] + " -beatExtraction <wavFileName> <PLOT (0 or 1)>"


	elif argv[1] == '-featureExtractionDir':	# same as -featureExtractionFile, in a batch mode (i.e. for each WAV file in the provided path)
		if len(argv)==7:
			path = argv[2]
			if not os.path.isdir(path):
				raise Exception("Input path not found!")
			if not (uT.isNum(argv[3]) and uT.isNum(argv[4]) and uT.isNum(argv[5]) and uT.isNum(argv[6])):
				raise Exception("Mid-term and short-term window sizes and steps must be numbers!")
			mtWin = float(argv[3])
			mtStep = float(argv[4])
			stWin = float(argv[5])
			stStep = float(argv[6])
			aF.mtFeatureExtractionToFileDir(path, mtWin, mtStep, stWin, stStep, True, True, True)
		else:
			print "Error.\nSyntax: " + argv[0] + " -featureExtractionDir <path> <mtWin> <mtStep> <stWin> <stStep>"

	elif argv[1] == '-featureVisualizationDir':	# visualize the content relationships between recordings stored in a folder
		if len(argv)==3:
			if not os.path.isdir(argv[2]):
				raise Exception("Input folder not found!")
			aV.visualizeFeaturesFolder(argv[2], "pca", "")

	elif argv[1] == '-fileSpectrogram':		# show spectogram of a sound stored in a file
			if len(argv)==3:
				wavFileName = argv[2]		
				if not os.path.isfile(wavFileName):
					raise Exception("Input audio file not found!")
				[Fs, x] = audioBasicIO.readAudioFile(wavFileName)
				x = audioBasicIO.stereo2mono(x)
				specgram, TimeAxis, FreqAxis = aF.stSpectogram(x, Fs, round(Fs*0.040), round(Fs*0.040), True)
			else:
				print "Error.\nSyntax: " + argv[0] + " -fileSpectrogram <fileName>"

	elif argv[1] == '-fileChromagram':		# show spectogram of a sound stored in a file
			if len(argv)==3:
				wavFileName = argv[2]		
				if not os.path.isfile(wavFileName):
					raise Exception("Input audio file not found!")
				[Fs, x] = audioBasicIO.readAudioFile(wavFileName)
				x = audioBasicIO.stereo2mono(x)
				specgram, TimeAxis, FreqAxis = aF.stChromagram(x, Fs, round(Fs*0.040), round(Fs*0.040), True)
			else:
				print "Error.\nSyntax: " + argv[0] + " -fileSpectrogram <fileName>"


	elif argv[1] == "-trainClassifier": 		# Segment classifier training (OK)
			if len(argv)>6: 
				method = argv[2]
				beatFeatures = (int(argv[3])==1)
				listOfDirs = argv[4:len(argv)-1]
				modelName = argv[-1]			
				aT.featureAndTrain(listOfDirs, 1, 1, aT.shortTermWindow, aT.shortTermStep, method.lower(), modelName, computeBEAT = beatFeatures)
			else:
				print "Error.\nSyntax: " + argv[0] + " -trainClassifier <method(svm or knn)> <beat features> <directory 1> <directory 2> ... <directory N> <modelName>"

	elif argv[1] == "-trainRegression": 		# Segment regression model
			if len(argv)==6: 
				method = argv[2]
				beatFeatures = (int(argv[3])==1)
				dirName = argv[4]
				modelName = argv[5]			
				aT.featureAndTrainRegression(dirName, 1, 1, aT.shortTermWindow, aT.shortTermStep, method.lower(), modelName, computeBEAT = beatFeatures)
			else:
				print "Error.\nSyntax: " + argv[0] + " -trainRegression <method(svm or knn)> <beat features> <directory> <modelName>"

	elif argv[1] == "-classifyFile":		# Single File Classification (OK)
			if len(argv)==5: 
				modelType = argv[2]
				modelName = argv[3]
				inputFile = argv[4]

				if modelType not in ["svm", "knn"]:
					raise Exception("ModelType has to be either svm or knn!")
				if not os.path.isfile(modelName):
					raise Exception("Input modelName not found!")
				if not os.path.isfile(inputFile):
					raise Exception("Input audio file not found!")

				[Result, P, classNames] = aT.fileClassification(inputFile, modelName, modelType)
				print "{0:s}\t{1:s}".format("Class","Probability")
				for i,c in enumerate(classNames):
					print "{0:s}\t{1:.2f}".format(c,P[i])
				print "Winner class: " + classNames[int(Result)]
			else:
				print "Error.\nSyntax: " + argv[0] + " -classifyFile <method(svm or knn)> <modelName> <fileName>"

	elif argv[1] == "-regressionFile":		# Single File Classification (OK)
			if len(argv)==5: 
				modelType = argv[2]
				modelName = argv[3]
				inputFile = argv[4]

				if modelType not in ["svm", "knn"]:
					raise Exception("ModelType has to be either svm or knn!")
				if not os.path.isfile(inputFile):
					raise Exception("Input audio file not found!")

				R, regressionNames = aT.fileRegression(inputFile, modelName, modelType)
				for i in range(len(R)):
					print "{0:s}\t{1:.3f}".format(regressionNames[i], R[i])
				
				#print "{0:s}\t{1:.2f}".format(c,P[i])

			else:
				print "Error.\nSyntax: " + argv[0] + " -regressionFile <method(svm or knn)> <modelName> <fileName>"

	elif argv[1] == "-classifyFolder": 			# Directory classification (Ok)
			if len(argv)==6 or len(argv)==5: 
				modelType = argv[2]
				modelName = argv[3]
				inputFolder = argv[4]
				if len(argv)==6:
					outputMode = argv[5]
				else:
					outputMode = "2"

				if modelType not in ["svm", "knn"]:
					raise Exception("ModelType has to be either svm or knn!")
				if outputMode not in ["0","1","2"]:
					raise Exception("outputMode has to be 0, 1 or 2")
				if not os.path.isfile(modelName):
					raise Exception("Input modelName not found!")
				if not os.path.isdir(inputFolder):
					raise Exception("Input folder not found!")

				types = ('*.wav',)
				wavFilesList = []
				for files in types:
					wavFilesList.extend(glob.glob(os.path.join(inputFolder, files)))

				wavFilesList = sorted(wavFilesList)	
				Results = []
				for wavFile in wavFilesList:	
					[Result, P, classNames] = aT.fileClassification(wavFile, modelName, modelType)	
					Result = int(Result)
					Results.append(Result)
					if outputMode=="1":
						print "{0:s}\t{1:s}".format(wavFile,classNames[Result])
				Results = numpy.array(Results)
				[Histogram, _] = numpy.histogram(Results, bins=numpy.arange(len(classNames)+1))
				if outputMode!="1":
					for h in Histogram:
						print "{0:20d}".format(h),
				if outputMode=="1":
					for i,h in enumerate(Histogram):
						print "{0:20s}\t\t{1:d}".format(classNames[i], h)
			else:
				print "Error.\nSyntax: " + argv[0] + " -classifyFolder <method(svm or knn)> <modelName> <folderName> <outputMode(0 or 1)"

	elif argv[1] == "-regressionFolder": 			# Regression applied on the WAV files of a folder
			if len(argv)==5: 
				modelType = argv[2]
				modelName = argv[3]
				inputFolder = argv[4]

				if modelType not in ["svm", "knn"]:
					raise Exception("ModelType has to be either svm or knn!")
				if not os.path.isdir(inputFolder):
					raise Exception("Input folder not found!")

				types = ('*.wav',)
				wavFilesList = []
				for files in types:
					wavFilesList.extend(glob.glob(os.path.join(inputFolder, files)))

				wavFilesList = sorted(wavFilesList)	
				Results = []
				for wavFile in wavFilesList:	
					R, regressionNames = aT.fileRegression(wavFile, modelName, modelType)
					Results.append(R)
				Results = numpy.array(Results)
				for i, r in enumerate(regressionNames):
					[Histogram, bins] = numpy.histogram(Results[:, i])
					centers = (bins[0:-1] + bins[1::]) / 2.0
					plt.subplot(len(regressionNames), 1, i);
					plt.plot(centers, Histogram)
					plt.title(r)
				plt.show()
#					for h in Histogram:
#						print "{0:20d}".format(h),
#				if outputMode=="1":
#					for i,h in enumerate(Histogram):
#						print "{0:20s}\t\t{1:d}".format(classNames[i], h)
			else:
				print "Error.\nSyntax: " + argv[0] + " -regressionFolder <method(svm or knn)> <modelName> <folderName>"


	elif argv[1] == '-segmentClassifyFile':		# Segmentation-classification (OK)
		if (len(argv)==5):
			modelType = argv[2]
			modelName = argv[3]
			inputWavFile = argv[4]

			if modelType not in ["svm", "knn"]:
				raise Exception("ModelType has to be either svm or knn!")
			if not os.path.isfile(modelName):
				raise Exception("Input modelName not found!")
			if not os.path.isfile(inputWavFile):
				raise Exception("Input audio file not found!")

			[segs, classes] = aS.mtFileClassification(inputWavFile, modelName, modelType, True)
		else:
			print "Error.\nSyntax: " + argv[0] + " -segmentClassifyFile <method(svm or knn)> <modelName> <fileName>"

	elif argv[1] == '-speakerDiarization':		# speaker diarization (from file): TODO
			inputFile = argv[2]
			[Fs, x] = audioBasicIO.readAudioFile(inputFile)
			#speechLimits = aS.speechSegmentation(x, Fs, 2.0, 0.10, True)
			aS.speakerDiarization(x, Fs, 2.0, 0.1, int(argv[3]));
			#print speechLimits

	elif argv[1] == '-thumbnail':			# music thumbnailing (OK)
			if len(argv)==4:	
				inputFile = argv[2]
				stWindow = 1.0
				stStep = 1.0
				if not os.path.isfile(inputFile):
					raise Exception("Input audio file not found!")

				[Fs, x] = audioBasicIO.readAudioFile(inputFile)						# read file
				if Fs == -1:	# could not read file
					return
				try:
					thumbnailSize = float(argv[3])
				except ValueError:
					print "Thumbnail size must be a float (in seconds)"
					return 
				[A1, A2, B1, B2, Smatrix] = aS.musicThumbnailing(x, Fs, stWindow, stStep, thumbnailSize)	# find thumbnail endpoints			

				# write thumbnails to WAV files:
				thumbnailFileName1 = inputFile.replace(".wav","_thumb1.wav")
				thumbnailFileName2 = inputFile.replace(".wav","_thumb2.wav")
				wavfile.write(thumbnailFileName1, Fs, x[int(Fs*A1):int(Fs*A2)])
				wavfile.write(thumbnailFileName2, Fs, x[int(Fs*B1):int(Fs*B2)])
				print "1st thumbnail (stored in file {0:s}): {1:4.1f}sec -- {2:4.1f}sec".format(thumbnailFileName1, A1, A2)
				print "2nd thumbnail (stored in file {0:s}): {1:4.1f}sec -- {2:4.1f}sec".format(thumbnailFileName2, B1, B2)

				# Plot self-similarity matrix:
				fig = plt.figure()
				ax = fig.add_subplot(111, aspect='auto')
				plt.imshow(Smatrix)
				# Plot best-similarity diagonal:
				Xcenter = (A1/stStep + A2/stStep) / 2.0
				Ycenter = (B1/stStep + B2/stStep) / 2.0


				e1 = matplotlib.patches.Ellipse((Ycenter, Xcenter), thumbnailSize * 1.4, 3,
			             angle=45, linewidth=3, fill=False)
				ax.add_patch(e1)

				plt.plot([B1, Smatrix.shape[0]], [A1, A1], color='k', linestyle='--', linewidth=2)
				plt.plot([B2, Smatrix.shape[0]], [A2, A2], color='k', linestyle='--', linewidth=2)
				plt.plot([B1, B1], [A1, Smatrix.shape[0]], color='k', linestyle='--', linewidth=2)
				plt.plot([B2, B2], [A2, Smatrix.shape[0]], color='k', linestyle='--', linewidth=2)

				plt.xlim([0, Smatrix.shape[0]])
				plt.ylim([Smatrix.shape[1], 0])



				ax.yaxis.set_label_position("right")
				ax.yaxis.tick_right()


				plt.xlabel('frame no')
				plt.ylabel('frame no')
				plt.title('Self-similarity matrix')

				plt.show()

			else: 
				print "Error.\nSyntax: " + argv[0] + " -thumbnail <filename> <thumbnailsize(seconds)>"

if __name__ == '__main__':
	main(sys.argv)
