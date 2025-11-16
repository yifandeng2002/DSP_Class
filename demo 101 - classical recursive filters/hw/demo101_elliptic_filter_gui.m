function elliptic_filter_gui

    fig = figure('Name', 'Elliptic Filter Designer', ...
                 'NumberTitle', 'off', ...
                 'Position', [100, 100, 1000, 600], ...
                 'Color', [0.94 0.94 0.94]);
    
    % default
    params.order = 3;
    params.delp = 0.05;
    params.dels = 0.02;
    params.cutoff = 0.4;
    
    % control panel
    uiPanel = uipanel('Parent', fig, 'Title', 'Filter Parameters', ...
                      'FontSize', 10, 'FontWeight', 'bold', ...
                      'Position', [0.02 0.42 0.25 0.5]);
    
    % create sliders with labels
    yPos = 0.85;
    spacing = 0.16;
    
    % order
    createLabel(uiPanel, 'Filter Order:', [0.05 yPos 0.5 0.06]);
    orderLabel = createValueLabel(uiPanel, num2str(params.order), [0.75 yPos 0.2 0.06]);
    orderSlider = createSlider(uiPanel, 1, 10, params.order, [0.05 yPos-0.08 0.9 0.06]);
    
    % passband ripple
    yPos = yPos - spacing;
    createLabel(uiPanel, 'Passband Ripple:', [0.05 yPos 0.5 0.06]);
    delpLabel = createValueLabel(uiPanel, sprintf('%.3f', params.delp), [0.75 yPos 0.2 0.06]);
    delpSlider = createSlider(uiPanel, 0.001, 0.2, params.delp, [0.05 yPos-0.08 0.9 0.06]);
    
    % stopband ripple
    yPos = yPos - spacing;
    createLabel(uiPanel, 'Stopband Ripple:', [0.05 yPos 0.5 0.06]);
    delsLabel = createValueLabel(uiPanel, sprintf('%.3f', params.dels), [0.75 yPos 0.2 0.06]);
    delsSlider = createSlider(uiPanel, 0.001, 0.1, params.dels, [0.05 yPos-0.08 0.9 0.06]);
    
    % cutoff freq
    yPos = yPos - spacing;
    createLabel(uiPanel, 'Cutoff Frequency:', [0.05 yPos 0.5 0.06]);
    cutoffLabel = createValueLabel(uiPanel, sprintf('%.2f', params.cutoff/2), [0.75 yPos 0.2 0.06]);
    cutoffSlider = createSlider(uiPanel, 0.1, 0.9, params.cutoff, [0.05 yPos-0.08 0.9 0.06]);
    
    % info display
    yPos = yPos - spacing;
    infoText = uicontrol('Parent', uiPanel, 'Style', 'text', ...
                         'String', '', 'Units', 'normalized', ...
                         'Position', [0.05 0.02 0.9 0.18], ...
                         'HorizontalAlignment', 'left', ...
                         'FontSize', 9, 'BackgroundColor', [1 1 1]);
    
    % plot axes
    ax1 = axes('Parent', fig, 'Position', [0.35 0.55 0.60 0.38]);
    title('Magnitude Response'); xlabel('Frequency (cycles/sample)'); ylabel('Magnitude');
    grid on; hold on;
    
    ax2 = axes('Parent', fig, 'Position', [0.35 0.08 0.60 0.38]);
    title('Magnitude Response (dB)'); xlabel('Frequency (cycles/sample)'); ylabel('Magnitude (dB)');
    grid on; hold on;
    
    % set callbacks
    set(orderSlider, 'Callback', @updateFilter);
    set(delpSlider, 'Callback', @updateFilter);
    set(delsSlider, 'Callback', @updateFilter);
    set(cutoffSlider, 'Callback', @updateFilter);
    
    updateFilter();
    
    % update function
    function updateFilter(~, ~)
        params.order = round(get(orderSlider, 'Value'));
        params.delp = get(delpSlider, 'Value');
        params.dels = get(delsSlider, 'Value');
        params.cutoff = get(cutoffSlider, 'Value');
        
        set(orderLabel, 'String', num2str(params.order));
        set(delpLabel, 'String', sprintf('%.3f', params.delp));
        set(delsLabel, 'String', sprintf('%.3f', params.dels));
        set(cutoffLabel, 'String', sprintf('%.2f', params.cutoff/2));
        
        Rp = -20*log10(1 - params.delp);
        Rs = -20*log10(params.dels);
        
        infoStr = sprintf('Rp = %.2f dB\nRs = %.2f dB\nfc = %.2f cycles/sample\nOrder = %d', ...
                          Rp, Rs, params.cutoff/2, params.order);
        set(infoText, 'String', infoStr);
        
        % filter
        [b, a] = ellip(params.order, Rp, Rs, params.cutoff);
        [H, om] = freqz(b, a, 512);
        f = om / (2*pi);
        
        % plot linear magnitude
        cla(ax1); axes(ax1);
        plot(f, abs(H), 'b-', 'LineWidth', 1.5);
        line([0 params.cutoff/2], [1-params.delp 1-params.delp], 'Color', 'r', 'LineStyle', '--');
        line([0 params.cutoff/2], [1+params.delp 1+params.delp], 'Color', 'r', 'LineStyle', '--');
        line([params.cutoff/2 0.5], [params.dels params.dels], 'Color', 'r', 'LineStyle', '--');
        ylim([0 1.2]); xlim([0 0.5]); grid on;
        title('Magnitude Response'); xlabel('Frequency (cycles/sample)'); ylabel('Magnitude');
        
        % plot dB magnitude
        cla(ax2); axes(ax2);
        plot(f, 20*log10(abs(H)), 'b-', 'LineWidth', 1.5);
        line([0 params.cutoff/2], [-Rp -Rp], 'Color', 'r', 'LineStyle', '--');
        line([params.cutoff/2 0.5], [-Rs -Rs], 'Color', 'r', 'LineStyle', '--');
        ylim([-80 10]); xlim([0 0.5]); grid on;
        title('Magnitude Response (dB)'); xlabel('Frequency (cycles/sample)'); ylabel('Magnitude (dB)');
    end

    % helper
    function h = createLabel(parent, str, pos)
        h = uicontrol('Parent', parent, 'Style', 'text', 'String', str, ...
                      'Units', 'normalized', 'Position', pos, ...
                      'HorizontalAlignment', 'left');
    end

    function h = createValueLabel(parent, str, pos)
        h = uicontrol('Parent', parent, 'Style', 'text', 'String', str, ...
                      'Units', 'normalized', 'Position', pos, ...
                      'FontWeight', 'bold');
    end

    function h = createSlider(parent, minVal, maxVal, val, pos)
        h = uicontrol('Parent', parent, 'Style', 'slider', ...
                      'Min', minVal, 'Max', maxVal, 'Value', val, ...
                      'Units', 'normalized', 'Position', pos);
    end
end