import numpy as np
import cv2 as cv

from pathlib import Path

import torch
import torch.utils.data

gpu = torch.cuda.is_available()
device = torch.device("cpu")

if gpu:
    print("use gpu")
    device = torch.device("cuda:0")

target_height = 512
target_width = 256
model_path = "./unet_mean_cpu.pth"

if gpu:
    model_path = "./unet_mean_gpu.pth"

# load pretrained model
model = torch.load(model_path)
net = model.to(device)

clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16))


class BoostNetChallgeDataset(torch.utils.data.Dataset):

    def __init__(self, names, transform=None):
        self.images = []
        self.labels = []

        for i, path in enumerate([names]):
            image_name = Path(path).name

            self.labels.append(image_name)
            origin_image = cv.imread(str(path), 0)
            image = np.zeros((target_height, target_width), np.uint8)
            cv.resize(clahe.apply(origin_image), (target_width, target_height), image)

            image = np.reshape(image, (1, image.shape[0], image.shape[1]))
            image_tensor = torch.from_numpy(image).float()

            self.images.append(image_tensor)

    def __getitem__(self, index):
        image = self.images[index]
        label = self.labels[index]
        return image, label

    def __len__(self):
        return len(self.images)


def prepare_dataset(img_path):
    target_data = BoostNetChallgeDataset(img_path)
    return torch.utils.data.DataLoader(target_data, batch_size=1, shuffle=True, num_workers=0)


def pred_landmark(img_path):
    for images, labels in prepare_dataset(img_path):
        batch, channel, height, width = images.shape
        ret = net(images.to(device))
        predict = ret[0]

        sample = images[0].numpy().squeeze(0)
        sample_BGR = cv.cvtColor(sample, cv.COLOR_GRAY2BGR)
        point_num = len(predict) // 2

        for j in range(point_num):
            cv.circle(sample_BGR, (int(predict[j] * width), int(predict[j + point_num] * height)), 2, (0, 0, 255))

        b, g, r = cv.split(sample_BGR)
        plt_img = cv.merge([b, g, r]).astype(np.int)

        return plt_img


if __name__ == "__main__":
    result = pred_landmark("./sample/sample_1.jpg")

    cv.imwrite("./result.jpg", result)
