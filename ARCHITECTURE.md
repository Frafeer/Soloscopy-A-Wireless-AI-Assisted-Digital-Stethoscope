# Auscult: Project Architecture

> "Auscult" is a placeholder repo name. Rename the root folder to whatever you pick.

One repository, three tracks. Each track owns one top-level folder.

| Folder      | Owner           | Contents                                            |
|-------------|-----------------|-----------------------------------------------------|
| `hardware/` | Mai & Mariam    | Chest Piece and Hearing Device firmware, schematics |
| `app/`      | Heaven & Sara   | Flutter app (optional Mode 2, on-device AI)         |
| `ml/`       | John            | Training, evaluation, export of Heart and Lung models |
| `docs/`     | Everyone        | Report material and the interface contract          |

## Folder tree

```
Auscult/
├── hardware/
│   ├── chest_piece/              firmware (ESP32), schematics, BOM
│   ├── hearing_device/           firmware (ESP32), schematics, BOM
│   ├── datasheets/               CM-01B, ESP32 notes
│   └── test_recordings/          small custom-hardware .wav samples (committed on purpose)
│
├── app/                          Flutter project
│   ├── lib/
│   ├── assets/models/            heart.tflite, lung.tflite (copied from ml/artifacts)
│   ├── test/
│   └── pubspec.yaml
│
├── ml/
│   ├── src/
│   │   ├── config.py                 paths, static links, static params (one block per organ)
│   │   ├── run_train.py              entry point: python run_train.py --organ heart|lung
│   │   ├── predict.py                load a saved model, take a .wav, return a label
│   │   ├── data/
│   │   │   ├── data_loader.py            reads files, builds master table, makes splits
│   │   │   └── preprocessing.py          resample, filter, normalize, window, log-mel
│   │   ├── models/
│   │   │   └── model_factory.py          builds the CNN from the config
│   │   ├── evaluation/
│   │   │   └── model_evaluator.py        per-recording metrics, leave-one-database-out
│   │   ├── tracking/
│   │   │   └── mlflow_logger.py          logs params, metrics, models to MLflow
│   │   ├── pipeline/
│   │   │   └── training_pipeline.py      orchestrates one full experiment
│   │   └── export/
│   │       └── tflite_exporter.py        Keras to TFLite, checked against the original
│   ├── notebooks/                    Colab exploration and plots
│   ├── artifacts/                    exported models agreed with the app team
│   └── requirements.txt
│
├── docs/
│   ├── ml/                       Dataset Understanding, Preprocessing Design, Evaluation Methodology
│   ├── hardware/
│   └── interface_contract.md     what each track promises the others
│
├── ARCHITECTURE.md
├── README.md
└── .gitignore
```

## How the ML pieces connect

```
run_train.py --organ heart
      |
      v
training_pipeline.py
      |-- data_loader.py      -> recordings + splits
      |-- preprocessing.py    -> windows -> log-mel
      |-- model_factory.py    -> model
      |-- (train)
      |-- model_evaluator.py  -> sensitivity / specificity per recording
      '-- mlflow_logger.py    -> saves everything for this run

tflite_exporter.py  -> ml/artifacts/*.tflite -> app/assets/models/
predict.py          -> preprocessing.py + saved model (no training code)
```

## System flow

```
Mode 1 (no app):
  Chest Piece --Bluetooth (uncompressed audio)--> Hearing Device --> doctor listens

Mode 2 (optional AI):
  Chest Piece --audio stream--> Flutter app --> pick organ --> preprocessing
                                                     --> .tflite model --> result
```

## Interface contract (docs/interface_contract.md)

Preprocessing runs in Python for training and must be reproduced exactly in the app.
The contract should list, per organ:

- sample rate, filter band, window length and overlap
- log-mel settings: number of mel bands, FFT size, hop length
- `.tflite` input and output shapes and what each output means
- golden test files: a `.wav` plus its expected spectrogram and prediction

It also records what the hardware promises: sample rate and bit depth of the audio
stream the app receives.

## Phase 2 (stretch) placement

New files, no reorganizing needed:

- `ml/src/pipeline/sqi.py` signal quality gatekeeper, runs before the classifier
- `ml/src/pipeline/uncertainty.py` confidence rejection, runs after the classifier
- `ml/src/robustness/` device-mimicking augmentation and custom-hardware checks
- Noise cancellation, speaker calibration: `hardware/` and `docs/`
- XAI highlighting and slow-motion replay: `app/lib/`

## Working habits

- Each track works on its own branch and merges through pull requests.
- Datasets are never committed. Each person downloads them separately.
- Only agreed `.tflite` files are committed, and the contract changes with them.
- One lab-notebook entry per working day (shared document).
