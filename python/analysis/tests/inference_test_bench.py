from analysis.cc_inference import cat_cc_wave, infer_ccwave_spline
import numpy as np
import matplotlib.pyplot as plt 

cmd_wave = np.zeros(100000)
cmd_wave[8000::16000]=-1
cmd_wave[::16000]=1
cmd_wave[0]=0

cc_wave, configs, results = infer_ccwave_spline(DEBUG_PLOTS=True, run_date = '20240413', 
                 run_time = '151907')

norm_factor = cc_wave[-1]
cc_wave = cc_wave/norm_factor

print(f'Length of cc_wave: {len(cc_wave)}')

cc_wave_full = cat_cc_wave(cmd_wave, cc_wave, amplitude=512*norm_factor, midpt=8192)
fig,ax=plt.subplots()
ax.plot(cc_wave_full)