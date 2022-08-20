function Ttex = table2latex(T, label, caption, options)
%     table2latex converts a table to the tabular form for use in LaTeX.
%
%     Input arguments
%     T: a table of elements
%     label: the label for references to the table. Default: Empty.
%     caption: the caption of the table. Default: Empty. 
%     
%	  Name Value Pair Arguments 
%     SelectedColumns: index vector of table columns that need to be
%     printed. Default: All columns.
%     ColumnWidths: the widths for each column. Default: Equally adjusted
%     width.
%     IsLandscape: flag to rotate table to landscape mode. Default:
%     Vertical mode.
%     Notes: a cell array of additional notes after the table. Default: Not
%     used. 
%     IsAfterpage: flag to execute commands after pagebreak. Default: no
%     afterpage.
%     Style: the style of the output table, chooese between 
%	  {"minimal", "caged"}. Default: "minimal"
%
%     Output arguments
%     Ttex: the formatted text for the table
%
%     Dependencies
%     None
%
%     LaTeX requirements for landscape view:
%     \usepackage{afterpage}
%     \usepackage{pdflscape} %rotates page
%
%     Usage
%     Ttex = table2latex(T);
%     Ttex = table2latex(T, 'tab:table1', 'Experimental Values');
%     Ttex = table2latex(T, 'tab:table1', 'Experimental Values', ...
%		'SelectedColumns', [1:5], 'IsLandscape', false, 'Style', 'caged', ...
%       'Notes', {'These are example values.'});
% 
%     The function prints the formatted table, which then
%     can be copied and pasted to LaTeX as is.
%
%
%     Created by foxelas [https://github.com/foxelas/] (2020)

arguments
    T 
    label char = ''
    caption char = ''
    options.SelectedColumns = []
    options.ColumnWidths = []
    options.IsLandscape logical = false
    options.Notes = {}
    options.IsAfterpage logical = false
    options.Style string {mustBeMember(options.Style,["caged","minimal"])} = "minimal"
end

hasHeader = istable(T);
if hasHeader
    v = table2cell(T);
elseif iscell(T)
    v = T;
else
    error('Unsupported file format.');
end

rows = size(v, 1);

selectedCols = options.SelectedColumns;
if nargin < 2 || isempty(selectedCols)
    columns = size(v, 2);
    selectedCols = 1:columns;
else
    columns = numel(selectedCols);
end

colWidths = options.ColumnWidths;
isLandscape = options.IsLandscape;
notes = options.Notes; 
isAfterpage = options.IsAfterpage;

symb = ' & ';
slant = '\\';

if strcmpi(options.Style, "minimal")
    titleSep = strcat(slant, 'hline');
    bodySep =  '';
    columnSep = '';
elseif strcmpi(options.Style, "caged")
    titleSep = strcat(slant, 'hline');
    bodySep =  strcat(slant, 'hline');
    columnSep = '|';
else
    titleSep = strcat(slant, 'hline');
    bodySep =  strcat(slant, 'hline');
    columnSep = '|';
end

hasNotes = ~isempty(notes);


textRows = cell(2+rows+1, 1);
curRows = 1;

if isAfterpage 
    textRows{curRows} = strcat(slant, 'afterpage{\n\n');
    curRows = curRows + 1;
end 

if isLandscape 
    textRows{curRows} = strcat(slant, 'begin{landscape}\n');
    curRows = curRows + 1;
end 

strParts = {slant, 'begin{table}[htb]\n', slant, 'caption{', caption, '}\n', slant, 'begin{center}\n', slant, 'label{tab:', label, '}\n{', slant, 'tt', '\n'};
    
textRows{curRows} = strcat(strParts{:});
curRows = curRows + 1; 
textRows{curRows} = strcat(slant, 'begin{tabular}{', columnSep);


if length(colWidths) ~= columns
    disp('Incorrect number of column widths');
end

for ii = 1:columns
    if isempty(colWidths)
        textRows{curRows} = strcat(textRows{curRows}, 'c', columnSep);
    else
        textRows{curRows} = strcat(textRows{curRows}, 'p{', num2str(colWidths(ii)), 'cm}', columnSep);
    end
end
textRows{curRows} = strcat(textRows{curRows}, '}', titleSep);

if hasHeader
    curRows = curRows + 1;
    textRows{curRows} = strcat(strjoin(cellfun(@(x) convertCell(strrep(x, '_1', ''), hasHeader), T.Properties.VariableNames(selectedCols),...
        'UniformOutput', false), symb), slant, slant, titleSep);
end

hasExtraHeader = false; 
for ii = 1:rows
    curRows = curRows + 1;
    if sum(cellfun(@(x)sum(ismissing(x)) == numel(x), v(ii, selectedCols))) == numel(v(ii, selectedCols))
        hasExtraHeader = true; 
        textRows{curRows} = '';
    elseif hasExtraHeader
        textRows{curRows} = titleSep;
        curRows = curRows + 1;
        textRows{curRows} = strcat(strjoin(cellfun(@(x) convertCell(x, true), v(ii, selectedCols), 'UniformOutput', false), symb), slant, slant, bodySep);
        curRows = curRows + 1;
        textRows{curRows} = titleSep;
        hasExtraHeader = false;
    else
        textRows{curRows} = strcat(strjoin(cellfun(@(x) convertCell(x), v(ii, selectedCols), 'UniformOutput', false), symb), slant, slant, bodySep);
    end
end

curRows = curRows + 1;
if hasNotes 
    strParts = {slant, 'end{tabular}\n}\n', slant, 'end{center}\n'};
    textRows{curRows} = strcat(strParts{:});
    for j = 1:numel(notes)
        curRows = curRows + 1;
        if j ~= numel(notes)
            strParts = {notes{j}, slant, slant '\n'};
        else
            strParts = {notes{j}, '\n'};
        end
        textRows{curRows} = strcat(strParts{:});
    end 
    strParts = {slant, 'end{table}', '\n\n'};
    curRows = curRows + 1;
    textRows{curRows} = strcat(strParts{:});
else 
    strParts = {slant, 'end{tabular}\n}\n', slant, 'end{center}\n', slant, 'end{table}', '\n\n'};
    textRows{curRows} = strcat(strParts{:});
end

if isLandscape 
    curRows = curRows + 1;
    textRows{curRows} = strcat(slant, 'end{landscape}\n');
end 

if isAfterpage 
    curRows = curRows + 1;
    textRows{curRows} = '\n}';
end 

Ttex = strjoin(textRows,'\n');
fprintf(Ttex);

end

function xnew = convertCell(x, hasHeader)
if nargin < 2 
    hasHeader = false;
end 
if ~isempty(x) && ~strcmp(x, '')
    if strcmpi(x, 'na') | isnan(x)
        xnew = 'N/A';
    elseif  (isnumeric(x) & (x <1))
         xnew = num2str(x * 100, '%.1f');
        xnew = strcat(xnew, '\\%%');   
        
    elseif (ischar(x) && ~isnan(str2double(x)))
        xnew = num2str(str2double(x) * 100, '%.2f');
        xnew = strcat(xnew, '\\%%');

    elseif ischar(x)
        xnew = strrep(x, '%', '\\%%'); 
        xnew = strrep(xnew, '&', '\\&');
        xnew = strrep(xnew, '_', '\\_');
        xnew = strrep(xnew, '\cite', '\\cite');
    elseif isnumeric(x)
        if floor(x)==x
            xnew = num2str(x, '%d');
        else
            xnew = num2str(x, '%.3f');
        end
    elseif islogical(x)
        logVals = {'F', 'T'};
        xnew = logVals{x+1};
    end

    if hasHeader 
        xnew = strcat('\\', 'textbf{', xnew , '}');
    end
else 
    xnew = ' ';
end

end