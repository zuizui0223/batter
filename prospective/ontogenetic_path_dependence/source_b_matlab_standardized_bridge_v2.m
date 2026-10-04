function source_b_matlab_standardized_bridge_v2
% Parser bridge only. Implements frozen within-day standardization and writes
% simple v7 cell arrays. Calculates no between-day spatial statistic.

root = fullfile("prospective","ontogenetic_path_dependence","matlab_structural");
bridgeRoot = fullfile("prospective","ontogenetic_path_dependence","matlab_bridge_v2");
if ~exist(bridgeRoot,"dir"), mkdir(bridgeRoot); end
M = readtable(fullfile(root,"manifest.csv"),TextType="string");

cohort = strings(height(M),1);
individual = strings(height(M),1);
n_valid_days = zeros(height(M),1);
n_exported_days = zeros(height(M),1);
bridge_path = strings(height(M),1);

for ii=1:height(M)
    S=load(M.path(ii),"data");
    d=S.data;
    validDays = cell(1,0);
    for jj=1:numel(d)
        tr=d(jj).track;
        if istable(tr) || istimetable(tr)
            vars=string(tr.Properties.VariableNames);
            assert(all(ismember(["x","y","time"],vars)),"frozen x/y/time absent");
            x=tr.x; y=tr.y; tt=tr.time;
        elseif isstruct(tr)
            assert(all(isfield(tr,{"x","y","time"})),"frozen x/y/time absent");
            x=[tr.x]'; y=[tr.y]'; tt=[tr.time]';
        else
            error("unsupported native track class: %s",class(tr));
        end

        x=double(x(:)); y=double(y(:));
        if isdatetime(tt)
            sec=seconds(tt(:)-tt(1));
        elseif isduration(tt)
            sec=seconds(tt(:)-tt(1));
        else
            tt=double(tt(:));
            sec=(tt-tt(1))*86400;
        end
        if ~(numel(x)==numel(y) && numel(y)==numel(sec)), continue; end
        ok=isfinite(x)&isfinite(y)&isfinite(sec);
        x=x(ok); y=y(ok); sec=sec(ok);
        if isempty(sec), continue; end
        [sec,ord]=sort(sec,'ascend');
        x=x(ord); y=y(ord);
        bins=floor(sec/30 + 1e-9);
        keep=[true; diff(bins)~=0];
        xy=[x(keep),y(keep)];
        if size(xy,1)>=20
            validDays{end+1}=xy; %#ok<AGROW>
        end
    end

    nvalid=numel(validDays);
    nexp=min(20,nvalid);
    xyDays=validDays(1:nexp); %#ok<NASGU>

    cohort(ii)=M.cohort(ii);
    individual(ii)=M.individual(ii);
    n_valid_days(ii)=nvalid;
    n_exported_days(ii)=nexp;

    cdir=fullfile(bridgeRoot,M.cohort(ii));
    if ~exist(cdir,"dir"), mkdir(cdir); end
    outfn=fullfile(cdir,M.individual(ii)+".mat");
    save(outfn,"xyDays","-v7");
    bridge_path(ii)=string(outfn);
end

B=table(cohort,individual,n_valid_days,n_exported_days,bridge_path);
writetable(B,fullfile(bridgeRoot,"manifest.csv"));
fprintf('bridge_files=%d\n',height(B));
fprintf('complete20=%d\n',sum(B.n_exported_days>=20));
end
