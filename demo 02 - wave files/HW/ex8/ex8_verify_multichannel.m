%% read file
[y, fs] = audioread('sin_multichannel.wav');

%% get num of channels
[num_samples, num_channels] = size(y);

fprintf('Channel count: %d\n', num_channels);

%% plot
figure;
for ch = 1:num_channels
    subplot(num_channels,1,ch);
    plot(y(1:1000, ch)); % zoom into first 1000 samples
    title(['Ch' num2str(ch)]);
    xlabel('Index');
    ylabel('Amplitude');
end