_base_ = ['provqe_vimeo90k_septuplet.py']

# exp_name = 'debug'

val_inter = 150
checkpoint_config = dict(interval=val_inter,
                         save_optimizer=True,
                         by_epoch=False)
evaluation = dict(interval=val_inter)

# work_dir = f'work_dirs/{exp_name}'