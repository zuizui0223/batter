function paf_schema_audit_matlab_v2()
% STRUCTURE ONLY. No acoustic numeric feature summaries.
here=fileparts(mfilename('fullpath'));
src=fullfile(here,'PAF_AllBatsData.mat');
outjson=fullfile(here,'PAF_SCHEMA_AUDIT_V2.json');
outmd=fullfile(here,'PAF_SCHEMA_AUDIT_V2.md');

S=load(src,'PAF_Tbl');
assert(isfield(S,'PAF_Tbl'),'STOP_NO_PAF_TBL');
T=S.PAF_Tbl;
assert(istable(T),'STOP_PAF_NOT_TABLE');
assert(width(T)>=32,'STOP_EXPECTED_32_COLUMNS');

names=T.Properties.VariableNames;
structNames=names(1:4);
featureNames=names(5:32);

bat=string(T.BatID);
hd=string(T.Hearing_Deaf);
sex=string(T.Sex);
ub=unique(bat,'stable');
assert(numel(ub)==10,'STOP_EXPECTED_10_BATS');

batRows=struct('BatID',{},'n_calls',{},'hearing_deaf',{},'sex',{});
for ii=1:numel(ub)
    idx=(bat==ub(ii));
    hdu=unique(hd(idx));
    sxu=unique(sex(idx));
    assert(numel(hdu)==1 && numel(sxu)==1,'STOP_BAT_METADATA_NOT_CONSTANT');
    batRows(ii).BatID=char(ub(ii));
    batRows(ii).n_calls=sum(idx);
    batRows(ii).hearing_deaf=char(hdu);
    batRows(ii).sex=char(sxu);
end

fourth=struct;
fourth.name=structNames{4};
v=T.(structNames{4});
fourth.class=class(v);
fourth.n_rows=height(T);
try
    sv=string(v);
    levels=unique(sv);
    if numel(levels)<=100
        fourth.levels=cellstr(levels);
        counts=zeros(numel(levels),1);
        for kk=1:numel(levels)
            counts(kk)=sum(sv==levels(kk));
        end
        fourth.counts=counts;
    else
        fourth.levels={};
        fourth.counts=[];
    end
catch
    fourth.levels={};
    fourth.counts=[];
end

R=struct;
R.version=2;
R.source='10.17632/h5ff9vv5pc.1';
R.variable='PAF_Tbl';
R.table_height=height(T);
R.table_width=width(T);
R.structural_columns=structNames;
R.feature_columns=featureNames;
R.feature_count=numel(featureNames);
R.fourth_column=fourth;
R.bats=batRows;
R.n_hearing=sum(hd=="H");
R.n_deaf=sum(hd=="D");
R.n_H_F=sum(hd=="H" & sex=="F");
R.n_H_M=sum(hd=="H" & sex=="M");
R.n_D_F=sum(hd=="D" & sex=="F");
R.n_D_M=sum(hd=="D" & sex=="M");

fid=fopen(outjson,'w');
fprintf(fid,'%s\n',jsonencode(R,'PrettyPrint',true));
fclose(fid);

fid=fopen(outmd,'w');
fprintf(fid,'# Auditory-feedback PAF schema audit v2\n\n');
fprintf(fid,'**MATLAB TABLE STRUCTURE ONLY — NO ACOUSTIC FEATURE VALUES REPORTED.**\n\n');
fprintf(fid,'- rows: **%d**\n',height(T));
fprintf(fid,'- columns: **%d**\n',width(T));
fprintf(fid,'- bats: **%d**\n',numel(ub));
fprintf(fid,'- hearing/deaf rows: **%d / %d**\n',R.n_hearing,R.n_deaf);
fprintf(fid,'- H female/male rows: **%d / %d**\n',R.n_H_F,R.n_H_M);
fprintf(fid,'- D female/male rows: **%d / %d**\n',R.n_D_F,R.n_D_M);
fprintf(fid,'- fixed acoustic features: **%d** (columns 5:32)\n\n',numel(featureNames));
fprintf(fid,'## Structural columns\n\n');
for kk=1:numel(structNames), fprintf(fid,'- %d: %s\n',kk,structNames{kk}); end
fprintf(fid,'\n## Fixed feature column names\n\n');
for kk=1:numel(featureNames), fprintf(fid,'- %02d: %s\n',kk,featureNames{kk}); end
fprintf(fid,'\n## Bat support\n\n| BatID | calls | H/D | sex |\n|---|---:|---|---|\n');
for ii=1:numel(batRows)
    fprintf(fid,'| %s | %d | %s | %s |\n',batRows(ii).BatID,batRows(ii).n_calls,batRows(ii).hearing_deaf,batRows(ii).sex);
end
fprintf(fid,'\n## Structural fourth column\n\n- name: %s\n- class: %s\n',fourth.name,fourth.class);
if isfield(fourth,'levels') && ~isempty(fourth.levels)
    for kk=1:numel(fourth.levels), fprintf(fid,'- level %s: %d rows\n',fourth.levels{kk},fourth.counts(kk)); end
end
fprintf(fid,'\nNo acoustic value, centroid, identity score, treatment effect, or dispersion was calculated.\n');
fclose(fid);

delete(src);
end
