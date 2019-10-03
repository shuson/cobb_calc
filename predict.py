import os
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

#clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16))


class BoostNetChallgeDataset(torch.utils.data.Dataset):

    def __init__(self, paths, transform=None):
        self.images = []
        self.labels = []

        for i, path in enumerate(paths):
            image_name = Path(path).name

            self.labels.append(image_name)
            origin_image = cv.imread(str(path), 0)
            image = np.zeros((target_height, target_width), np.uint8)
            cv.resize(origin_image, (target_width, target_height), image)

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
    target_data = BoostNetChallgeDataset([img_path])  # only 1 image is in the prediction dataset
    return torch.utils.data.DataLoader(target_data, batch_size=1, shuffle=False, num_workers=0)


def pred_landmark(img_path):
    for images, labels in prepare_dataset(img_path):
        batch, channel, height, width = images.shape
        ret = net(images.to(device))

        predict = ret[0]

        sample = images[0].numpy().squeeze(0)
        sample_BGR = cv.cvtColor(sample, cv.COLOR_GRAY2BGR)
        point_num = len(predict) // 2

        for j in range(point_num):
            cv.circle(sample_BGR, (int(predict[j] * width), int(predict[j + point_num] * height)), 3, (0, 0, 255))

        b, g, r = cv.split(sample_BGR)
        plt_img = cv.merge([b, g, r]).astype(np.int)

        return predict, plt_img


def _lines_degree(l1, l2):
    l1 = np.array(l1)
    l2 = np.array(l2)
    cosang = np.dot(l1, l2)
    sinang = np.linalg.det([l1, l2])
    angle = np.math.atan2(sinang, cosang)
    return round(abs(np.degrees(angle)), 2)


def pred_angle(landmarks):
    # 1-68 values are X-axis, 69-136 values are Y-axis
    landmarks = landmarks.tolist()
    n = len(landmarks) // 2
    points = [(landmarks[i], landmarks[n+i]) for i in range(n)]
    lines = [(round(points[i+1][0]-points[i][0], 6), round(points[i+1][1]-points[i][1], 6)) for i in range(0, n, 2)]

    angles = []
    m = n // 2
    for i in range(m):
        for j in range(i+1, m-i):
            l1 = lines[i]
            l2 = lines[j+i]
            angle = _lines_degree(l1, l2)
            angles.append((i, j, angle))

    angs = [a[2] for a in angles]
    return angles[angs.index(max(angs))]


def predict(img_path):
    landmarks, masked_img = pred_landmark(img_path)
    angle = pred_angle(landmarks)

    return angle, masked_img


if __name__ == "__main__":
    from datetime import datetime
    OUTPUT_FOLDER = "./result"

    angle, result = predict("./sample/sample3.jpg")
    now = datetime.now()
    output_path = os.path.join(OUTPUT_FOLDER, "output_" + str(datetime.timestamp(now)) + ".jpg")
    cv.imwrite(output_path, result)
    print(angle)
