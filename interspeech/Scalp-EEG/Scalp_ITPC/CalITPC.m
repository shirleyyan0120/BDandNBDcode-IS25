

% calculate inner-trial phase coherence for block design

% itpc (frequency channels * time samples)

clear
clc
EEGDataDir = ['../preprocess_data_bd/data_env/'];   
sblist = dir(EEGDataDir);
sblist(1:2) = [];
sbnum = size(sblist,1);

conditions = {'1', '2', '3', '4'};


AudioIndexs = 1:10;

eegChannels = 1:59;

if 1 
for i1 = 1:length(conditions)
    disp(['condition = ', num2str(i1)])
    count = 1;c
    for i0 = 1:sbnum
        disp(['---------Subject NO. ---------' num2str(i0)])
        subjectName = sblist(i0).name;
        subjectNameDir =[EEGDataDir filesep subjectName];
        for EEGDataFileNo = (i1-1)*10+1:i1*10
            EEGDataFileName = [subjectNameDir filesep num2str(EEGDataFileNo) '_cap.mat'];
            load(EEGDataFileName,'EEG_env');
            EEG = EEG_env;
            EEGdata = EEG.data; % channel by time
            fs1 = EEG.srate;
            EEGdata(60:64,:) = [];% delete EoG
            EEGdata_temp = mapminmax(double(EEGdata),-1,1);
            respSet{count} = EEGdata_temp';
            count = count + 1;
        end
    end
    for channel2use = eegChannels
        % calculate itpc
        [itpc, frex] = cal_itpc(respSet, fs1, channel2use);
        itpc_t(i1, channel2use, :) = mean(itpc, 2);                
    end
end
save(['./itpc_bd.mat'], 'itpc_t', 'frex');
end

%% plot averaged results for each condition
load('./itpc_bd.mat');
channelindex = 22; % FC5
% channelindex = 52; % PO4

figure
hold on
for i1=1:4
    itpc_t_con = squeeze(itpc_t(i1,channelindex,:));
    plot(frex, itpc_t_con, 'linewidth', 1);
end
lg = legend('+30','-30','+90','-90');
set(lg, 'fontsize',12)
xlabel('Frequency (Hz)')
ylabel('ITPC')
title('electrode FC5')
box on
set(gca,'fontsize',12, 'linewidth', 1)
%% calculate inner-trial phase coherence for non-block design

% itpc (frequency channels * time samples)

clear
clc
EEGDataDir = ['../preprocess_data_nbd/data_env/'];   
sblist = dir(EEGDataDir);
sblist(1:2) = [];
sbnum = size(sblist,1);

conditions = {'1', '2', '3', '4'};


AudioIndexs = 1:10;

eegChannels = 1:59;

if 1 
for i1 = 1:length(conditions)
    disp(['condition = ', num2str(i1)])
    count = 1;c
    for i0 = 1:sbnum
        disp(['---------Subject NO. ---------' num2str(i0)])
        subjectName = sblist(i0).name;
        subjectNameDir =[EEGDataDir filesep subjectName];
        for EEGDataFileNo = (i1-1)*10+1:i1*10
            EEGDataFileName = [subjectNameDir filesep num2str(EEGDataFileNo) '_cap.mat'];
            load(EEGDataFileName,'EEG_env');
            EEG = EEG_env;
            EEGdata = EEG.data; % channel by time
            fs1 = EEG.srate;
            EEGdata(60:64,:) = [];% delete EoG
            EEGdata_temp = mapminmax(double(EEGdata),-1,1);
            respSet{count} = EEGdata_temp';
            count = count + 1;
        end
    end
    for channel2use = eegChannels
        % calculate itpc
        [itpc, frex] = cal_itpc(respSet, fs1, channel2use);
        itpc_t(i1, channel2use, :) = mean(itpc, 2);                
    end
end
save(['./itpc_nbd.mat'], 'itpc_t', 'frex');
end

%% plot averaged results for each condition
load('./itpc_nbd.mat');
channelindex = 22; % FC5
% channelindex = 52; % PO4
cc
figure
hold on
for i1=1:4
    itpc_t_con = squeeze(itpc_t(i1,channelindex,:));
    plot(frex, itpc_t_con, 'linewidth', 1);
end
lg = legend('+30','-30','+90','-90');
set(lg, 'fontsize',12)
xlabel('Frequency (Hz)')
ylabel('ITPC')
title('electrode FC5')
%ylim([0.44 0.48])
box on
set(gca,'fontsize',12, 'linewidth', 1)
%% %% plot the block design and non-block design ITPC for scalp-EEG
EEGDataDirs = { './itpc_bd.mat', ...  %the path for your calculated ITPC
                './itpc_nbd.mat', ...
};
for i = 1:2
load(EEGDataDirs{i});
itpc_t_all(i,:,:,:) = itpc_t;
end
itpc = mean(itpc_t_all,2);
result = squeeze(itpc);
channelindex = {26,29};%Cz,C3

figure

for i0= 1:2 % 


subplot(2,1,i0)
hold on

for i1=1:2
    final = squeeze(result(i1,channelindex{i0},:));
    plot(frex, final, 'linewidth', 1);
end

if i0 == 1
    title('Electrode Cz','FontWeight', 'bold', 'FontSize', 18, 'FontName', 'Times New Roman');
else
    title('Electrode C3','FontWeight', 'bold', 'FontSize', 18, 'FontName', 'Times New Roman');
end
lg = legend('Block Design','Non-Block Design');
set(lg, 'fontsize',16,'FontName', 'Times New Roman')
xlabel('Frequency (Hz)')
ylabel({'ITPC'})
ylim([0.06 0.09])
box on
set(gca,'fontsize',16, 'linewidth', 1,'FontName', 'Times New Roman','xtick', [0:2:20])
end