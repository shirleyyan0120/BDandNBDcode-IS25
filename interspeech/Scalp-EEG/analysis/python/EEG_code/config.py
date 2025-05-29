import torch

# models
# # you could change the code to other models by only changing the number
process_data_dir = '../'
# if model_name == 'CNN_baseline':
#     dataset_name = 'AAD_4_direction_1D.mat'
# else:
#     dataset_name = 'AAD_4_direction_2D.mat'

device_ids = 0
device = torch.device(f"cuda:{device_ids}" if torch.cuda.is_available() else "cpu")
epoch_num = 100
batch_size = 128
sample_rate = 128
categorie_num = 4
sbnum = 16
kfold_num = 5

lr=1e-3
weight_decay=0.01






