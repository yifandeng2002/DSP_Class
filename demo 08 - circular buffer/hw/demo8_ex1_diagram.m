clear all; close all;

% Parameters
b0 = 1.0;
G = 0.8;
RATE = 44100;
N = round(RATE * 0.05);  % N = 2205 samples

%% Impulse Response
figure;
n_samples = N + 500;
h = zeros(1, n_samples);
h(1) = b0;
h(N+1) = G;
n = 0:n_samples-1;

stem(n, h, 'b', 'LineWidth', 1);
grid on;
xlabel('Sample n');
ylabel('h(n)');
title('Impulse Response');
xlim([0 n_samples-1]);

%% Pole-Zero Diagram
figure;
magnitude = abs(-G)^(1/N);
angles = (angle(-G) + 2*pi*(0:N-1)) / N;
zeros_z = magnitude * exp(1j * angles);
zeros_z = zeros_z(:);
poles_z = zeros(N, 1);

zplane(zeros_z, poles_z);
title(sprintf('Pole Zero Diagram N=%d', N));
grid on;