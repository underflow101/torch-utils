import numpy as np
import h5py

dir = '/home/bearpaek/data/datasets/lplSmall/train/train_data.hdf5'
#f = h5py.File(dir, 'w')
with h5py.File(dir, 'w') as f:
    g = f.create_group('train')
    others = g.create_group('others')
    phoneWithHand = g.create_group('phoneWithHand')
    sleep = g.create_group('sleep')
    writing = g.create_group('writing')

    others.create_dataset('/home/bearpaek/data/datasets/lplSmall/train/others', (2000, 224, 224, 3), dtype='float32')
    phoneWithHand.create_dataset('/home/bearpaek/data/datasets/lplSmall/train/phoneWithHand', (2000, 224, 224, 3), dtype='float32')
    sleep.create_dataset('/home/bearpaek/data/datasets/lplSmall/train/sleep', (2000, 224, 224, 3), dtype='float32')
    writing.create_dataset('/home/bearpaek/data/datasets/lplSmall/train/writing', (2000, 224, 224, 3), dtype='float32')



#with h5py.File(dir, 'w') as f:
#    f.create_dataset('/home/bearpaek/data/datasets/lplSmall/train', (8000, 224, 224, 3), dtype='float32')