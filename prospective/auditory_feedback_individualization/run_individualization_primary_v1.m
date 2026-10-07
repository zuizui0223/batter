function run_individualization_primary_v1()
% Frozen randomized developmental auditory-feedback individualization primary.
% Contract: PRIMARY_INDIVIDUALIZATION_CONTRACT_V1.md

here=fileparts(mfilename('fullpath'));
src=fullfile(here,'PAF_AllBatsData.mat');
outjson=fullfile(here,'PRIMARY_RESULT_V1.json');
outmd=fullfile(here,'PRIMARY_RESULT_V1.md');

S=load(src,'PAF_Tbl');
T=S.PAF_Tbl;
names=T.Properties.VariableNames;
featNames=names(5:32);
assert(numel(featNames)==28,'STOP_EXPECTED_28_FEATURES');

bat=string(T.BatID);
sex=string(T.Sex);
hd=string(T.Hearing_Deaf);
ub=unique(bat,'stable');
assert(numel(ub)==10,'STOP_EXPECTED_10_BATS');

M=nan(10,28);
support=zeros(10,28);
batSex=strings(10,1);
obsH=false(10,1);

for ii=1:10
    idx=(bat==ub(ii));
    sx=unique(sex(idx));
    tr=unique(hd(idx));
    assert(numel(sx)==1 && numel(tr)==1,'STOP_METADATA_DRIFT');
    batSex(ii)=sx;
    obsH(ii)=(tr=="H");
    for kk=1:28
        x=double(T.(featNames{kk})(idx));
        ok=isfinite(x);
        support(ii,kk)=sum(ok);
        if support(ii,kk)<100
            error('STOP_28D_BAT_CENTROID_SUPPORT: %s %s n=%d',ub(ii),featNames{kk},support(ii,kk));
        end
        M(ii,kk)=mean(x(ok));
    end
end

assert(sum(obsH)==5,'STOP_EXPECTED_5_HEARING');
assert(sum(batSex=="F" & obsH)==3,'STOP_EXPECTED_3_HEARING_FEMALES');
assert(sum(batSex=="M" & obsH)==2,'STOP_EXPECTED_2_HEARING_MALES');

mu=mean(M,1);
sd=std(M,0,1);
assert(all(isfinite(sd) & sd>0),'STOP_BAD_BAT_CENTROID_SCALE');
Z=(M-mu)./sd;

[Dobs,VHobs,VDobs,resObs]=calcD(Z,batSex,obsH);

F=find(batSex=="F");
Midx=find(batSex=="M");
cf=nchoosek(F,3);
cm=nchoosek(Midx,2);
assert(size(cf,1)*size(cm,1)==120,'STOP_EXPECTED_120_ASSIGNMENTS');

nullD=nan(120,1);
assignments=false(120,10);
cc=0;
for ff=1:size(cf,1)
    for mm=1:size(cm,1)
        cc=cc+1;
        h=false(10,1);
        h(cf(ff,:))=true;
        h(cm(mm,:))=true;
        assignments(cc,:)=h;
        nullD(cc)=calcD(Z,batSex,h);
    end
end
assert(cc==120);

tol=1e-12;
extreme=sum(abs(nullD)>=abs(Dobs)-tol);
p=extreme/120;

% Observed assignment must occur once.
obsRows=sum(all(assignments==obsH',2));
assert(obsRows==1,'STOP_OBSERVED_ASSIGNMENT_NOT_UNIQUE');

% Complement symmetry audit.
for rr=1:120
    comp=~assignments(rr,:)';
    match=find(all(assignments==comp',2),1);
    assert(~isempty(match),'STOP_COMPLEMENT_MISSING');
    assert(abs(nullD(rr)+nullD(match))<1e-10,'STOP_COMPLEMENT_SYMMETRY');
end

% Sex-specific descriptive contrasts using the same treatment labels.
Df=calcDsex(Z,batSex,obsH,"F");
Dm=calcDsex(Z,batSex,obsH,"M");

sqnorm=sum(resObs.^2,2);

R=struct;
R.version=1;
R.source='10.17632/h5ff9vv5pc.1';
R.n_bats=10;
R.n_features=28;
R.feature_names=featNames;
R.bat_ids=cellstr(ub);
R.sex=cellstr(batSex);
R.observed_treatment=cellstr(repmat("D",10,1));
for ii=1:10
    if obsH(ii), R.observed_treatment{ii}='H'; end
end
R.min_finite_calls_per_bat_feature=min(support,[],2);
R.global_min_finite_calls=min(support,[],'all');
R.V_hearing=VHobs;
R.V_deaf=VDobs;
R.D_hearing_minus_deaf=Dobs;
R.D_female_descriptive=Df;
R.D_male_descriptive=Dm;
R.per_bat_squared_residual_norm=sqnorm;
R.n_assignments=120;
R.extreme_assignments=extreme;
R.p_exact_two_sided=p;
R.null_D=nullD;
if p<=0.05
    if Dobs>0
        verdict='HEARING_MORE_DIFFERENTIATED';
    elseif Dobs<0
        verdict='DEAF_MORE_DIFFERENTIATED';
    else
        verdict='NO_DIFFERENCE_IN_AMOUNT';
    end
else
    verdict='NO_DIFFERENCE_IN_AMOUNT';
end
R.verdict=verdict;

fid=fopen(outjson,'w');
fprintf(fid,'%s\n',jsonencode(R,'PrettyPrint',true));
fclose(fid);

fid=fopen(outmd,'w');
fprintf(fid,'# Auditory-feedback adult vocal individualization result v1\n\n');
fprintf(fid,'- bats = **10**\n');
fprintf(fid,'- fixed acoustic features = **28**\n');
fprintf(fid,'- global minimum finite calls per bat × feature = **%d**\n',R.global_min_finite_calls);
fprintf(fid,'- V_hearing = **%.6f**\n',VHobs);
fprintf(fid,'- V_deaf = **%.6f**\n',VDobs);
fprintf(fid,'- D = V_hearing - V_deaf = **%+.6f**\n',Dobs);
fprintf(fid,'- exact conditioned assignments = **120**\n');
fprintf(fid,'- extreme |D| assignments = **%d**\n',extreme);
fprintf(fid,'- exact two-sided p = **%.6f**\n',p);
fprintf(fid,'- verdict = **%s**\n\n',verdict);
fprintf(fid,'## Descriptive sex-specific contrasts\n\n');
fprintf(fid,'- female D = %+.6f\n',Df);
fprintf(fid,'- male D = %+.6f\n',Dm);
fprintf(fid,'\n## Bat support and residual individuality\n\n');
fprintf(fid,'| Bat | sex | treatment | min finite calls/feature | squared residual norm |\n');
fprintf(fid,'|---|---|---|---:|---:|\n');
for ii=1:10
    fprintf(fid,'| %s | %s | %s | %d | %.6f |\n',ub(ii),batSex(ii),R.observed_treatment{ii},R.min_finite_calls_per_bat_feature(ii),sqnorm(ii));
end
fprintf(fid,'\nAll 28 source features were retained. Calls were not treated as biological replicates.\n');
fclose(fid);

delete(src);
end

function [D,VH,VD,res]=calcD(Z,sex,h)
res=zeros(size(Z));
for sx=["F","M"]
    for tr=[false true]
        idx=(sex==sx & h==tr);
        assert(sum(idx)>=2,'STOP_CELL_TOO_SMALL');
        m=mean(Z(idx,:),1);
        res(idx,:)=Z(idx,:)-m;
    end
end
ss=sum(res.^2,2);
VH=mean(ss(h));
VD=mean(ss(~h));
D=VH-VD;
end

function D=calcDsex(Z,sex,h,targetSex)
idxSex=(sex==targetSex);
R=zeros(size(Z));
for tr=[false true]
    idx=(idxSex & h==tr);
    m=mean(Z(idx,:),1);
    R(idx,:)=Z(idx,:)-m;
end
ss=sum(R(idxSex,:).^2,2);
hs=h(idxSex);
D=mean(ss(hs))-mean(ss(~hs));
end
