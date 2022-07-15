%% Ian Delgadillo Bonequi
clear all;
close all;
clc;
%% Plotting Cmd Signal

%Grab CMD data from .h5 file
y = hdf5read('SeriesResData\alpha_0.7_data.h5','/adc');
cmd_data = y(2:2:end,5);
t = (1:length(cmd_data))*400e-3;

%plot CMD
figure(1);
subplot(2, 1, 1);
plot(t, cmd_data, '-*');
xlim([6450 6750]);
ylim([5000 9200]);
grid on;
title('Cmd Signal Summed With Filtered Current Measurements');
xlabel('t (μs)');
ylabel('Hexadecimal DAC Codes');

%Now zoomed in plot
subplot(2, 1, 2);
plot(t, cmd_data, '-*');
xlim([6548 6565]);
ylim([7000 7800]);
grid on;
title('Zoomed In On Discontinuity');
xlabel('t (μs)');
ylabel('Hexadecimal DAC Codes');
saveas(figure(1), 'EndToEndLatencyMeasMATLAB.png');

%% Plotting Cmd Signal and Current on Same Plot

%Grab Im data from .h5 file
current_data = dec2bin(y(:,1));
current_data = typecast(uint16(bin2dec(current_data)), 'int16');

%5 MSPS time array
t2 = (1:length(current_data))*200e-3;

%plot CMD
figure(2);
subplot(2, 1, 1);
plot(t, cmd_data, '-*');
hold on;

%plot Im
plot(t2, current_data*0.125 + 8192, '-*');
xlim([6450 6750]);
ylim([5000 12000]);
grid on;
title('Cmd Signal Summed and Filtered Current Measurements');
xlabel('t (μs)');
ylabel('Hexadecimal DAC/ADC Codes');
legend('CMD', 'Current Meas', 'Location', 'southwest');

%Now, zoomed in plot
subplot(2, 1, 2);
plot(t, cmd_data, '-*');
hold on;
plot(t2, current_data*0.125 + 8192, '-*');
xlim([6548 6565]);
ylim([7000 8500]);
grid on;
title('Zoomed In On Discontinuity');
xlabel('t (μs)');
ylabel('Hexadecimal DAC/ADC Codes');
legend('CMD', 'Current Meas', 'Location', 'southwest');
saveas(figure(2), 'FilterLatencyMeasMATLAB.png');

%% Plot CMD, Im, P1, and Vm

f = figure(3);
t = t-3277.2;
t2 = t2-3277.2;
% f.Units('normalized');
% f.Position(3:4) = [1 1];
set(gcf, 'Position', get(0, 'Screensize'));
tiledlayout('flow', 'TileSpacing', 'compact')
a = nexttile;
b = nexttile;
c = nexttile;
d = nexttile;

for alpha = [0.0, 0.25, 0.5, 0.75]

    %Special case for α=0 .h5 file
    if(alpha == 0)
        y = hdf5read(['SeriesResData\alpha_0.0_data.h5'],'/adc');
    else
        y = hdf5read(['SeriesResData\alpha_', num2str(alpha, 2), '_data.h5'],'/adc');
    end

    %Grab CMD, Im, P1, and Vm data from .h5 file
    cmd_data = y(2:2:end,5);
    current_data = dec2bin(y(:,1));
    current_data = typecast(uint16(bin2dec(current_data)), 'int16');
    p1_data = dec2bin(y(1:10:end,8));
    p1_data = typecast(uint16(bin2dec(p1_data)), 'int16');
    vm_data = dec2bin(y(2:10:end,8));
    vm_data = typecast(uint16(bin2dec(vm_data)), 'int16');

    %1 MSPS time array
    t3 = (1:length(p1_data))*2000e-3;
    t3 = t3-3277.2;
    
    %Plot CMD for current α
    axes(a);
    plot(t, cmd_data, '-*', 'LineWidth', 2);
    xlim([-100 150]);
    hold on;
    
    %Plot Im for current α
    axes(b)
    plot(t2, current_data, '-*', 'LineWidth', 2);
    xlim([-100 150]);
    hold on;
    
    %Plot P1 for current α
    axes(c);
    plot(t3, p1_data, '-*', 'LineWidth', 2);
    xlim([-100 150]);
    hold on;

    %Plot Vm for current α
    axes(d)
    plot(t3, vm_data, '-*', 'LineWidth', 2);
    xlim([-100 200]);
    hold on;
end

%Axes label for CMD
axes(a);
title('CMD');
xlabel('t (μs)');
ylabel('Hexadecimal DAC Codes');
grid on;

%Axes label for Im
axes(b);
title('Im');
xlabel('t (μs)');
ylabel('Hexadecimal ADC Codes');
grid on;

%Axes label for P1
axes(c);
title('P1 (tracks Vm)');
xlabel('t (μs)');
ylabel('Hexadecimal ADS Codes');
grid on;

%Axes label for Vm
axes(d);
title('Vm');
xlabel('t (μs)');
ylabel('Hexadecimal ADS Codes');

%Shared Legend
lgd = legend('α=0', 'α=0.25','α=0.5', 'α=0.75', 'Location', 'northeast');
%set(lgd,'position',[0 0 0.5 0.5]);
lgd.FontSize = 18;
lgd.Location = 'northeastoutside';
grid on;

saveas(figure(3), 'series_res_comp_data_full.png');
