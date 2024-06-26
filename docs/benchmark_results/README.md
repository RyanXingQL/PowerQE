# Benchmark Results

Benchmarks (PSNR/dB):
- [DIV2K dataset](div2k_psnr.csv)
- [MFQEv2 dataset](mfqev2_psnr.csv)
- [Vimeo90K septuplet dataset](vimeo90k_septuplet_psnr.csv)
- [Vimeo90K triplet dataset](vimeo90k_triplet_psnr.csv)

Note:
- During inference on the Vimeo90K septuplet dataset, some samples show zero MSE, resulting in infinite PSNR. These samples are excluded from the average PSNR calculation, and their count is recorded in [this table](inf_vimeo90k_septuplet_psnr.csv).
- The video benchmark results are sample-wise averages from the PowerQE testing script, favoring videos with more frames and possibly not fully representative due to the varied number of test samples per video.
- PSNR for image benchmarks is calculated on the entire image, with no border cropping.