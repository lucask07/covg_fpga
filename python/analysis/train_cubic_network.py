from analysis.cubicspline_cc import main

subdir = 'c:\\Users\\koer2434\\Documents\\covg\\data\\clamp\\20240417\\'

for adg_r, ccomp in ([(10, 47), (33,47), (100, 47), (33,4700), (100,4700), (332,47), (332,4700)]):
    cmd_file=f'cmd_impulse_20240417-163357_rtia{adg_r}_ccomp{ccomp}.h5'
    cc_file=f'cc_impulse_20240417-163357_rtia{adg_r}_ccomp{ccomp}.h5'
    main(subdir, cmd_file, cc_file)
