import argparse
import torch
import torchvision.transforms as transforms
import munch
import yaml
from trainer_dataset import build_dataset_val
from train_utils import *
import logging
import importlib
import random
import os
from model_utils import *
from tqdm import tqdm
import matplotlib.pyplot as plt
import warnings
import cv2
import numpy as np
import time
warnings.filterwarnings("ignore")

def normalize_pointcloud(pc):
    """ Normalize a point cloud to zero mean and unit sphere. """
    pc = pc - pc.mean(0)
    scale = np.linalg.norm(pc, axis=1).max()
    pc = pc / scale
    return pc

def visualize_point_cloud(pred_points, gt):
    pred_np = pred_points[0].detach().cpu().numpy()
    gt_np = gt[0].detach().cpu().numpy()
    x, y, z = pred_np[:, 0], pred_np[:, 1], pred_np[:, 2]
    x1, y1, z1 = gt_np[:, 0], gt_np[:, 1], gt_np[:, 2]

    fig = plt.figure(figsize=(12, 6))

    ax = fig.add_subplot(121, projection='3d')
    ax.scatter(x, y, z, marker='o', s=1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title("Predicted Points")

    ax1 = fig.add_subplot(122, projection='3d')
    ax1.scatter(x1, y1, z1, marker='o', s=1)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    ax1.set_title("Ground Truth Points")

    plt.tight_layout()
    plt.show()


def val():
    dataloader_test = build_dataset_val(args)

    seed = random.randint(1, 10000) if not args.manual_seed else int(args.manual_seed)
    logging.info('Random Seed: %d' % seed)
    random.seed(seed)
    torch.manual_seed(seed)

    # Load model
    model_module = importlib.import_module(args.model_name)
    net = torch.nn.DataParallel(model_module.Model(args))
    net.cuda()

    if hasattr(model_module, 'weights_init'):
        net.module.apply(model_module.weights_init)

    ckpt = torch.load(args.load_model)
    net.module.load_state_dict(ckpt['net_state_dict'])
    logging.info("%s's previous weights loaded." % args.model_name)

    net.module.eval()
    logging.info('Testing...')

    test_loss_l1 = AverageValueMeter()
    test_loss_l2 = AverageValueMeter()

    # Load DRR image
    drr_path = r"D:\ABALATION\sr_folder\L2_s1428_pitch_210.png"
    drr = cv2.imread(drr_path)
    tensorImg = transforms.ToTensor()(drr).unsqueeze(0)

    # Load and normalize GT mesh
    gt_path = r"D:\ABALATION\processed\s1428_vertebrae_L1.npy"
    gt_mesh = np.load(gt_path)
    gt_mesh = normalize_pointcloud(gt_mesh)
    tensorMesh = torch.from_numpy(gt_mesh).float().unsqueeze(0)
    start_time = time.time()
    with torch.no_grad():
        images = tensorImg.cuda().float()
        gt = tensorMesh.cuda().float()

        pred_points = net(images)
        loss_p, loss_t = calc_cd(pred_points, gt)

        cd_l1_item = torch.sum(loss_p).item()
        cd_l2_item = torch.sum(loss_t).item()
        test_loss_l1.update(cd_l1_item, images.shape[0])
        test_loss_l2.update(cd_l2_item, images.shape[0])

    print('Chamfer Distance (L1): %f' % test_loss_l1.avg)
    print('Chamfer Distance (L2): %f' % test_loss_l2.avg)

    #visualize_point_cloud(pred_points, gt)

    pred_np = pred_points[0].detach().cpu().numpy()
    gt_np = gt[0].detach().cpu().numpy()
    os.makedirs("D:/ABALATION/results", exist_ok=True)
    np.save("D:/ABALATION/results/vs1428_vertebrae_L1_pred.npy", pred_np)
    np.save("D:/ABALATION/results/vs1428_vertebrae_L1_gt.npy", gt_np)
    end_time=time.time()
    elapse_time=end_time-start_time
    print(elapse_time)
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Validate on ShapeNet-aligned sample')
    parser.add_argument('-c', '--config', help='Path to config file', required=True)
    parser.add_argument('-gpu', '--gpu_id', help='GPU ID', required=True)
    arg = parser.parse_args()

    config_path = arg.config
    args = munch.munchify(yaml.safe_load(open(config_path)))

    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = str(arg.gpu_id)
    print('Using GPU: ' + str(arg.gpu_id))

    val()
    
   