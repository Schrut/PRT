from img import TiffSequence

class Video():
    def __init__(self, sequence: :):


"""

TODO

        # Read first image to check shape
		# Meaning that the whole image sequence choosen
		# must has the same shape (width/height).
		tiff = Tiff(fnames[0])
		_h, _w = tiff.shape()
		
		# Path security check
		videopath = "../video/"
		if os.path.exists(videopath) is False:
			os.makedirs(videopath)

		# Create a VideoWirter:
		# output format .MKV
		# encoded using HFYU (Huffman Lossless Codec)
		# 25 frames/sec
		# Size( width, height )
		# False -> not a color video (only grey images here)
		video = cv2.VideoWriter(
			videopath+"video.mkv", 
			cv2.VideoWriter_fourcc('H','F','Y','U'), 
			25.0, 
			(_w, _h), 
			False
		)
		
		# If the VideoWriter creation failed, exit.
		# e.g.:
		# HFYU codec is not present at runtime on the machine.
		if video.isOpened() is False:
			print("Video [FAILED]")
			return

		# Remember that we read the first sequence image.
		# During the process, 16-bits greyscale images
		# are converted to 8-bits.
		video.write(tiff.to_8bits())
		fnames.pop(0)
		
		# Now read all the others.
		for fname in fnames:
			tiff = Tiff(fname)
			video.write(tiff.to_8bits())

		# "close" VideoWriter.
		video.release()
"""
