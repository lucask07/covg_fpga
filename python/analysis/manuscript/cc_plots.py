import os
import itertools
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis.cc_calibration import main as main_cc
from analysis.cc_inference import infer_ccwave_spline as infer_ccwave_spline
from analysis.utils import my_savefig, fig_size, fig_dir  # also configures matplotlib defautls
from datastream.datastream import h5_to_datastreams
from filters.filter_tools import butter_lowpass_filter
from analysis.adc_data import find_peak
from control import step_info
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

FS = 5e6
main_cc(subdir='clamp/20240413/',
        cmd_file='cmd_impulse.h5', cc_file='cc_impulse.h5', MAKE_PLTS=True)

# load the training results
base_dir = "/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp"

fig_dir = os.path.join(fig_dir, 'cc')

adg_r = 33
ccomp = 47
cc_wave, configs, results = infer_ccwave_spline(run_date='20240417',
                                                run_time='163357',
                                                cmd_wave=None, DEBUG_PLOTS=True,
                                                base_dir=base_dir,
                                                rtia=adg_r,
                                                ccomp=ccomp)

decay = 0.8
fig, ax = plt.subplots(figsize=(fig_size[0], fig_size[1]*0.8))
# get a time vector 
for res in results['step_wave']:
    decay *= 0.99
    ax.plot(res.cpu().detach().numpy(), alpha=1 - decay, color='blue')
my_savefig(fig, fig_dir, f'Im_and_trained_response_rtia{adg_r}_ccomp{ccomp}')

fig, ax = plt.subplots(figsize=(fig_size[0], fig_size[1]*0.8))
# get a time vector 
tl = 450e-6
scale_factor = (configs['max_target'] / configs['max_impulse']) * configs['cmd_conv_factor'] / configs[
    'cc_conv_factor']  #
# results['output'] is the predicted I_CC after convolution with the wave and normalized impulse
# this is trained to match the normalized Im 
# target waveform: 
# ds['CMD0']['Im'].data[im_idx_imp]/impulse['CMD0'].step_pkpk # A/V
target_scale = configs['cmd_val'] * configs['cmd_conv_factor'] * 2.0
t = np.linspace(start=0, stop=1 / FS * len(results['output'][-1]), num=len(results['output'][-1]))

ax.plot((t - tl) * 1e6, (configs['target'] * target_scale).cpu().detach().numpy() * 1e6, label='CMD')
ax.plot((t - tl) * 1e6, (results['output'][-1] * configs['max_target'] * target_scale).cpu().detach().numpy() * 1e6,
        label='CC', linestyle='--')
ax.set_xlabel('time [$\mu$s]')
ax.set_ylabel('$I \; [\mu A]$')
ax.set_xlim([-50, 250])
ax.yaxis.set_label_coords(-0.1,0.5) # so that the ylabels on the two stacked charts align
ax.legend(loc=9, handlelength=1.8) # ensure that the dashed line is clear

# and inset for the training
axins2 = inset_axes(ax, width="100%", height="100%",
                    bbox_to_anchor=(.65, .55, .35, .35),
                    bbox_transform=ax.transAxes)

for res in results['step_wave']:
    decay *= 0.99
    axins2.plot((t - tl) * 1e6, res.cpu().detach().numpy(), alpha=1 - decay, color='blue')

axins2.set_ylabel('')
axins2.yaxis.set_tick_params(labelleft=False)
axins2.set_yticks([], minor=True)
axins2.yaxis.set_ticks_position('none')
axins2.set_xlabel('time [$\mu$s]')
axins2.set_xlim([-50, 250])

my_savefig(fig, fig_dir, f'Im_and_trained_response_rtia{adg_r}_ccomp{ccomp}')

# data folders and method
method = 'spline'
file_name = '204333'
yrdate = '20240418'

# parameters 
fc = 1000e3
order = 1
res = {}

for k in ['meas_config', 'msq', 'peak', 'int_q', 'undershoot', 'risetime', 'rtia', 'ccomp', 'cmd_step',
          'undershoot_manual']:
    res[k] = []

for adg_r, ccomp in ([(10, 47), (33, 47), (100, 47), (33, 4700), (100, 4700), (332, 47), (332, 4700)]):

    clr = itertools.cycle(['b', 'tab:orange', 'g', 'k'])

    ds = {}
    ds['CMD0'] = h5_to_datastreams(os.path.join(base_dir, yrdate),
                                   f"cmd_impulse_{yrdate}-{file_name}_rtia{adg_r}_ccomp{ccomp}.h5")
    res['cmd_step'] = np.max(ds['CMD0']['CMD0'].data) - np.min(ds['CMD0']['CMD0'].data)

    pos_pks = find_peak(ds['CMD0']['CMD0'].create_time(),
                        np.diff(ds['CMD0']['CMD0'].data),
                        th=0.5e-3, height=2e-3, distance=100)
    t = ds['CMD0']['Im'].create_time()
    t_idx = (t > (pos_pks[0][0] - 50e-6)) & (t < (pos_pks[0][0] + 250e-6))
    t_idx_pedestal = (t > (pos_pks[0][0] - 200e-6)) & (t < (pos_pks[0][0] - 50e-6))
    ds['CC0'] = h5_to_datastreams(os.path.join(base_dir, yrdate),
                                  f"cc_impulse_{yrdate}-{file_name}_rtia{adg_r}_ccomp{ccomp}.h5")

    ds['cancel'] = h5_to_datastreams(os.path.join(base_dir, yrdate),
                                     f"cancelation_{method}_{yrdate}-{file_name}_rtia{adg_r}_ccomp{ccomp}.h5")

    ds['canceling_cc'] = h5_to_datastreams(os.path.join(base_dir, yrdate),
                                           f"canceling_cc_{method}_{yrdate}-{file_name}_rtia{adg_r}_ccomp{ccomp}.h5")

    fig, ax = plt.subplots(figsize=(fig_size[0],fig_size[1]*0.8))
    print('---------')
    lbls = {'CMD0': 'CMD',
            'canceling_cc': 'CC',
            'CC0': 'CC0',
            'cancel': 'CMD + CC'}
    for meas in ['CMD0', 'canceling_cc', 'CC0', 'cancel']:
        res['meas_config'].append(meas)
        data = ds[meas]['Im'].data
        data = data - np.mean(data[t_idx_pedestal])

        res['msq'].append(np.sum((data[t_idx]) ** 2))
        res['peak'].append(np.max(np.abs(data[t_idx])) * 1e6)  # peak current in uA
        res['int_q'].append(np.sum((data[t_idx]) * 1 / FS) * 1e9)  # integrated charge in nC
        res['rtia'].append(adg_r)
        res['ccomp'].append(ccomp)

        # prepare plotting data
        t = ds[meas]['Im'].create_time() - pos_pks[0][0]
        data = butter_lowpass_filter(data, cutoff=fc, fs=FS, order=1)
        if meas != 'CC0':
            if meas == 'cancel':
                ax.plot(t[t_idx] * 1e6, data[t_idx] * 1e6, color=next(clr), label=lbls[meas], linestyle='--')
            elif meas == 'canceling_cc':
                ax.plot(t[t_idx] * 1e6, data[t_idx] * 1e6, color=next(clr), label=lbls[meas], linestyle='-.')
            else:
                ax.plot(t[t_idx] * 1e6, data[t_idx] * 1e6, color=next(clr), label=lbls[meas])
        sf = step_info(data[t_idx], t[t_idx])  # the current isn't a step so this doesn't work well
        res['undershoot'].append(sf['Undershoot'])
        res['risetime'].append(sf['RiseTime'])
        res['undershoot_manual'].append(-np.min(data[t_idx]) / np.max(data[t_idx]) * 100)

        print(f'{meas}, mean square = {res["msq"][-1]}, peak = {res["peak"][-1] * 1e6} [uA]; intQ={res["int_q"][-1]}')
        print(f'Command step: {res["cmd_step"]}')
    print('---------')
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$I \; [\mu A]$')
    ax.yaxis.set_label_coords(-0.1,0.5)
    ax.legend(handlelength=3)
    ax.set_xlim([-50, 250])
    my_savefig(fig, fig_dir, f'cc_cancelation_measured_rtia{adg_r}_ccomp{ccomp}')

    plt.close('all')

# create a CSV
df = pd.DataFrame(res)
df.to_csv(os.path.join(fig_dir, 'cc_cancel_metrics.csv'))

# [10,47], [33, 4700] - not stable
# [332, 47] - saturates
df2 = df[((df['rtia'] == 33) & (df['ccomp'] == 47)) | ((df['rtia'] == 100) & (df['ccomp'] == 47)) | (
        (df['rtia'] == 100) & (df['ccomp'] == 4700) | (df['rtia'] == 332) & (df['ccomp'] == 4700))]

df2 = df2[(df2['meas_config'] == 'cancel') | (df2['meas_config'] == 'CMD0')]

# reorder column titles
columns_titles = ['rtia', 'ccomp', 'undershoot_manual', 'meas_config', 'msq', 'peak', 'int_q']
df2 = df2.reindex(columns=columns_titles)


def float_format_num(x):
    return f'\\num{{ {x:1.3g} }}'


df2.to_csv(os.path.join(fig_dir, 'cc_cancel_metrics_cropped.csv'))
print(df2.to_latex(index=False, float_format=float_format_num))
