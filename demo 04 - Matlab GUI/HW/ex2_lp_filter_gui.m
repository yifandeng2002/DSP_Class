function ex2_gui
    
    % --- layout ---
    fig = uifigure('Name', 'Filter GUI', 'Position', [100 100 600 600]);
    gl = uigridlayout(fig,[3 1]); % freq plot, impulse plot, slider
    gl.RowHeight = {'1x','1x',60};
    gl.ColumnWidth = {'1x'};
    
    % --- axes for frequency response ---
    ax1 = uiaxes(gl);
    ax1.Layout.Row = 1; ax1.Layout.Column = 1;
    title(ax1,'Frequency Response');
    xlabel(ax1,'Frequency (Hz)'); ylabel(ax1,'|H(f)|');
    
    % --- axes for impulse response ---
    ax2 = uiaxes(gl);
    ax2.Layout.Row = 2; ax2.Layout.Column = 1;
    title(ax2,'Impulse Response');
    xlabel(ax2,'Samples'); ylabel(ax2,'Amplitude');
    
    % --- slider ---
    slider = uislider(gl, ...
        'Limits',[100 5000], ...
        'Value',1000, ...
        'MajorTicks',[100 1000 5000], ...
        'MinorTicks',[], ...             
        'ValueChangedFcn',@(s,~) updatePlots(s.Value));
    slider.Layout.Row = 3; 
    slider.Layout.Column = 1;
    
    % --- plot ---
    updatePlots(slider.Value);
    
    % --- update ---
    function updatePlots(fc)
        fs = 16000;          % sr
        [b,a] = butter(6, fc/(fs/2));  % 6th order butterworth LPF
        
        % frequency response
        [h,w] = freqz(b,a,512,fs);
        plot(ax1,w,abs(h),'LineWidth',1.5);
        grid(ax1,'on');
        ylim(ax1,[0 1.2]);
        title(ax1,sprintf('Frequency Response (fc = %.0f Hz)',fc));
        
        % impulse response
        imp = [1; zeros(127,1)];
        resp = filter(b,a,imp);
        plot(ax2,resp,'LineWidth',1.5);
        grid(ax2,'on');
        ylim(ax2,[-0.5 1]);
        title(ax2,'Impulse Response');
    end
end