# Dataset Integration Audit

## 1. Issue Identification: The Label Explosion
The initial integration resulted in an explosive 1,049,641 records because the `dianxiang-sun/rugpull_dataset.csv` file contained **1046214 empty padding rows**. 
Because pandas `read_csv` reads these as NaN rows instead of skipping them, the integration script blindly assigned `rugpull_label = 1` to all 1046214 empty rows, artificially inflating the positive class by over a million.

## 2. CRPWarner Verification
The `CRPWarner` dataset contains two folders: `groundtruth` and `large`.
- `groundtruth.xlsx` contains exactly 69 manually verified rug pull addresses.
- The massive bytecode/unlabeled datasets in `large/` were **never parsed or treated as rug pulls** by the integration script. The explosion was exclusively caused by Dianxiang Sun's empty rows.

## 3. Original Label Distribution (Corrected)
- **TM-RugPull**: 1000 projects (Legit labels, no explicit token addresses)
- **CRPWarner**: 69 projects (Verified Rug Pulls)
- **Dianxiang-Sun**: 2361 projects (Verified Rug Pulls)

The corrected expected total should be approximately 3,430 projects, not 1,049,641.

## 4. Remediation
1. The parser in `integrate_datasets.py` was updated to explicitly invoke `dropna(how='all')` on the Dianxiang dataset.
2. The dataset has been rebuilt using strictly verified labeled projects.
