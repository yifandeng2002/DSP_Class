%%
[x, fs] = audioread('sin_8bit_220Hz.wav');
N = length(x);
t = (0:N-1).'/fs;

%%  plot a waveform
seg = 1:min(round(5*fs/floor(fs/440)), N);
figure; plot(t(seg), x(seg), '.-'); grid on;
xlabel('Time(s)'); ylabel('Amplitude');
title('8 bit sin wave');

%% estimate quantization step size
dx = diff(x);
dx_nz = dx(abs(dx) > 0);
est_step = median(abs(dx_nz));
fprintf('Estimated quantization step ≈ %.6f \n', ...
    est_step);

%% spectrum
X = fft(x .* hann(N));
f = (0:N-1)' * (fs/N);
mag_db = 20*log10(abs(X)+eps);

%% plot
figure; plot(f(1:floor(N/2)), mag_db(1:floor(N/2)));
grid on; xlabel('Frequency(Hz)'); ylabel('Magnitude(dBFS)');
xlim([0 fs/2]);