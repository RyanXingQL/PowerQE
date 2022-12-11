_base_ = ['./arcnn_c64c32c16k9k7k1k5_div2k_ps128_bs32_1000k_g1.py']

exp_name = 'arcnn_c64c32c16k9k7k1k5_div2k_lmdb_ps128_bs32_1000k_g1'

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
    train=dict(dataset=dict(_delete_=True,
                            type='SRLmdbDataset',
                            lq_folder='./data/div2k/train/lq_patches.lmdb',
                            gt_folder='./data/div2k/train/gt_patches.lmdb',
                            pipeline=train_pipeline,
                            scale=1)),
    val=dict(_delete_=True,
             type='SRLmdbDataset',
             lq_folder='./data/div2k/valid/lq.lmdb',
             gt_folder='./data/div2k/valid/gt.lmdb',
             pipeline=test_pipeline,
             scale=1),
    test=dict(_delete_=True,
              type='SRLmdbDataset',
              lq_folder='./data/div2k/valid/lq.lmdb',
              gt_folder='./data/div2k/valid/gt.lmdb',
              pipeline=test_pipeline,
              scale=1))

# runtime settings
work_dir = f'./work_dirs/{exp_name}'
