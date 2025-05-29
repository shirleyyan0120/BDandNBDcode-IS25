function [itpc, frex] = cal_itpc(respSet, fs1, channel2use)
% codes are based on https://github.com/AndreiZn/Tutorial_neural_time_series_analysis/tree/master/2_Morlet_wavelet_convolution
% and http://mikexcohen.com/lectures.html

trials_num = size(respSet,2);
trial_len = size(respSet{1, 1}, 1);

% organize eegdata
eegdata = [];
for i0=1:trials_num
    eegdata = [eegdata; respSet{1,i0}(:,channel2use)];
end
eegdata = eegdata';

% wavelet parameters
num_frex = 40;
min_freq =  1;
max_freq = 20;
range_cycles = [4 10];% set range for variable number of wavelet cycles
% other wavelet parameters
frex = logspace(log10(min_freq), log10(max_freq),num_frex);
wavecycles = logspace(log10(range_cycles(1)), log10(range_cycles(end)), num_frex);
time = -2:1/fs1:2;
half_wave_size = (length(time)-1)/2;

% FFT parameters
nWave = length(time);
nData = trial_len * trials_num;
nConv = nWave + nData - 1;

% FFT of data (doesn't change on frequency iteration)
dataX = fft(eegdata, nConv);

% initialize output time-frequency data
itpc = zeros(num_frex, trial_len);

% loop over frequencies
for fi=1:num_frex
    
    % create wavelet and get its FFT
    s = wavecycles(fi)/(2*pi*frex(fi));
    wavelet  = exp(2*1i*pi*frex(fi).*time) .* exp(-time.^2./(2*s^2));
    waveletX = fft(wavelet, nConv);
    
    % run convolution
    as = ifft(waveletX.*dataX, nConv);
    as = as(half_wave_size+1:end-half_wave_size);
    as = reshape(as,trial_len, trials_num);
    
    % compute ITPC
    phase = atan2(imag(as), real(as)); % angle(as)
    itpc(fi,:) = abs(mean(exp(1i*phase), 2)); 
end


