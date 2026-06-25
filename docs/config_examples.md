# Configuration Examples

The repository includes a few example JSON files under `examples/` to help you get the training pipeline running quickly.

## `dataset_roots.example.json`

Use this as the starting point for local training runs. It includes:

- `daic_woz_root`
- `meld_root`
- `ravdess_root`
- `manifest_dir`
- `ravdess_frames_dir`
- `comorbidity_balanced_manifest`
- `comorbidity_target_rows`

The comorbidity bootstrapped manifest now defaults to `tmp_datasets/comorbidity_60k.csv`, with `comorbidity_target_rows` set to `60000` and a balanced bucket target mix.

Why that path:

- the repository had a locked `data/manifests/comorbidity_balanced.csv` file in this workspace
- `tmp_datasets/` is writable and safe for regenerated pipeline artifacts
- the training pipeline and README now both point to that writable location by default

## `dataset_roots_and_federated.example.json`

Use this when you want the same dataset roots plus a federated training example.

It includes the same writable manifest path so federated and non-federated runs stay aligned.

## Local Copies

When you copy the examples to a local file, you can adjust the dataset roots and leave the writable manifest path as-is:

```powershell
Copy-Item examples\dataset_roots.example.json examples\dataset_roots.local.json
Copy-Item examples\dataset_roots_and_federated.example.json examples\dataset_roots_and_federated.local.json
```

If the locked CSV issue is resolved later, you can point `comorbidity_balanced_manifest` back to `data/manifests/comorbidity_balanced.csv`, but that is no longer the default.

## Notes on Current Training Priorities

The training pipeline currently treats:

- `text_transformer` as the primary text bundle,
- `audio` as the primary audio bundle,
- `image_dl` as the primary image bundle,
- `comorbidity` as a downstream head that should be retrained after the upstream modalities stabilize.
