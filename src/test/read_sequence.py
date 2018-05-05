import sys
sys.path.insert(0, '..')

from img import TiffSequence

# 4 images
path = [
    '../../tif/20170407054917_MSG2.tif',
    '../../tif/20170407055416_MSG2.tif',
    '../../tif/20170407055916_MSG2.tif',
    '../../tif/20170407060416_MSG2.tif'
]

sequence = TiffSequence(path)

print("Number of images into sequence:", sequence.size())

## { 0, 0, 1 }
print("{ ",
sequence.previous()[0],
sequence.current()[0],
sequence.nextone()[0],
" }")

sequence.shift_right() ## { 0, 1, 2 }
sequence.shift_right() ## { 1, 2, 3 }
sequence.shift_right() ## { 2, 3, 3 }

print("{ ",
sequence.previous()[0],
sequence.current()[0],
sequence.nextone()[0],
" }")

sequence.shift_left() ## { 1, 2, 3 }
sequence.shift_left() ## { 0, 1, 2 }
sequence.shift_left() ## { 0, 0, 1 }

print("{ ",
sequence.previous()[0],
sequence.current()[0],
sequence.nextone()[0],
" }")