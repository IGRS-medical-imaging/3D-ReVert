import argparse
import torch
import munch
import yaml
from trainer_dataset import build_dataset_val
import torch
from train_utils import *
import logging
import importlib
import random
import os
import argparse
from model_utils import *
from tqdm import tqdm
import matplotlib.pyplot as plt
import warnings
import visdom
warnings.filterwarnings("ignore")


def visualize_point_cloud(pred_points, gt):
    pred_np = pred_points[0].detach().cpu().numpy()  # Convert to NumPy
    gt_np = gt[0].detach().cpu().numpy()
    x, y, z = pred_np[:, 0], pred_np[:, 1], pred_np[:, 2]
    x1, y1, z1 = gt_np[:,0], gt_np[:,1], gt_np[:,2]
    
    fig = plt.figure(figsize=(12, 6))

    ax = fig.add_subplot(121, projection='3d')
    ax.scatter(x, y, z, marker='o', s=1)  # 3D scatter plot
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title("Predicted points")

    ax1 = fig.add_subplot(122, projection='3d')
    ax1.scatter(x1, y1, z1, marker='o', s=1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title("GT points")

    plt.show()



def val():
    
    dataloader_test = build_dataset_val(args)

    if not args.manual_seed:
        seed = random.randint(1, 10000)
    else:
        seed = int(args.manual_seed)
    logging.info('Random Seed: %d' % seed)
    random.seed(seed)
    torch.manual_seed(seed)

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

    save_dir = r"C:\attriflow_val_save"
    for i, data in enumerate(tqdm(dataloader_test)):
        with torch.no_grad():
            images = data['image'].cuda()
            gt = data['points'].cuda()
            pred_points = net(images)

            batch_size = gt.shape[0]
            for b in range(batch_size):
                # Extract pointcloud filename
                file_path = data['pointcloud_path'][b]  # Get filename for each sample
                file_name = os.path.basename(file_path).replace('.npy', '')

                # Save the image, gt, and pred for each sample
                np.save(f"{save_dir}/{file_name}_input.npy", images[b].cpu().numpy())
                np.save(f"{save_dir}/{file_name}_gt.npy", gt[b].cpu().numpy())
                np.save(f"{save_dir}/{file_name}_pred.npy", pred_points[b].cpu().numpy())

    with tqdm(dataloader_test) as t:
        for i, data in enumerate(t):
            with torch.no_grad():
                print(data)
                images = data['image'].cuda()
                gt = data['points'].cuda()

                batch_size = gt.shape[0]
                
                pred_points = net(images)
                batch_size = gt.shape[0]
                for b in range(batch_size):
                    # Extract pointcloud filename
                    file_path = data['pointcloud_path'][b]  # Get filename for each sample
                    file_name = os.path.basename(file_path).replace('.npy', '')

                    # Save the image, gt, and pred for each sample
                    np.save(f"{save_dir}/{file_name}_input.npy", images[b].cpu().numpy())
                    np.save(f"{save_dir}/{file_name}_gt.npy", gt[b].cpu().numpy())
                    np.save(f"{save_dir}/{file_name}_pred.npy", pred_points[b].cpu().numpy())


                # # Extract original file name (remove directory if needed)
                # file_path = data['pointcloud_path'][0] if isinstance(data['pointcloud_path'], list) else data['pointcloud_path']
                # file_name = os.path.basename(file_path).replace('.npy', '')

                # print(gt.shape)
                # print(pred_points.shape)
                #visualize_point_cloud(pred_points, gt)
                if i % 10 == 0:
                    vis.image(images[0].cpu(), win='INPUT IMAGE VAL', opts=dict(title="INPUT IMAGE TRAIN"))
                    vis.scatter(X=gt[0].cpu(),
                                win='VAL_INPUT',
                                opts=dict(
                                    title="VAL_INPUT",
                                    markersize=2,
                                ),
                                )
                    vis.scatter(X=pred_points[0].cpu(),
                                win='VAL_INPUT_RECONSTRUCTED',
                                opts=dict(
                                    title="VAL_INPUT_RECONSTRUCTED",
                                    markersize=2,
                                ),
                                )
                
                #save
                np.save(f"{save_dir}/image4k_{i}.npy", images.cpu().numpy())  # Save input image
                np.save(f"{save_dir}/gt4k_{i}.npy", gt.cpu().numpy())  # Save ground truth
                np.save(f"{save_dir}/pred4k_{i}.npy", pred_points.cpu().numpy())  # Save predicted points

                loss_p, loss_t = calc_cd(pred_points, gt)
                cd_l1_item = torch.sum(loss_p).item() / batch_size
                cd_l2_item = torch.sum(loss_t).item() / batch_size
                test_loss_l1.update(cd_l1_item, images.shape[0])
                test_loss_l2.update(cd_l2_item, images.shape[0])
                
    print('cd_l1 %f cd_l2 %f' % (test_loss_l1.avg, test_loss_l2.avg))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train config file')
    parser.add_argument('-c', '--config', help='path to config file', required=True)
    parser.add_argument('-gpu', '--gpu_id', help='gpu_id', required=True)
    arg = parser.parse_args()
    config_path = arg.config
    args = munch.munchify(yaml.safe_load(open(config_path)))

    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = str(arg.gpu_id)
    print('Using gpu:' + str(arg.gpu_id))
    vis = visdom.Visdom(port=8097)
    val()
    # Call this function after prediction
