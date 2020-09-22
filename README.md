# Beat-PD challenge community phase - Snakemake Implementation
https://www.synapse.org/#!Synapse:syn20825169

Original snakemake implementation courtesy of:
Yidi Huang, Mark Keller, Mohammed Saqib

## Setup

Create and activate the [conda](https://docs.conda.io/en/latest/) environment.

```sh
conda env create -f environment.yml
conda activate beat-pd-team-dbmi
```

To enable the Snakefile to download raw data files (for the community-phase clinical measurements), set your Synapse credentials in the following environment variables:

```sh
export SYNAPSE_USERNAME="my_username_here"
export SYNAPSE_PASSWORD="mY-sUpEr-SeCrEt-pAsSwOrD-HeRe"
```

## Downloading the raw data

The inputs to the pipeline should be placed in the `data/raw/` directory (see demo files).
The pipeline will generate all of the files in the `data/processed/` directory.

```
data/
├── raw/
│   ├── train/
│   │   ├── {cohort}_{device}_{instrument}_{subject_id}_{measurement_id}.csv
│   │   ├── labels.csv
│   │   └── manifest.csv
│   └── test/
│       ├── {cohort}_{device}_{instrument}_{subject_id}_{measurement_id}.csv
│       └── manifest.csv
└── processed/
    ├── features/
    │   ├── train/
    │   │   ├── {cohort}_{device}_{instrument}_{subject_id}_{measurement_id}.csv
    │   │   └── features.csv
    │   ├── test/
    │   │   ├── {cohort}_{device}_{instrument}_{subject_id}_{measurement_id}.csv
    │   │   └── features.csv
    │   └── annotations.json
    ├── predictions/
    │   └── test/
    │       ├── {cohort}_{device}_{instrument}_{subject_id}_{measurement_id}.csv
    │       └── predictions.csv
    └── models/
        ├── {cohort}_{device}_{instrument}_{subject_id}.dyskinesia.cv_results.csv
        ├── {cohort}_{device}_{instrument}_{subject_id}.dyskinesia.model_info.json
        ├── {cohort}_{device}_{instrument}_{subject_id}.dyskinesia.model
        ├── {cohort}_{device}_{instrument}_{subject_id}.on_off.cv_results.csv
        ├── {cohort}_{device}_{instrument}_{subject_id}.on_off.model_info.json
        ├── {cohort}_{device}_{instrument}_{subject_id}.on_off.model
        ├── {cohort}_{device}_{instrument}_{subject_id}.tremor.cv_results.csv
        ├── {cohort}_{device}_{instrument}_{subject_id}.tremor.model_info.json
        └── {cohort}_{device}_{instrument}_{subject_id}.tremor.model
```


## Run locally

Download raw data only:

```sh
snakemake \
  --cores 1 \
  --snakefile download.smk \
  --config team=dbmi
```

Download raw data and extract features only:

```sh
snakemake \
  --cores 1 \
  --snakefile featurize.smk \
  --config team=dbmi
```

Download raw data, extract features, train and predict:

```sh
snakemake \
  --cores 1 \
  --snakefile predict.smk \
  --config team=dbmi
```


## Run on a cluster

Fitted models can be evaluated without a cluster, but feature extraction and fitting will be greatly accelerated using a cluster, and the hyperparameter search is infeasible on a single computer. 

Copy the cluster profile to the `~/.config/` directory.

```sh
mkdir -p ~/.config/snakemake/beat-pd
cp ./cluster-profile.yml ~/.config/snakemake/beat-pd/config.yaml
```

To run only the feature extraction part of the pipeline with the cluster profile:

```sh
snakemake \
  --snakefile featurize.smk \
  --profile beat-pd \
  --config team=dbmi base=/n/scratch3/users/m/mk596/pd
```

To run the feature extraction, training, and prediction pipeline with the cluster profile:

```sh
snakemake \
  --snakefile predict.smk \
  --profile beat-pd \
  --config team=dbmi base=/n/scratch3/users/m/mk596/pd
```

Note: these instructions are for SLURM.
If using a different job submission manager, update the `cluster-profile.yml` file.

## Adapting the pipeline for another team

To adapt this pipline code for another team's method, at a minimum, the functions in the following files will need to be updated:
- `extract_annotations.py` [template](./src/extract_annotations.template.py)
- `extract_features_by_measurement.py` [template](./src/extract_features_by_measurement.template.py)
- `train_by_subject.py` [template](./src/train_by_subject.template.py)
- `predict_by_measurement.py` [template](./src/predict_by_measurement.template.py)

Each of the above files runs a single function to produce output file(s) from its input files & wildcard values.
For teams whose methods include a per-subject training step, the pipeline structure (`.smk` file contents) should require little to no modification.

Please reference the comments in the template files (`.template.py`) and in the Snakefiles (`.smk`) for more information about each step of the pipeline.
To learn more about Snakemake please visit the documentation and tutorials [here](https://snakemake.readthedocs.io/en/stable/index.html).


## Pipeline overview


## Pipeline in detail


### Preconditions
 

### Feature extraction


### Hyperparameter search


### Fit on train data


### Predict test data

