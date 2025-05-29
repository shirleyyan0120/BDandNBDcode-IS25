import shutil
import os
import scipy.io
import numpy as np
from scipy.io import savemat
# 源文件路径
ear_dir = ''
eeg_dir = ''
dest_dit='../../../preprocess_data/'
mat_file_path = './real_tail.mat'

sblist = [2,3,4,5,6,7,8,9,10,1,13,14,15,16,17,18]
attdir2 = scipy.io.loadmat(mat_file_path)['real_tail']
for sb in range(1,17):
    if sb<10:
        out_dit = dest_dit +'/sub00'+str(sb)
    else:
        out_dit = dest_dit + '/sub0' + str(sb)
    if not os.path.exists(out_dit):
        os.makedirs(out_dit)
    for tr in range(1,41):
        trr =int(attdir2[sblist[sb-1]-1,tr-1])
        if trr <10:
            out_dir = out_dit +'/tr00'+str(trr)+'/'
        else:
            out_dir = out_dit +'/tr0'+str(trr)+'/'

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)


        savemat(out_dir + 'pseudodir.mat', {'pseudodir': (tr-1)//10})
