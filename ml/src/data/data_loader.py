from pathlib import Path
import pandas as pd
import librosa
import soundfile as sf
import sys

# Resolves to .../ml/src so `import config` works when running this file directly
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
import config as cfg

path = Path(cfg.DATA_PATH)
rel_path = path.parent

dfs = []

rec_id = []
sub_db = []
label = []
wav_path = []
sample_rate = []
n_samples = []
duration_sec = []

sqi_flag = []
annotation_path = []
has_annotation = []
if path.exists():
    for folder in path.iterdir():
        if folder.name.startswith("training") and not folder.name.endswith("b"):
            for csv_file in folder.glob("REFERENCE-SQI*"):
                dfs.append(
                    pd.read_csv(
                        csv_file,
                        header=None,
                        names=["recording_id", "label", "sqi_flag"],
                    )
                )
            for file in folder.glob("*.wav"):
                rec_id.append(file.name.removesuffix(".wav"))
                sub_db.append(file.name[0])
                wav_path.append(file.relative_to(rel_path))
                audio_file = sf.info(file)
                sample_rate.append(audio_file.samplerate)
                n_samples.append(audio_file.frames)
                duration_sec.append(audio_file.duration)

else:
    print("Path doesn't exist")


df = pd.DataFrame(
    {
        "recording_id": rec_id,
        "sub_db": sub_db,
        "wav_path": wav_path,
        "sample_rate": sample_rate,
        "n_samples": n_samples,
        "duration_sec": duration_sec,
    }
)

concated_dfs = pd.concat(dfs, ignore_index=True)
df = pd.merge(df, concated_dfs, "left", "recording_id")


annot_path = path / "annotations" / "hand_corrected"
for i in range(df.shape[0]):
    if Path(
        annot_path
        / f'training-{df["recording_id"][i][0]}_StateAns'
        / f'{df["recording_id"][i]}_StateAns.mat'
    ).exists():
        annotation_path.append(
            Path(
                annot_path
                / f'training-{df["recording_id"][i][0]}_StateAns'
                / f'{df["recording_id"][i]}_StateAns.mat'
            ).relative_to(rel_path)
        )
        has_annotation.append(1)
    else:
        annotation_path.append(pd.NA)
        has_annotation.append(0)

df['annotation_path'] = annotation_path
df['has_annotation'] = has_annotation

df.to_csv('ml/outputs/master_table.csv', index=False)
