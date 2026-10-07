function paf_callclass_support_v1()
% STRUCTURAL SUPPORT ONLY. No acoustic feature magnitudes.
here=fileparts(mfilename('fullpath'));
src=fullfile(here,'PAF_AllBatsData.mat');
outjson=fullfile(here,'PAF_CALLCLASS_SUPPORT_V1.json');
outmd=fullfile(here,'PAF_CALLCLASS_SUPPORT_V1.md');

S=load(src,'PAF_Tbl');
T=S.PAF_Tbl;
assert(istable(T),'STOP_PAF_NOT_TABLE');

bat=string(T.BatID);
grp=string(T.("Acoustic Group"));
ub=unique(bat,'stable');
ug=sort(unique(grp));
assert(numel(ub)==10,'STOP_EXPECTED_10_BATS');

% Frozen acoustic features are columns 5:32.
X=T{:,5:32};
if ~isnumeric(X)
    error('STOP_FEATURE_MATRIX_NOT_NUMERIC');
end
finiteRow=all(isfinite(X),2);

records=struct('BatID',{},'AcousticGroup',{},'n_calls',{},'n_complete28',{});
kk=0;
groupPass=false(numel(ug),1);

for gi=1:numel(ug)
    allbat=true;
    support20=true;
    for bi=1:numel(ub)
        idx=(bat==ub(bi) & grp==ug(gi));
        n=sum(idx);
        nf=sum(idx & finiteRow);
        kk=kk+1;
        records(kk).BatID=char(ub(bi));
        records(kk).AcousticGroup=char(ug(gi));
        records(kk).n_calls=n;
        records(kk).n_complete28=nf;
        if n==0, allbat=false; end
        if nf<20, support20=false; end
    end
    groupPass(gi)=allbat && support20;
end

passgroups=ug(groupPass);
if ~isempty(passgroups)
    architecture='CLASS_CONDITIONED';
    selected=passgroups(1);
else
    architecture='WHOLE_REPERTOIRE_CLASS_RESIDUALIZED';
    selected="";
end

R=struct;
R.version=1;
R.groups=cellstr(ug);
R.records=records;
R.pass_groups=cellstr(passgroups);
R.architecture=architecture;
R.selected_group=char(selected);

fid=fopen(outjson,'w');
fprintf(fid,'%s\n',jsonencode(R,'PrettyPrint',true));
fclose(fid);

fid=fopen(outmd,'w');
fprintf(fid,'# Auditory-feedback call-class support v1\n\n');
fprintf(fid,'**STRUCTURAL COUNTS ONLY — NO ACOUSTIC MAGNITUDES.**\n\n');
fprintf(fid,'- groups: %s\n',strjoin(cellstr(ug),', '));
fprintf(fid,'- architecture: **%s**\n',architecture);
if strlength(selected)>0
    fprintf(fid,'- selected group: **%s**\n',selected);
end
fprintf(fid,'\n| BatID | Group | calls | complete 28-feature calls |\n|---|---|---:|---:|\n');
for ii=1:numel(records)
    fprintf(fid,'| %s | %s | %d | %d |\n',records(ii).BatID,records(ii).AcousticGroup,records(ii).n_calls,records(ii).n_complete28);
end
fprintf(fid,'\nNo acoustic value, identity score, or treatment effect was calculated.\n');
fclose(fid);
end
