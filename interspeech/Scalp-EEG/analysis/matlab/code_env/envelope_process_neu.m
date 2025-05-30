clear;clc;

dim_tr =59;

load('./space_num.mat');
load('./space_envall.mat')

att_rand = [1 1 1 1 1 1 1 1 1 1];
unatt_rand = [2 2 2 2 2 2 2 2 2 2];

Envelope_att = space_env(space_num(:,1),:);



if 1

    nowdir = cd;
    cd ..
    projectdir =  cd;
    DataDir = ['../../../preprocess_data/data_env/'];    

    cd (nowdir)    

    Lags = 0:32;
    dim = dim_tr*(length(Lags)+1);
    M = eye(dim,dim);

    sblist = dir(DataDir);
    sblist(1:2) = [];

    sbnum = size(sblist,1);
    decode_att = zeros(sbnum,40,dim);
    decode_unatt = zeros(sbnum,40,dim);

    for sb = 1:sbnum
        sbname = sblist(sb).name;
        sbdir = [DataDir filesep sbname];

        for tr = 1:40

            disp(['  sb:' num2str(sb) '  tr:' num2str(tr)]);

            trdir = [sbdir filesep num2str(tr) '_cap.mat'];
            load(trdir);
            eeg = EEG_env.data(:,:);
            eeg(dim_tr+1:64,:) = [];
            eeg = eeg';
            eeg = zscore(eeg);
            
            env_att = Envelope_att(tr,:)';


            X = [ones(size(eeg)),lagGen(eeg,min(-Lags):max(-Lags))];

            XX = X'*X;
            XYatt = X'*env_att;

            d2_att = (XX+4096*M)\XYatt;
            
            decode_att(sb,tr,:) = d2_att';
        end


    end
    save(['envelope_decoder_nue.mat'],'decode_att','decode_unatt');
end



if 1

    nowdir = cd;
    cd ..
    projectdir =  cd;
    DataDir = ['../../../preprocess_data/data_env/'];  

    cd (nowdir)
    

    Lags = 0:32;
    dim = dim_tr*(length(Lags)+1);
    M = eye(dim,dim);


    sblist = dir(DataDir);
    sblist(1:2) = [];

    res_raw =zeros(16,7);

    load('envelope_decoder_nue.mat');
    C_att_raw = zeros(sbnum,40);
    C_unatt_raw = zeros(sbnum,40);

    t = [60 30 20 10 5 2 1];
    for i= 1: length(t)
    ti = t(i);
    

    for sb = 1:sbnum
        sbname = sblist(sb).name;
        sbdir = [DataDir filesep sbname];

        for tr = 1:40
            disp(['  sb:' num2str(sb) '  tr:' num2str(tr)]);
            unattnum = space_num(tr,2:4);
            trdir = [sbdir filesep num2str(tr) '_cap.mat'];
            load(trdir);
            eeg = EEG_env.data(:,:);
            eeg(dim_tr+1:64,:) = [];
            eeg = eeg';
            eeg = zscore(eeg);

           
            env_att = Envelope_att(tr,:)';
            env_unatt = space_env(unattnum,:)';

            
            X = [ones(size(eeg)),lagGen(eeg,min(-Lags):max(-Lags))];

            decoder_raw = sum(squeeze(decode_att(sb,:,:)))' - squeeze(decode_att(sb,tr,:));
            pred_att_raw = X*decoder_raw;
            
           
                for t_n = 1:60/ti

                    C_att_raw(sb,tr,t_n) = corr(env_att(ti*64*(t_n-1)+1:ti*64*t_n,:),pred_att_raw(ti*64*(t_n-1)+1:ti*64*t_n,:));
                    C_unatt_raw(sb,tr,t_n) = max([corr(env_unatt(ti*64*(t_n-1)+1:ti*64*t_n,1),pred_att_raw(ti*64*(t_n-1)+1:ti*64*t_n,:)),corr(env_unatt(ti*64*(t_n-1)+1:ti*64*t_n,2),pred_att_raw(ti*64*(t_n-1)+1:ti*64*t_n,:)),corr(env_unatt(ti*64*(t_n-1)+1:ti*64*t_n,3),pred_att_raw(ti*64*(t_n-1)+1:ti*64*t_n,:))]);
                   
                
                end
            end


    end

        de_raw = gt(C_att_raw,C_unatt_raw);
        
     res_raw(:,i) = mean(mean(de_raw,2),3);
     disp(i);
    end

    


end



function xLag = lagGen(x,lags)
xLag = zeros(size(x,1),size(x,2)*length(lags));

i = 1;
for j = 1:length(lags)
    if lags(j) < 0
        xLag(1:end+lags(j),i:i+size(x,2)-1) = x(-lags(j)+1:end,:);
    elseif lags(j) > 0
        xLag(lags(j)+1:end,i:i+size(x,2)-1) = x(1:end-lags(j),:);
    else
        xLag(:,i:i+size(x,2)-1) = x;
    end
    i = i+size(x,2);
end

end
