#####################################################################
# dataLoader.py
#
# Dev. Dongwon Paek
# Description: Dataloader util source
#####################################################################

import h5py
import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torchvision import transforms


class Hdf5Dataset(Dataset):
    def __init__(self, data_path, x_key, y_key):
        data_file = h5py.File(data_path, 'r')
        self.x = data_file['train'][x_key]
        self.y = data_file['train']
        self.N = self.x.shape[0]

        # transform data
        self.transform = transforms.Compose(
            [transforms.ToTensor(),
             transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
        )

    def __len__(self):
        return self.N

    def __getitem__(self, index):
        image = self.x[index]
        label = self.y[index]
        return self.transform(image), torch.from_numpy(label).long()


def get_loader(data_path, x_key, y_key, batch_size, mode='train'):
    dataset = Hdf5Dataset(data_path, x_key, y_key)

    shuffle = False
    if mode == 'train':
        shuffle = True

    data_loader = DataLoader(dataset=dataset,
                             batch_size=batch_size,
                             shuffle=shuffle)

    return data_loader

def load_dataset_train():
    data_path = './train/'
    train_dataset = torchvision.datasets.ImageFolder(
        root=data_path,
        transform=torchvision.transforms.ToTensor()
    )
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        num_workers=NUM_WORKERS,
        shuffle=True
    )
    return train_loader

def load_dataset_test():
    data_path = './validation/'
    test_dataset = torchvision.datasets.ImageFolder(
        root=data_path,
        transform=torchvision.transforms.ToTensor()
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        num_workers=NUM_WORKERS,
        shuffle=True
    )
    return test_loader