from argparse import ArgumentParser
import cv2
import os
from mmdet.apis import inference_detector, init_detector

def show_result_pyplot(model,
                       img,
                       result,
                       score_thr=0.5,
                       title='result',
                       wait_time=0,
                       out_dir = None,
                       remove=False):
    """Visualize the detection results on the image.

    Args:
        model (nn.Module): The loaded detector.
        img (str or np.ndarray): Image filename or loaded image.
        result (tuple[list] or list): The detection result, can be either
            (bbox, segm) or just bbox.
        score_thr (float): The threshold to visualize the bboxes and masks.
        title (str): Title of the pyplot figure.
        wait_time (float): Value of waitKey param.
                Default: 0.
    """
    if hasattr(model, 'module'):
        model = model.module
    out = model.show_result(
        img,
        result,
        score_thr=score_thr,
        show=False,
        wait_time=wait_time,
        win_name=title,
        bbox_color=(72, 101, 241),
        text_color=(72, 101, 241),
        out_dir = out_dir,
        remove = remove
    )
    return out

def main():
    parser = ArgumentParser()
    parser.add_argument('--img_dir', default='data/coco/valpic', help='Image file')
    parser.add_argument('--out_dir', default='val', help='Image file')
    parser.add_argument('--config', default='configs/swin/mask_rcnn_swin_small_patch4_window7_mstrain_480-800_adamw_3x_coco.py', help='Config file')
    # parser.add_argument('--config', default='configs/swin/mask_rcnn_swin_tiny_patch4_window7_mstrain_480-800_adamw_3x_coco.py', help='Config file')
    # parser.add_argument('--checkpoint', default='work_dirs/maskrcnn_swin_small_b1/epoch_75.pth', help='Checkpoint file')
    parser.add_argument('--checkpoint', default='/home/qlx/Swin-Transformer-Object-Detection/work_dirs/maskrcnn_swin_small_b4_707/epoch_38.pth', help='Checkpoint file')
    parser.add_argument(
        '--device', default='cuda:0', help='Device used for inference')
    parser.add_argument(
        '--score-thr', type=float, default=0.7, help='bbox score threshold')
    parser.add_argument(
        '--remove_small', type=bool, default=True, help='bbox score threshold')
    args = parser.parse_args()

    # build the model from a config file and a checkpoint file
    model = init_detector(args.config, args.checkpoint, device=args.device)
    # test a single image
    for img in os.listdir(args.img_dir):
        img_path = os.path.join(args.img_dir, img)
        result = inference_detector(model, img_path)
        # show the results
        out = show_result_pyplot(model, img_path, result, score_thr=args.score_thr, remove=args.remove_small, out_dir = args.out_dir)
        save_name = os.path.join(args.out_dir, img)
        cv2.imwrite(save_name,out)

if __name__ == '__main__':
    main()
