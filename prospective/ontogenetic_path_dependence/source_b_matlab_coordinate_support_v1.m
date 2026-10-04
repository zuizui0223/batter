function source_b_matlab_coordinate_support_v1
% MATLAB-native implementation of the already-frozen coordinate structural gate.
% Reports counts only; does not calculate spatial distances or route outcomes.

root = fullfile("prospective","ontogenetic_path_dependence","matlab_structural");
M = readtable(fullfile(root,"manifest.csv"),TextType="string");
out = table('Size',[height(M),5], ...
    'VariableTypes',["string","string","double","double","logical"], ...
    'VariableNames',["cohort","individual","n_source_day_objects","n_valid_movement_days","passes_20"]);
for ii=1:height(M)
    S=load(M.path(ii),"data");
    assert(isfield(S,"data"),"data missing");
    d=S.data;
    nsrc=numel(d);
    nvalid=0;
    for jj=1:nsrc
        tr=d(jj).track;
        if isempty(tr), continue; end
        if istable(tr) || istimetable(tr)
            vars=string(tr.Properties.VariableNames);
            if ~all(ismember(["x","y","time"],vars)), continue; end
            x=tr.x; y=tr.y; tt=tr.time;
        elseif isstruct(tr)
            if ~all(isfield(tr,{"x","y","time"})), continue; end
            x=[tr.x]'; y=[tr.y]'; tt=[tr.time]';
        else
            continue;
        end
        if isempty(x) || isempty(y) || isempty(tt), continue; end
        try
            x=double(x(:)); y=double(y(:));
            if isdatetime(tt)
                sec=seconds(tt(:)-tt(1));
            elseif isduration(tt)
                sec=seconds(tt(:)-tt(1));
            else
                tt=double(tt(:));
                sec=(tt-tt(1))*86400;
            end
        catch
            continue;
        end
        if ~(numel(x)==numel(y) && numel(y)==numel(sec)), continue; end
        ok=isfinite(x)&isfinite(y)&isfinite(sec);
        x=x(ok); y=y(ok); sec=sec(ok); %#ok<NASGU>
        if isempty(sec), continue; end
        [sec,ord]=sort(sec,'ascend'); %#ok<ASGLU>
        bins=floor(sec/30 + 1e-9);
        nstd=1+sum(diff(bins)~=0);
        if nstd>=20, nvalid=nvalid+1; end
    end
    out.cohort(ii)=M.cohort(ii);
    out.individual(ii)=M.individual(ii);
    out.n_source_day_objects(ii)=nsrc;
    out.n_valid_movement_days(ii)=nvalid;
    out.passes_20(ii)=nvalid>=20;
end

cNames=unique(out.cohort);
fprintf('BEGIN_STRUCTURAL_RESULT\n');
for cc=1:numel(cNames)
    c=cNames(cc);
    n=sum(out.cohort==c & out.passes_20);
    fprintf('cohort=%s pass20=%d total=%d\n',c,n,sum(out.cohort==c));
end
fprintf('total_pass20=%d total=%d\n',sum(out.passes_20),height(out));
fprintf('eligible=');
eligible=out.individual(out.passes_20);
fprintf('%s',strjoin(eligible',','));
fprintf('\nEND_STRUCTURAL_RESULT\n');

writetable(out,fullfile(root,"SOURCE_B_MATLAB_COORDINATE_SUPPORT_RESULT_V1.csv"));
end
