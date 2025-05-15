# corrField

Close GPU reimplementation in PyTorch of the corrField registration method based on the publicly available [C++ implementation](http://www.mpheinrich.de/code/corrFieldWeb.zip). The method is described [here](http://www.mpheinrich.de/pub/MICCAI2015_paper894.pdf) and can be cited as

```
@inproceedings{heinrich2015estimating,
    title={Estimating large lung motion in COPD patients by symmetric regularised correspondence fields},
    author={Heinrich, Mattias P and Handels, Heinz and Simpson, Ivor JA},
    booktitle={International Conference on Medical Image Computing and Computer-Assisted Intervention (MICCAI)},
    pages={338--345},
    year={2015},
}
```
The implementation is evaluated on the [DIR-LAB COPDgene lung CT dataset](https://www.dir-lab.com/index.html) and achieves similar results as the original implementation with an average-case runtime of approximately 15 seconds on a NVIDIA RTX 2080 TI. The following table lists the target registration error (TRE, in mm) for all 10 cases.

| | # 1 | # 2 | # 3 | # 4 | # 5 | # 6 | # 7 | # 8 | # 9 | # 10 | avg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C++ (orig) | 1.068 | 1.570 | 1.027 | 1.035 | 0.985 | 1.063 | 1.030 | 1.085 | 0.797 | 1.203 | 1.0863 
| PyTorch (GPU) | 0.983 | 1.780 | 1.041 | 0.952 | 1.009 | 0.922 | 1.087 | 1.035 | 0.829 | 1.126 | 1.0764 |

### Example Usage

To register and evaluate case 4 of the DIR-LAB COPDgene data run following commands:

```
./corrfield.py -F ../data/COPDgene/copd4_img_inh.nii.gz -M ../data/COPDgene/copd4_img_exh.nii.gz -m ../data/COPDgene/copd4_mask_inh.nii.gz -O copd4_disp

>> Files copd4_disp.csv and copd4_disp.nii.gz written.
>> Total computation time: 11.6 s
```

```
./eval_copdgene.py -C 4 -D copd4_disp.nii.gz

>> DIR-LAB COPDgene Case 4 evaluation results
>> -----------------------------
>>           Foldings: 0.0008 %
>> SD of log Jacobian: 0.0727
>>                TRE: 0.9498 mm
```

