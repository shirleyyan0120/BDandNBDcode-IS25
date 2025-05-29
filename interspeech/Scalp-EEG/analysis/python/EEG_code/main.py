import numpy as np
import h5py
import torch
import config as cfg
from train_valid_and_test import train_valid_model,test_model
import argparse
import os

def from_mat_to_tensor(raw_data):
    #transpose, the dimention of mat and numpy is contrary
    Transpose = np.transpose(raw_data)
    Nparray = np.array(Transpose)
    return Nparray

# all the number of sbjects in the experiment
# train one model for every subject

parser = argparse.ArgumentParser()


parser.add_argument('--dataset', type=str, default='B_EEG',choices=['B_EEG','NB_EEG','pNB_EEG'])
parser.add_argument('--decision_window', type=float, default=0.5)
parser.add_argument('--model',type = str,default='CNN_baseline',choices=['DenseNet_37-I3D','CNN_baseline','STANet'])

args, unknown = parser.parse_known_args()
cfg.decision_window = int(args.decision_window * 128)
cfg.dataset_name = args.dataset
cfg.model_name = args.model

if args.dataset == 'B_EEG':
    cfg.elenum = 64
else:
    cfg.elenum = 59

# read the data
if args.model == 'DenseNet_37-I3D':
    eegname = cfg.process_data_dir + '/' +  cfg.dataset_name + '_2D.mat'
else:
    eegname = cfg.process_data_dir + '/' +  cfg.dataset_name + '_1D.mat'

eegdata = h5py.File(eegname, 'r')
data = from_mat_to_tensor(eegdata['EEG'])  # eeg data
label = from_mat_to_tensor(eegdata['ENV'])  # 0 or 1, representing the attended direction

# random seed
torch.manual_seed(2024)
if torch.cuda.is_available():
    torch.backends.cudnn.deterministic = True
    torch.cuda.manual_seed_all(2024)

res = torch.zeros((cfg.sbnum,cfg.kfold_num))


from sklearn.model_selection import KFold,train_test_split
kfold = KFold(n_splits=cfg.kfold_num, shuffle=True, random_state=2024)

for sb in range(cfg.sbnum):
    # get the data of specific subject
    eegdata = data[sb]
    eeglabel = label[sb]
    datasize = eegdata.shape


    for fold in range(5):
        # test_ids: fold*2,fold*2+1,fold*2+10,fold*2+11,fold*2+20,fold*2+21,fold*2+30,fold*2+31
        test_ids = np.array([fold*2,fold*2+1,fold*2+10,fold*2+11,fold*2+20,fold*2+21,fold*2+30,fold*2+31])
        valid_ids = (test_ids + 2) % 40
        train_ids = np.setdiff1d(np.arange(40), np.concatenate((test_ids, valid_ids), axis=0))
        print(fold)

        traindata = eegdata[train_ids]
        trainlabel = eeglabel[train_ids]
        validdata = eegdata[valid_ids]
        validlabel = eeglabel[valid_ids]
        testdata = eegdata[test_ids]
        testlabel = eeglabel[test_ids]

        if args.model == 'DenseNet_37-I3D':
            traindata = traindata.reshape(24 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window, 9, 9)
            trainlabel = trainlabel.reshape(24 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window)
            validdata = validdata.reshape(8 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window, 9, 9)
            validlabel = validlabel.reshape(8 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window)
            testdata = testdata.reshape(8 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window, 9, 9)
            testlabel = testlabel.reshape(8 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window)
        else:
            traindata = traindata.reshape(24 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window, cfg.elenum)
            trainlabel = trainlabel.reshape(24 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window)
            validdata = validdata.reshape(8 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window, cfg.elenum)
            validlabel = validlabel.reshape(8 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window)
            testdata = testdata.reshape(8 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window, cfg.elenum)
            testlabel = testlabel.reshape(8 * int(60 * cfg.sample_rate / cfg.decision_window), cfg.decision_window)


        train_valid_model(traindata, trainlabel, validdata, validlabel, sb, fold)
        res[sb,fold] = test_model(testdata, testlabel, sb,fold)
    print("good job!")

for sb in range(cfg.sbnum):
    print(sb)
    print(torch.mean(res[sb]))

csvname = f'./result/{cfg.decision_window}_{cfg.dataset_name}_{cfg.model_name}' + '.csv'
if not os.path.exists('./result/'):
    os.makedirs('./result/')
np.savetxt(csvname, res.numpy(), delimiter=',')


