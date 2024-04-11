from analysis.cc_inference import cat_cc_wave, infer_ccwave_spline
import numpy as np
import matplotlib.pyplot as plt 

cmd_wave = np.zeros(100000)
cmd_wave[8000::16000]=-1
cmd_wave[::16000]=1
cmd_wave[0]=0

cc_wave, configs, results = infer_ccwave_spline(DEBUG_PLOTS=True)
cc_wave = cc_wave/cc_wave[-1]
print(f'Length of cc_wave: {len(cc_wave)}')

cc_wave_full = cat_cc_wave(cmd_wave, cc_wave.cpu().detach().numpy(), 10)

fig,ax=plt.subplots()

ax.plot(cc_wave_full)