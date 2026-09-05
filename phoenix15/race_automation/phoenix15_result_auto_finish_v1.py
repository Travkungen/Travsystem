from pathlib import Path
import pandas as pd
import json

ROOT = Path('/content/drive/MyDrive/PhoenixTrav/phoenix_15_live')
ARCHIVE_ROOT = ROOT / 'results_archive'


def phoenix_prepare_round_result(result_df):
    if result_df is None:
        raise ValueError('result_df är None.')
    if not isinstance(result_df, pd.DataFrame):
        raise TypeError('result_df måste vara pandas DataFrame.')
    df = result_df.copy()
    for col in ['race_id', 'horse_id']:
        if col not in df.columns:
            raise ValueError(f'Resultat saknar {col}.')
    result_col = next((c for c in ['actual_position','placement_sort','placement','position','finish','result'] if c in df.columns), None)
    if result_col is None:
        raise ValueError('Ingen placeringskolumn hittades.')
    df['actual_position'] = pd.to_numeric(df[result_col], errors='coerce')
    df['winner'] = (df['actual_position'] == 1).astype(int)
    return df.drop_duplicates(['race_id','horse_id'], keep='first').reset_index(drop=True)


def phoenix_validate_live_round(prediction_df, result_df):
    pred = prediction_df[['race_id','horse_id']].drop_duplicates()
    res = result_df[['race_id','horse_id']].drop_duplicates()
    matched = pred.merge(res, on=['race_id','horse_id'], how='inner')
    pred_races = pred['race_id'].nunique()
    result_races = res['race_id'].nunique()
    matched_races = matched['race_id'].nunique()
    coverage = matched_races / max(pred_races, 1) * 100
    return {'prediction_races': int(pred_races), 'result_races': int(result_races), 'matched_races': int(matched_races), 'race_coverage_pct': round(coverage, 2), 'prediction_rows': int(len(pred)), 'result_rows': int(len(res)), 'matched_rows': int(len(matched))}


def phoenix_finish_full_round(date, game, prediction_df, result_df):
    result_df = phoenix_prepare_round_result(result_df)
    validation = phoenix_validate_live_round(prediction_df, result_df)
    if validation['race_coverage_pct'] < 100:
        raise ValueError('Resultatet täcker inte alla prediction-lopp.')
    round_id = f'{date}_{game}'
    round_dir = ARCHIVE_ROOT / 'rounds' / round_id
    round_dir.mkdir(parents=True, exist_ok=True)
    prediction_path = round_dir / 'phoenix_predictions.parquet'
    result_path = round_dir / 'actual_results.parquet'
    if not prediction_path.exists():
        prediction_df.to_parquet(prediction_path, index=False)
    if not result_path.exists():
        result_df.to_parquet(result_path, index=False)
    manifest_path = round_dir / 'manifest.json'
    manifest = {'round_id': round_id, 'date': str(date), 'game': str(game), 'prediction_archived': True, 'result_archived': True, 'result_validation': validation, 'master_read_only': True, 'model_read_only': True, 'append_only': True}
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    return {'round_id': round_id, 'validation': validation, 'prediction_path': str(prediction_path), 'result_path': str(result_path), 'manifest_path': str(manifest_path)}
