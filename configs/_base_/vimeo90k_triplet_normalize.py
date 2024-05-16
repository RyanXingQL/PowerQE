_base_ = "vimeo90k_triplet.py"

norm_cfg = dict(mean=[0, 0, 0], std=[1, 1, 1])
train_pipeline = [
    dict(
        type="LoadImageFromFileList", io_backend="disk", key="lq", channel_order="rgb"
    ),
    dict(
        type="LoadImageFromFileList", io_backend="disk", key="gt", channel_order="rgb"
    ),
    dict(type="RescaleToZeroOne", keys=["lq", "gt"]),
    dict(type="Normalize", keys=["lq", "gt"], **norm_cfg),
    dict(type="PairedRandomCrop", gt_patch_size=256),  # keys must be 'lq' and 'gt'
    dict(type="Flip", keys=["lq", "gt"], flip_ratio=0.5, direction="horizontal"),
    dict(type="Flip", keys=["lq", "gt"], flip_ratio=0.5, direction="vertical"),
    dict(type="RandomTransposeHW", keys=["lq", "gt"], transpose_ratio=0.5),
    dict(type="FramesToTensor", keys=["lq", "gt"]),
    dict(type="Collect", keys=["lq", "gt"], meta_keys=["lq_path", "gt_path"]),
]
test_pipeline = [
    dict(
        type="LoadImageFromFileList", io_backend="disk", key="lq", channel_order="rgb"
    ),
    dict(
        type="LoadImageFromFileList", io_backend="disk", key="gt", channel_order="rgb"
    ),
    dict(type="RescaleToZeroOne", keys=["lq", "gt"]),
    dict(type="Normalize", keys=["lq", "gt"], **norm_cfg),
    dict(type="FramesToTensor", keys=["lq", "gt"]),
    dict(type="Collect", keys=["lq", "gt"], meta_keys=["lq_path", "gt_path", "key"]),
]

# Since there are only three frames in a sequence,
# two of which need padding in testing,
# training also use padding.
data = dict(
    train=dict(
        dataset=dict(pipeline=train_pipeline),
    ),
    val=dict(pipeline=test_pipeline),
    test=dict(pipeline=test_pipeline),
)
