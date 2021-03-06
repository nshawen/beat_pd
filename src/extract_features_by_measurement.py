import pandas as pd
import numpy as np
import tsfresh as tsf
from itertools import product

from constants import *


def sample_seq(seq: pd.DataFrame, n_samples=10, samp_len=pd.Timedelta(seconds=10), starts=None, reset_time=True):
    if starts is None:
        starts = [pd.Timedelta(seconds=t) for t in random.uniform(low=0, high=float(seq.index.max()-samp_len), size=n_samples)]
    idx = pd.IndexSlice
    if type(seq.index) == pd.MultiIndex:
        samples = [seq.xs(idx[start:start+samp_len], level='t', drop_level=False) for start in starts]
    else:
        samples = [seq.loc[start:start+samp_len] for start in starts]
    # Some samples will be empty/incomplete due to lapses in measurements
    # TODO: Address multiple devices in real-pd smartwatch measurements
    if not reset_time:
        return samples
    if type(seq.index) == pd.MultiIndex:
        return [samp.set_index(samp.index.set_levels(samp.index.levels[1] - start, level='t')) for samp,start in zip(samples, starts)]
    else:
        return [samp.set_index(samp.index - start) for samp,start in zip(samples, starts)]


def read_seq(df, t_colname='t', xyz_colnames=['x', 'y', 'z'], devid_colnames=[], use_time_index=False, resample=pd.Timedelta(seconds=(1/50))):
    df = df.rename(columns=dict(zip([t_colname, *xyz_colnames], ['t', 'x', 'y', 'z'])))

    time_index = pd.to_timedelta(df['t'], unit="s") if use_time_index else df['t']
    devid_index = [df[c] for c in devid_colnames]
    # Drop explicitly to avoid funny business
    df = df.set_index([*devid_index, time_index,], drop=False).drop(columns=['t', *devid_colnames])
    if use_time_index and resample is not None:
        if devid_colnames:
            df = df.groupby(devid_colnames)
        df = df.resample(resample, level='t').mean()
    return df


def extract_features_by_measurement(measurement_df, cohort, device, instrument, subject_id, measurement_id):
    colnames=dict()

    if cohort == "cispd":
        colnames = {'t_colname': 'Timestamp', 'xyz_colnames': ['X', 'Y', 'Z']}
    elif cohort == "realpd" and device == "smartwatch":
        colnames = {'devid_colnames': ['device_id']}
    
    resample_rate = F_HYPERPARAM_VALS[F_HYPERPARAMS.RESAMPLE_RATE.value]
    seq = read_seq(measurement_df, use_time_index=True, resample='100ms', **colnames)
    
    # Some slight interpolation for missing values.
    seq = seq.interpolate(axis=0, limit=1, method='linear')

    # Gravity constant depends on cohort, device, and instrument type.
    rms_g_constant = F_HYPERPARAM_VALS[F_HYPERPARAMS.RMS_G_CONSTANT.value][(cohort, device, instrument)]

    # Subtract constant for gravity.
    rms = pd.DataFrame({ 'rms': np.sqrt(np.square(seq).sum(axis=1, skipna=False)) - rms_g_constant })

    window_offset = F_HYPERPARAM_VALS[F_HYPERPARAMS.WINDOW_OFFSET.value]
    window_size = F_HYPERPARAM_VALS[F_HYPERPARAMS.WINDOW_SIZE.value]
    

    window_starts = [pd.Timedelta(seconds=t) for t in [*range(0, rms.index.get_level_values('t').max().seconds - window_size, window_offset)]]
    samples = sample_seq(rms, starts=window_starts, samp_len=pd.Timedelta(seconds=window_size), reset_time=True)
    for i, df in enumerate(samples):
        df['ord'] = str(i)
        if 'devid_colnames' in colnames:
            df.reset_index(level=colnames['devid_colnames'], inplace=True)
            df['ord'] += '-' + df[colnames['devid_colnames'][0]]
            df.drop(columns=colnames['devid_colnames'], inplace=True)
    
    # Remove windows with nulls.
    tsf_data = pd.concat(samples, axis=0).groupby('ord').filter(lambda x: x.notnull().values.all())
    # Extract time series features with tsfresh.
    tsf_df = tsf.extract_features(tsf_data, column_id="ord", disable_progressbar=True, n_jobs=0)

    # Append the measurement ID.
    tsf_df['measurement_id'] = measurement_id

    # Drop un-used feature columns.

    # These features don't compute for a number of observations.
    drop_cols = ['rms__friedrich_coefficients__m_3__r_30__coeff_0',
        'rms__friedrich_coefficients__m_3__r_30__coeff_1',
        'rms__friedrich_coefficients__m_3__r_30__coeff_2',
        'rms__friedrich_coefficients__m_3__r_30__coeff_3',
        'rms__max_langevin_fixed_point__m_3__r_30']
    # These fft features are null for our size of windows.
    null_fft_cols = ['rms__fft_coefficient__coeff_%d__attr_"%s"' % (n, s) 
                        for n, s in product(range(51, 100), ['abs', 'angle', 'imag', 'real'])]
    # Sample entropy can take inf which screws with models.
    inf_cols = ['rms__sample_entropy']

    tsf_df = tsf_df.drop(columns=[*drop_cols, *null_fft_cols, *inf_cols])

    return tsf_df

if __name__ == "__main__":
    measurement_df = pd.read_csv(snakemake.input[0])
    cohort = snakemake.wildcards['cohort']
    device = snakemake.wildcards['device']
    instrument = snakemake.wildcards['instrument']
    subject_id = snakemake.wildcards['subject_id']
    measurement_id = snakemake.wildcards['measurement_id']
    features_df = extract_features_by_measurement(measurement_df, cohort, device, instrument, subject_id, measurement_id)
    features_df.to_csv(snakemake.output[0], index=True)