from AADdataset import AADdataset_1point,AADdataset_1second
from torch.utils.data import DataLoader
from model import EEG_STANet, CNN_baseline
import tqdm
import torch
import config as cfg
import torch.nn as nn
from sklearn.model_selection import train_test_split
from torch.utils.tensorboard import SummaryWriter
import os

writer = SummaryWriter()


# train the model for every subject
def train_valid_model(x_train, y_train, x_valid, y_valid, sb, fold):

    if cfg.model_name == 'STANet':
        model = EEG_STANet().to(cfg.device)
    else:
        model = CNN_baseline().to(cfg.device)

    train_dataset = AADdataset_1second(x_train, y_train)
    valid_dataset = AADdataset_1second(x_valid, y_valid)

    train_loader = DataLoader(dataset=train_dataset, batch_size=cfg.batch_size, shuffle=True)
    valid_loader = DataLoader(dataset=valid_dataset, batch_size=cfg.batch_size, shuffle=True)

    # set the criterion and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)

    # ---------------------train and valid-----------
    valid_loss_min = 100
    for epoch in range(cfg.epoch_num):

        # train the model
        num_correct = 0
        num_samples = 0
        train_loss = 0

        # ---------------------train---------------------
        for iter, (eeg, label) in enumerate(tqdm.tqdm(train_loader, position=0, leave=True), start=1):
            running_loss = 0.0
            # get the input
            eeg = eeg.to(cfg.device)
            label = label.to(cfg.device)

            pred = model(eeg)
            loss = criterion(pred, label)
            train_loss += loss

            # backward
            optimizer.zero_grad()  # clear the grad
            loss.backward()

            # gradient descent or adam step
            optimizer.step()

            _, predictions = pred.max(1)
            num_correct += (predictions == label).sum()
            num_samples += predictions.size(0)


        # ---------------------valid---------------------
        num_correct = 0
        num_samples = 0
        valid_loss = 0.0
        model.eval()
        for iter, (eeg, label) in enumerate(tqdm.tqdm(valid_loader, position=0, leave=True), start=1):
            with torch.no_grad():
                eeg = eeg.to(cfg.device)
                label = label.to(cfg.device)
                pred = model(eeg)
                loss = criterion(pred, label)
                valid_loss = loss + valid_loss
                _, predictions = pred.max(1)
                num_correct += (predictions == label).sum()
                num_samples += predictions.size(0)

        decoder_answer = float(num_correct) / float(num_samples) * 100

        print(f"sb: {sb}, kfold: {fold} epoch: {epoch},\n"
              f"valid loss: {valid_loss / iter} , valid_decoder_answer: {decoder_answer}%\n")


        if valid_loss_min > valid_loss / iter:
            valid_loss_min = valid_loss / iter
            # savedir = './model_{cfg.decision_widow}_{cfg.dataset_name}/sb' + str(sb)
            savedir = f'./model/{cfg.decision_window}_{cfg.dataset_name}_{cfg.model_name}/sb' + str(sb)
            if not os.path.exists(savedir):
                os.makedirs(savedir)
            saveckpt = savedir + '/fold' + str(fold) + '.ckpt'
            torch.save(model.state_dict(), saveckpt)





def test_model(eegdata, eeglabel, sb, fold):

# ----------------------initial model------------------------


    if cfg.model_name == 'STANet':
        model = EEG_STANet().to(cfg.device)
    else:
        model = CNN_baseline().to(cfg.device)

    # test using the current folded data
    x_test, y_test = eegdata, eeglabel


    test_dataset = AADdataset_1second(x_test, y_test)
    # test the data one by one
    test_loader = DataLoader(dataset=test_dataset, batch_size=1, shuffle=True)


# -------------------------test--------------------------------------------
    # after some epochs, test model
    savedir = f'./model/{cfg.decision_window}_{cfg.dataset_name}_{cfg.model_name}/sb' + str(sb)
    saveckpt = savedir + '/fold' + str(fold) + '.ckpt'
    test_acc = 0
    model.load_state_dict(torch.load(saveckpt))
    model.eval()
    total_num = 0
    for iter, (eeg, label) in enumerate(tqdm.tqdm(test_loader, position=0, leave=True), start=1):
        with torch.no_grad():

            # the between densenet and other models
            #
            eeg = eeg.to(cfg.device)
            label = label.to(cfg.device)
            pred = model(eeg)

            _, predictions = pred.max(1)

            if predictions == label:
                test_acc += 1
            total_num = total_num + 1

    res = 100 * test_acc / total_num
    print('Subject %d Fold %d test accuracy: %.3f %%' % (sb, fold, res))


    return res