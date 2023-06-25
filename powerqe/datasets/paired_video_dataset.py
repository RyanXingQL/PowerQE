"""
Author: RyanXingQL
"""

import os
import os.path as osp

from mmedit.datasets import SRAnnotationDataset

from .registry import DATASETS


@DATASETS.register_module()
class PairedVideoDataset(SRAnnotationDataset):
    """Paired video dataset with an annotation file.

    Differences to SRAnnotationDataset:
        Support versatile video loading. See arguments.

    Suppose the video sequences are stored as:

    powerqe
    `-- {gt,lq}_folder
        `-- {001,002,...,100}
            `-- im{1,2,...,7}.png

    Then the annotation file should be:

    001
    002
    ...
    100

    Suppose the video sequences are stored as:

    powerqe
    `-- {gt,lq}_folder
        `-- {001,002,...,100}
            `-- {0001,0002,...,1000}
                `-- im{1,2,...,7}.png

    Then the annotation file should be:

    001/0001
    001/0002
    ...
    001/1000
    002/0001
    ...
    100/1000

    Args:
        lq_folder (str | :obj:Path): LQ folder.
        gt_folder (str | :obj:Path): GT folder.
        ann_file (str | :obj:Path): Path to the annotation file.
            Each line records a sequence path relative to the GT/LQ folder.
        pipeline (List[dict | callable]): A list of data transformations.
        scale (int): Upsampling scale ratio.
        test_mode (bool): Store True when building test dataset.
            Default: False.
        samp_len (int): Sample length.
            The default value -1 corresponds to the sequence length.
            Default: -1.
        edge_padding (bool): Set True to obtain more samples.
            Value False is recommended for training and True for testing.
            Default False.
        center_gt (bool): If True, only the center frame is recorded in GT.
            The samp_len is required to be odd.
            Note that gt_path is always a list. Default: False.
    """

    def __init__(self,
                 lq_folder,
                 gt_folder,
                 ann_file,
                 pipeline,
                 scale,
                 test_mode=False,
                 samp_len=-1,
                 edge_padding=False,
                 center_gt=False):
        self.samp_len = samp_len
        self.edge_padding = edge_padding
        self.center_gt = center_gt

        super().__init__(lq_folder=lq_folder,
                         gt_folder=gt_folder,
                         ann_file=ann_file,
                         pipeline=pipeline,
                         scale=scale,
                         test_mode=test_mode)

    def find_neighboring_frames(self, center_idx, nfrms_left, nfrms_right):
        idxs = list(
            range(center_idx - nfrms_left, center_idx + nfrms_right + 1))
        idxs = [max(min(x, self.seq_len - 1), 0) for x in idxs]  # clip
        return idxs

    def load_annotations(self):
        """Load sequences according to the annotation file.

        The GT sequence includes all frames by default.

        Returned keys (sequence ID; also for image saving):

        (1) center_gt is True:

        001/0001/im4.png  # im1 is the center-frame name of this sample
        001/0001/im2.png  # im2 is the center-frame name of this sample
        ...
        001/0001/im7.png  # im7 is the center-frame name of this sample
        001/0002/im1.png  # im1 is the center-frame name of this sample
        ...

        (2) center_gt is False:

        001/0001/{im1,im2,im3,im4,im5,im6,im7}.png
        001/0002/{im1,im2,im3,im4,im5,im6,im7}.png
        ...
        001/1000/{im1,im2,im3,im4,im5,im6,im7}.png
        ...

        See the image saving function in BasicVQERestorer for reasons.

        Returns:
            list[dict]: Each dict records the information for a sub-sequence to
                serve as a sample in training or testing.
        """
        # Get sequence names (keys)

        with open(self.ann_file, 'r') as f:
            keys = f.read().split('\n')
            keys = [
                k.strip() for k in keys if (k.strip() is not None and k != '')
            ]
        keys = [key.replace('/', os.sep) for key in keys]

        # Collect sample paths according to the sequence names

        data_infos = []
        for key in keys:
            # Get frame paths (sorted)

            gt_seq = osp.join(self.gt_folder, key)
            lq_seq = osp.join(self.lq_folder, key)
            gt_paths = self.scan_folder(gt_seq)
            if len(gt_paths) == 0:
                raise FileNotFoundError(f'No images were found in "{gt_seq}".')
            lq_paths = self.scan_folder(lq_seq)
            if len(gt_paths) != len(lq_paths):
                raise ValueError(
                    f'The GT and LQ sequences for key "{key}" should have'
                    ' the same number of images;'
                    f' GT has {len(gt_paths)} images while'
                    f' LQ has {len(lq_paths)} images.')
            gt_paths = sorted(gt_paths)  # NOTE: sorted
            gt_names = []
            for gt_path in gt_paths:
                gt_name = osp.basename(gt_path)
                lq_path = osp.join(lq_seq, gt_name)
                if lq_path not in lq_paths:
                    raise FileNotFoundError(
                        f'Cannot find "{lq_path}" in "{lq_seq}".')
                gt_names.append(gt_name)

            # Check

            if self.samp_len == -1:
                self.samp_len = len(
                    gt_paths)  # take the whole sequence as a sample

            if self.samp_len > len(gt_paths):
                raise ValueError(
                    f'The sample length ({self.samp_len}) should not be'
                    f' larger than the sequence length ({len(gt_paths)}).')

            if hasattr(self, 'seq_len'):
                if len(gt_paths) != self.seq_len:
                    raise ValueError(
                        'All sequences should have the same number of images;'
                        f' found two sequences with {len(gt_paths)} and'
                        f' {self.seq_len} images.')
            else:
                self.seq_len = len(gt_paths)  # init

            if self.center_gt and (self.samp_len % 2 == 0):
                raise ValueError(
                    f'The sample length ({self.samp_len}) should be odd'
                    ' when requiring center GT.')

            # Record samples

            idxs = list(range(self.seq_len))
            nfrms_left = self.samp_len // 2
            nfrms_right = self.samp_len - nfrms_left - 1
            if (self.samp_len == 1) or self.edge_padding:
                center_idxs = idxs
            else:
                center_idxs = idxs[nfrms_left:(-nfrms_right)]

            for center_idx in center_idxs:
                lq_idxs = self.find_neighboring_frames(center_idx, nfrms_left,
                                                       nfrms_right)
                if self.center_gt:
                    gt_idxs = [center_idx]
                else:
                    gt_idxs = lq_idxs

                samp_gt_paths = [gt_paths[idx] for idx in gt_idxs]
                samp_lq_paths = [
                    osp.join(lq_seq, gt_names[idx]) for idx in lq_idxs
                ]

                record_key = key + os.sep + ','.join(
                    [gt_names[idx] for idx in gt_idxs])
                data_infos.append(
                    dict(gt_path=samp_gt_paths,
                         lq_path=samp_lq_paths,
                         key=record_key))
        return data_infos


@DATASETS.register_module()
class PairedVideoKeyFramesDataset(PairedVideoDataset):
    """Paired video dataset with an annotation file. Return the paths of
    neighboring key frames.

    Differences to PairedVideoAnnotationDataset:
        Use high-quality key frames instead of neighboring frames.
            See "find_neighboring_frames".

    Suppose the video sequences are stored as:

    powerqe
    `-- {gt,lq}_folder
        `-- {001,002,...,100}
            `-- im{1,2,...,7}.png

    Then the annotation file should be:

    001
    002
    ...
    100

    Suppose the video sequences are stored as:

    powerqe
    `-- {gt,lq}_folder
        `-- {001,002,...,100}
            `-- {0001,0002,...,1000}
                `-- im{1,2,...,7}.png

    Then the annotation file should be:

    001/0001
    001/0002
    ...
    001/1000
    002/0001
    ...
    100/1000

    Args:
        lq_folder (str | :obj:Path): LQ folder.
        gt_folder (str | :obj:Path): GT folder.
        ann_file (str | :obj:Path): Path to the annotation file.
            Each line records a sequence path relative to the GT/LQ folder.
        pipeline (List[dict | callable]): A list of data transformations.
        scale (int): Upsampling scale ratio.
        test_mode (bool): Store True when building test dataset.
            Default: False.
        samp_len (int): Sample length.
            The default value -1 corresponds to the sequence length.
            Default: -1.
        edge_padding (bool): Set True to obtain more samples.
            Value False is recommended for training and True for testing.
            Default False.
        center_gt (bool): If True, only the center frame is recorded in GT.
            The samp_len is required to be odd.
            Note that gt_path is always a list. Default: False.
        key_frames (list): Key-frame annotation for a sequence.
            "1" denotes key frames; "0" denotes non-key frames.
            See the document for more details.
    """

    def __init__(self,
                 lq_folder,
                 gt_folder,
                 ann_file,
                 pipeline,
                 scale,
                 test_mode=False,
                 samp_len=-1,
                 edge_padding=False,
                 center_gt=False,
                 key_frames=[1, 0, 1, 0, 1, 0, 1]):
        self.key_frames = key_frames
        super().__init__(lq_folder=lq_folder,
                         gt_folder=gt_folder,
                         ann_file=ann_file,
                         pipeline=pipeline,
                         scale=scale,
                         test_mode=test_mode,
                         samp_len=samp_len,
                         edge_padding=edge_padding,
                         center_gt=center_gt)

    def find_neighboring_frames(self, center_idx, nfrms_left, nfrms_right):
        # Check

        if len(self.key_frames) != self.seq_len:
            raise ValueError(
                f'The sequence length ({self.seq_len}) should be equal to'
                ' that of the key-frame annotation'
                f' ({len(self.key_frames)}).')

        # Find neighboring key frames

        key_idxs = [
            idx for idx in range(len(self.key_frames)) if self.key_frames[idx]
        ]

        key_idxs_left = [idx for idx in key_idxs if idx < center_idx]
        if len(key_idxs_left) == 0:  # if not found
            key_idxs_left = [center_idx - 1] * nfrms_left  # use neighbor
        elif len(key_idxs_left) < nfrms_left:
            key_idxs_left = [key_idxs_left[0]] * (
                nfrms_left - len(key_idxs_left)) + key_idxs_left
        else:
            key_idxs_left = key_idxs_left[-nfrms_left:]

        key_idxs_right = [idx for idx in key_idxs if idx > center_idx]
        if len(key_idxs_right) == 0:
            key_idxs_right = [center_idx + 1] * nfrms_right
        elif len(key_idxs_right) < nfrms_right:
            key_idxs_right = key_idxs_right + [key_idxs_right[-1]] * (
                nfrms_right - len(key_idxs_right))
        else:
            key_idxs_right = key_idxs_right[:nfrms_right]

        idxs = key_idxs_left + [center_idx] + key_idxs_right
        idxs = [max(min(x, self.seq_len - 1), 0) for x in idxs]  # clip
        return idxs


@DATASETS.register_module()
class PairedVideoKeyFramesAnnotationDataset(PairedVideoDataset):
    """Paired video dataset with an annotation file. Return the annotation of
    key frames in each sample.

    Differences to PairedVideoAnnotationDataset:
        Return key-frame annotation. See "load_annotations".

    Suppose the video sequences are stored as:

    powerqe
    `-- {gt,lq}_folder
        `-- {001,002,...,100}
            `-- im{1,2,...,7}.png

    Then the annotation file should be:

    001
    002
    ...
    100

    Suppose the video sequences are stored as:

    powerqe
    `-- {gt,lq}_folder
        `-- {001,002,...,100}
            `-- {0001,0002,...,1000}
                `-- im{1,2,...,7}.png

    Then the annotation file should be:

    001/0001
    001/0002
    ...
    001/1000
    002/0001
    ...
    100/1000

    Args:
        lq_folder (str | :obj:Path): LQ folder.
        gt_folder (str | :obj:Path): GT folder.
        ann_file (str | :obj:Path): Path to the annotation file.
            Each line records a sequence path relative to the GT/LQ folder.
        pipeline (List[dict | callable]): A list of data transformations.
        scale (int): Upsampling scale ratio.
        test_mode (bool): Store True when building test dataset.
            Default: False.
        samp_len (int): Sample length.
            The default value -1 corresponds to the sequence length.
            Default: -1.
        edge_padding (bool): Set True to obtain more samples.
            Value False is recommended for training and True for testing.
            Default False.
        center_gt (bool): If True, only the center frame is recorded in GT.
            The samp_len is required to be odd.
            Note that gt_path is always a list. Default: False.
        key_frames (list): Key-frame annotation for a sequence.
            "1" denotes key frames; "0" denotes non-key frames.
            See the document for more details.
    """

    def __init__(self,
                 lq_folder,
                 gt_folder,
                 ann_file,
                 pipeline,
                 scale,
                 test_mode=False,
                 samp_len=-1,
                 edge_padding=False,
                 center_gt=False,
                 key_frames=[1, 0, 1, 0, 1, 0, 1]):
        self.key_frames = key_frames
        super().__init__(lq_folder=lq_folder,
                         gt_folder=gt_folder,
                         ann_file=ann_file,
                         pipeline=pipeline,
                         scale=scale,
                         test_mode=test_mode,
                         samp_len=samp_len,
                         edge_padding=edge_padding,
                         center_gt=center_gt)

    def load_annotations(self):
        """Load sequences according to the annotation file.

        The GT sequence includes all frames by default.

        Returned keys (sequence ID; also for image saving):

        (1) center_gt is True:

        001/0001/im4.png  # im1 is the center-frame name of this sample
        001/0001/im2.png  # im2 is the center-frame name of this sample
        ...
        001/0001/im7.png  # im7 is the center-frame name of this sample
        001/0002/im1.png  # im1 is the center-frame name of this sample
        ...

        (2) center_gt is False:

        001/0001/{im1,im2,im3,im4,im5,im6,im7}.png
        001/0002/{im1,im2,im3,im4,im5,im6,im7}.png
        ...
        001/1000/{im1,im2,im3,im4,im5,im6,im7}.png
        ...

        See the image saving function in BasicVQERestorer for reasons.

        Returns:
            list[dict]: Each dict records the information for a sub-sequence to
                serve as a sample in training or testing.
        """
        # Get sequence names (keys)

        with open(self.ann_file, 'r') as f:
            keys = f.read().split('\n')
            keys = [
                k.strip() for k in keys if (k.strip() is not None and k != '')
            ]
        keys = [key.replace('/', os.sep) for key in keys]

        # Collect sample paths according to the sequence names
        # also key-frame annotation

        data_infos = []
        for key in keys:
            # Get frame paths (sorted)

            gt_seq = osp.join(self.gt_folder, key)
            lq_seq = osp.join(self.lq_folder, key)
            gt_paths = self.scan_folder(gt_seq)
            if len(gt_paths) == 0:
                raise FileNotFoundError(f'No images were found in "{gt_seq}".')
            lq_paths = self.scan_folder(lq_seq)
            if len(gt_paths) != len(lq_paths):
                raise ValueError(
                    f'The GT and LQ sequences for key "{key}" should have'
                    ' the same number of images;'
                    f' GT has {len(gt_paths)} images while'
                    f' LQ has {len(lq_paths)} images.')
            gt_paths = sorted(gt_paths)  # NOTE: sorted
            gt_names = []
            for gt_path in gt_paths:
                gt_name = osp.basename(gt_path)
                lq_path = osp.join(lq_seq, gt_name)
                if lq_path not in lq_paths:
                    raise FileNotFoundError(
                        f'Cannot find "{lq_path}" in "{lq_seq}".')
                gt_names.append(gt_name)

            # Check

            if self.samp_len == -1:
                self.samp_len = len(
                    gt_paths)  # take the whole sequence as a sample
            if self.samp_len > len(gt_paths):
                raise ValueError(
                    f'The sample length ({self.samp_len}) should not be'
                    f' larger than the sequence length ({len(gt_paths)}).')
            if hasattr(self, 'seq_len'):
                if len(gt_paths) != self.seq_len:
                    raise ValueError(
                        'All sequences should have the same number of images;'
                        f' found two sequences with {len(gt_paths)} and'
                        f' {self.seq_len} images.')
            else:
                self.seq_len = len(gt_paths)  # init
            if self.center_gt and (self.samp_len % 2 == 0):
                raise ValueError(
                    f'The sample length ({self.samp_len}) should be odd'
                    ' when requiring center GT.')

            # Record samples

            idxs = list(range(self.seq_len))
            nfrms_left = self.samp_len // 2
            nfrms_right = self.samp_len - nfrms_left - 1
            if (self.samp_len == 1) or self.edge_padding:
                center_idxs = idxs
            else:
                center_idxs = idxs[nfrms_left:(-nfrms_right)]
            for center_idx in center_idxs:
                lq_idxs = self.find_neighboring_frames(center_idx, nfrms_left,
                                                       nfrms_right)
                if self.center_gt:
                    gt_idxs = [center_idx]
                else:
                    gt_idxs = lq_idxs
                samp_gt_paths = [gt_paths[idx] for idx in gt_idxs]
                samp_lq_paths = [
                    osp.join(lq_seq, gt_names[idx]) for idx in lq_idxs
                ]

                record_key = key + os.sep + ','.join(
                    [gt_names[idx] for idx in gt_idxs])

                key_frms = [self.key_frames[idx] for idx in lq_idxs]

                data_infos.append(
                    dict(gt_path=samp_gt_paths,
                         lq_path=samp_lq_paths,
                         key=record_key,
                         key_frms=key_frms))
        return data_infos