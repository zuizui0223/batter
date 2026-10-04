function source_b_matlab_native_parser_diagnostic_v1
% Structural parser diagnostic only. No numeric coordinate values are printed.
names = ["Ali","Anka"];
for ii = 1:numel(names)
    nm = names(ii);
    fn = fullfile("prospective","ontogenetic_path_dependence","matlab_probe",nm+"_data.mat");
    S = load(fn,"data");
    assert(isfield(S,"data"),"data variable missing");
    d = S.data;
    fprintf('BEGIN %s\n',nm);
    fprintf('data_class=%s\n',class(d));
    fprintf('data_size=%s\n',mat2str(size(d)));
    assert(numel(d)>=1,"empty data");
    day = d(1);
    fprintf('day_class=%s\n',class(day));
    if isstruct(day)
        disp("day_fields="+strjoin(string(fieldnames(day))',","));
    else
        try
            disp("day_fields="+strjoin(string(properties(day))',","));
        catch
            disp("day_fields=<unavailable>");
        end
    end
    tr = day.track;
    fprintf('track_class=%s\n',class(tr));
    fprintf('track_size=%s\n',mat2str(size(tr)));
    vars = strings(0,1);
    if istable(tr) || istimetable(tr)
        vars = string(tr.Properties.VariableNames(:));
    elseif isstruct(tr)
        vars = string(fieldnames(tr));
    else
        try
            vars = string(properties(tr));
        catch
            vars = strings(0,1);
        end
    end
    disp("track_variables="+strjoin(vars',","));
    frozen = ["x","y","time"];
    for kk = 1:numel(frozen)
        vname=frozen(kk);
        present=any(vars==vname);
        fprintf('%s_present=%d\n',vname,present);
        if present
            if istable(tr) || istimetable(tr)
                v=tr.(vname);
            elseif isstruct(tr)
                if numel(tr)>1
                    v=[tr.(vname)];
                else
                    v=tr.(vname);
                end
            else
                v=tr.(vname);
            end
            fprintf('%s_class=%s\n',vname,class(v));
            fprintf('%s_size=%s\n',vname,mat2str(size(v)));
        end
    end
    fprintf('END %s\n',nm);
end
end
