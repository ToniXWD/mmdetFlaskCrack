_base_ = './ms_rcnn_r101_caffe_fpn_1x_coco.py'
# learning policy
lr_config = dict(step=[16, 22, 27])
runner = dict(type='EpochBasedRunner', max_epochs=30)
