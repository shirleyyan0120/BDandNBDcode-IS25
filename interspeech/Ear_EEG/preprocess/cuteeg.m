clear
clc
% add your eeglab address,or you can add the path to dir
% addpath(genpath('D:\eeglab_current\eeglab2022.0'));
% rmpath(genpath('D:\eeglab_current\eeglab2022.0/plugins/Fieldtrip-lite20220630/external/signal/'));

Trial_num=40;
Trial_timelen=60;

DataDir = '../rawdata';
SaveDir = '../preprocess_data/';

sblist = dir(DataDir);
sblist(1:2) = [];
Subject_num = size(sblist,1);

for sb = 1:Subject_num
    sbname = sblist(sb).name;

    rawdatadir = [DataDir filesep sbname filesep];
    
   
    ttt = dir([rawdatadir '*Poly5']);
    
    poly5name = ttt.name;
    eegpoly5path = [rawdatadir poly5name];
    filepath =[rawdatadir ];
    if sb <10

        savepath_env = [SaveDir filesep 'data_env' filesep 'sb00' num2str(sb)];
        savepath_space = [SaveDir filesep 'data_space' filesep 'sb00' num2str(sb)];
    else

        savepath_env = [SaveDir filesep 'data_env' filesep 'sb0' num2str(sb)];
        savepath_space = [SaveDir filesep 'data_space' filesep 'sb0' num2str(sb)];
    end

    if ~exist(savepath_env,'dir')
        mkdir(savepath_env)
    end

    if ~exist(savepath_space,'dir')
        mkdir(savepath_space)
    end

    

    EEG = Poly5toEEGlab(eegpoly5path,filepath);

    
    trial_lag=0;

    %
    % trigger
    for i =1:length(EEG.chanlocs)
        if string(EEG.chanlocs(i).labels) == 'TRIGGERS1'
            tr_num = i;
            break
        end
    end

  
   
        data = EEG.data;
        real = data(tr_num,:);
        for i =1:15
            real =real +data(tr_num+i,:)*(2^i);
        end
        for i =1:length(real)
            if real(i)==0
                real(i:end)=[];
                break
            end
        end
        real_tr=real(find(real~=255));  
        

        d = find(real~=255);
        dd =diff(d);
        d(find(dd<10)+1)=[];
        real_tr(find(dd<10)+1)=[];
        real_tr =255-real_tr;

   

    EEG.data(21:end,:)= [];
    EEG.chanlocs(:,21:end)= [];

    EEG = eeg_checkset( EEG );
    
    Trigger_latency = d';
    
     EEG.event=[];
        for Trigger_cnt=1:length(real_tr)
            EEG.event(Trigger_cnt).latency = Trigger_latency(Trigger_cnt);
            EEG.event(Trigger_cnt).type = real_tr(Trigger_cnt);
        end
    
    %there's some data transmission error during recording, fix it.
    if sb==2
        EEG.event(43).type=28;
    end
     if sb==8
        EEG.event(41).type=25;
    end
    if sb==9
        EEG.event(60).type=18;
    end
    if sb==13
        EEG.event(20).type=33;
    end
    if sb==15
        EEG.event(22).type=33;
    end
    
         k = [];
        for i = 1:length(EEG.event)-1;
            
            if EEG.event(i).type==EEG.event(i+1).type;
                if not(isempty(k))
                    if i-k(end)==1
                        k(end)=[];
                    end
                end
                
                k = [k,i];
            end
        end
       
        EEG.event = EEG.event(k);
    

   EEG_64 = EEG;
   
   for eegcnt=1:40
        [EEG_trial_cap,indices] = pop_epoch( EEG_64, {  EEG.event(eegcnt).type  }, [0  Trial_timelen], 'newname', 'CNT file resampled epochs', 'epochinfo', 'yes','eventindices',eegcnt);
        EEG_trial_cap = eeg_checkset( EEG_trial_cap );

        
        EEG_env = EEG_trial_cap;
        EEG_space = EEG_trial_cap;
        
        % for the stimulus reconstruction method,band-pass filtering, 2-8 Hz
        [EEG_env,com,b] = pop_eegfiltnew(EEG_env,2,8,4096,0,[],0);
        
        EEG_env = pop_rmbase( EEG_env, []);

        % downsample
        EEG_env = pop_resample( EEG_env, 64);
        EEG_space = pop_resample( EEG_space, 128);
        if EEG.event(eegcnt).type <10
            a = [savepath_env  filesep 'tr00' num2str((EEG.event(eegcnt).type))]
            b = [savepath_space filesep 'tr00' num2str((EEG.event(eegcnt).type))]
        else
            a = [savepath_env  filesep 'tr0' num2str((EEG.event(eegcnt).type))]
            b = [savepath_space filesep 'tr0' num2str((EEG.event(eegcnt).type))]
        end

        if ~exist(a,'dir')
            mkdir(a)
        end

        if ~exist(b,'dir')
            mkdir(b)
        end

        save_envname=[a filesep  num2str((EEG.event(eegcnt).type)) '_cap'];
        save_spacename=[b filesep  num2str((EEG.event(eegcnt).type)) '_cap'];
        
        save([save_envname '.mat'],'EEG_env');
        save([save_spacename '.mat'],'EEG_space');
        
        disp(['preprocessing Done! You saved the ' save_envname ]);
        disp(['preprocessing Done! You saved the ' save_spacename ]);
        
    end
end