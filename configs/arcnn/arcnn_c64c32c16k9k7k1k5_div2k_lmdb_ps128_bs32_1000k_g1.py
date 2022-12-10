exp_name = 'arcnn_c64c32c16k9k7k1k5_div2k_lmdb_ps128_bs32_1000k_g1'

# model settings
model = dict(type='BasicRestorerQE',
             generator=dict(type='ARCNN',
                            in_channels=3,
                            mid_channels_1=64,
                            mid_channels_2=32,
                            mid_channels_3=16,
                            out_channels=3,
                            in_kernel_size=9,
                            mid_kernel_size_1=7,
                            mid_kernel_size_2=1,
                            out_kernel_size=5),
             pixel_loss=dict(type='L1Loss', loss_weight=1.0, reduction='mean'))

# model training and testing settings
train_cfg = None
test_cfg = dict(metrics=['PSNR', 'SSIM'], crop_border=1)

# dataset settings
train_pipeline = [
    dict(
        type='LoadImageFromFile',
        #     io_backend='disk',
        io_backend='lmdb',
        db_path='./data/div2k/train/lq_patches.lmdb',
        key='lq',
        flag='color',
        channel_order='rgb'),
    dict(
        type='LoadImageFromFile',
        #     io_backend='disk',
        io_backend='lmdb',
        db_path='./data/div2k/train/gt_patches.lmdb',
        key='gt',
        flag='color',
        channel_order='rgb'),
    dict(type='RescaleToZeroOne', keys=['lq', 'gt']),
    #     dict(type='PairedRandomCrop', gt_patch_size=128),
    dict(type='Flip',
         keys=['lq', 'gt'],
         flip_ratio=0.5,
         direction='horizontal'),
    dict(type='Flip', keys=['lq', 'gt'], flip_ratio=0.5, direction='vertical'),
    dict(type='RandomTransposeHW', keys=['lq', 'gt'], transpose_ratio=0.5),
    dict(type='Collect', keys=['lq', 'gt'], meta_keys=['lq_path', 'gt_path']),
    dict(type='ImageToTensor', keys=['lq', 'gt'])
]
test_pipeline = [
    dict(
        type='LoadImageFromFile',
        #  io_backend='disk',
        io_backend='lmdb',
        db_path='./data/div2k/train/lq.lmdb',
        key='lq',
        flag='color',
        channel_order='rgb'),
    dict(
        type='LoadImageFromFile',
        #  io_backend='disk',
        io_backend='lmdb',
        db_path='./data/div2k/train/gt.lmdb',
        key='gt',
        flag='color',
        channel_order='rgb'),
    dict(type='RescaleToZeroOne', keys=['lq', 'gt']),
    dict(type='Collect', keys=['lq', 'gt'], meta_keys=['lq_path', 'gt_path']),
    dict(type='ImageToTensor', keys=['lq', 'gt'])
]

data = dict(
    workers_per_gpu=32,
    train_dataloader=dict(samples_per_gpu=32, drop_last=True),
    val_dataloader=dict(samples_per_gpu=1),
    test_dataloader=dict(samples_per_gpu=1),
    train=dict(
        type='RepeatDataset',
        times=1000,
        dataset=dict(
            #   type='QEFolderDataset',
            #   lq_folder='./data/div2k/train/lq',
            #   gt_folder='./data/div2k/train/gt',
            type='SRLmdbDataset',
            lq_folder='./data/div2k/train/lq_patches.lmdb',
            gt_folder='./data/div2k/train/gt_patches.lmdb',
            pipeline=train_pipeline,
            #   filename_tmpl='{}.png')),
            scale=1)),
    val=dict(
        # type='QEFolderDataset',
        # lq_folder='./data/div2k/valid/lq',
        # gt_folder='./data/div2k/valid/gt',
        type='SRLmdbDataset',
        lq_folder='./data/div2k/valid/lq.lmdb',
        gt_folder='./data/div2k/valid/gt.lmdb',
        pipeline=test_pipeline,
        # filename_tmpl='{}.png'),
        scale=1),
    test=dict(
        # type='QEFolderDataset',
        # lq_folder='./data/div2k/valid/lq',
        # gt_folder='./data/div2k/valid/gt',
        type='SRLmdbDataset',
        lq_folder='./data/div2k/valid/lq.lmdb',
        gt_folder='./data/div2k/valid/gt.lmdb',
        pipeline=test_pipeline,
        # filename_tmpl='{}.png'))
        scale=1))

# optimizer
optimizers = dict(generator=dict(type='Adam', lr=1e-4, betas=(0.9, 0.999)))

# learning policy
total_iters = 1000000
lr_config = dict(policy='CosineRestart',
                 by_epoch=False,
                 periods=[total_iters],
                 min_lr=1e-7)

checkpoint_config = dict(interval=5000, save_optimizer=True, by_epoch=False)
evaluation = dict(interval=5000, save_image=False, gpu_collect=True)
log_config = dict(interval=100,
                  hooks=[
                      dict(type='TextLoggerHook', by_epoch=False),
                      dict(type='TensorboardLoggerHook'),
                  ])
visual_config = None

# runtime settings
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = f'./work_dirs/{exp_name}'
load_from = None
resume_from = None
workflow = [('train', 1)]
