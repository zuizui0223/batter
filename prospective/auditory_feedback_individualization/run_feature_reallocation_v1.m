function run_feature_reallocation_v1()
% Post-primary descriptive exact additive decomposition across 28 features.
% No p-values.

here=fileparts(mfilename('fullpath'));
src=fullfile(here,'PAF_AllBatsData.mat');
primaryjson=fullfile(here,'PRIMARY_RESULT_V1.json');
outjson=fullfile(here,'FEATURE_REALLOCATION_RESULT_V1.json');
outmd=fullfile(here,'FEATURE_REALLOCATION_RESULT_V1.md');

assert(isfile(primaryjson),'STOP_PRIMARY_RESULT_ABSENT');
P0=jsondecode(fileread(primaryjson));
assert(strcmp(P0.verdict,'NO_DIFFERENCE_IN_AMOUNT'),'STOP_UNEXPECTED_PRIMARY_VERDICT');

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
        assert(sum(ok)>=100,'STOP_SUPPORT_DRIFT');
        M(ii,kk)=mean(x(ok));
    end
end

mu=mean(M,1);
sd=std(M,0,1);
assert(all(isfinite(sd) & sd>0),'STOP_BAD_SCALE');
Z=(M-mu)./sd;

R=zeros(size(Z));
for sx=["F","M"]
    for tr=[false true]
        idx=(batSex==sx & obsH==tr);
        assert(sum(idx)>=2,'STOP_CELL_TOO_SMALL');
        m=mean(Z(idx,:),1);
        R(idx,:)=Z(idx,:)-m;
    end
end

VH=mean(R(obsH,:).^2,1);
VD=mean(R(~obsH,:).^2,1);
Dk=VH-VD;
Dsum=sum(Dk);

tol=1e-10;
assert(abs(Dsum-P0.D_hearing_minus_deaf)<tol,'STOP_DECOMPOSITION_DOES_NOT_SUM_TO_PRIMARY');

positiveSum=sum(Dk(Dk>0));
negativeSum=sum(Dk(Dk<0));
absTotal=sum(abs(Dk));
if absTotal>0
    cancellation=1-abs(Dsum)/absTotal;
else
    cancellation=NaN;
end

[~,ord]=sort(abs(Dk),'descend');

rows=struct('feature',{},'V_hearing',{},'V_deaf',{},'D',{},'abs_D',{},'sign',{});
for kk=1:28
    rows(kk).feature=featNames{kk};
    rows(kk).V_hearing=VH(kk);
    rows(kk).V_deaf=VD(kk);
    rows(kk).D=Dk(kk);
    rows(kk).abs_D=abs(Dk(kk));
    if Dk(kk)>0
        rows(kk).sign='H>D';
    elseif Dk(kk)<0
        rows(kk).sign='H<D';
    else
        rows(kk).sign='equal';
    end
end

O=struct;
O.version=1;
O.source='10.17632/h5ff9vv5pc.1';
O.primary_D=P0.D_hearing_minus_deaf;
O.sum_feature_D=Dsum;
O.positive_sum=positiveSum;
O.negative_sum=negativeSum;
O.absolute_sum=absTotal;
O.cancellation_ratio=cancellation;
O.n_positive=sum(Dk>0);
O.n_negative=sum(Dk<0);
O.features=rows;
O.rank_by_abs_D=cellstr(string(featNames(ord)));

fid=fopen(outjson,'w');
fprintf(fid,'%s\n',jsonencode(O,'PrettyPrint',true));
fclose(fid);

fid=fopen(outmd,'w');
fprintf(fid,'# Auditory-feedback feature reallocation result v1\n\n');
fprintf(fid,'**DESCRIPTIVE ONLY — NO P-VALUES; PRIMARY VERDICT UNCHANGED.**\n\n');
fprintf(fid,'- primary D = **%+.6f**\n',O.primary_D);
fprintf(fid,'- sum of 28 feature contributions = **%+.6f**\n',Dsum);
fprintf(fid,'- positive feature contribution sum = **%+.6f**\n',positiveSum);
fprintf(fid,'- negative feature contribution sum = **%+.6f**\n',negativeSum);
fprintf(fid,'- total absolute contribution = **%.6f**\n',absTotal);
fprintf(fid,'- cancellation ratio = **%.6f**\n',cancellation);
fprintf(fid,'- positive / negative feature counts = **%d / %d**\n\n',O.n_positive,O.n_negative);

fprintf(fid,'## All 28 features, ranked by |D_k|\n\n');
fprintf(fid,'| rank | feature | V hearing | V deaf | D = H-D | sign |\n');
fprintf(fid,'|---:|---|---:|---:|---:|---|\n');
for rr=1:28
    kk=ord(rr);
    fprintf(fid,'| %d | %s | %.6f | %.6f | %+.6f | %s |\n', ...
        rr,featNames{kk},VH(kk),VD(kk),Dk(kk),rows(kk).sign);
end

fprintf(fid,'\nBy construction, these 28 D values sum exactly to the frozen primary D.\n');
fprintf(fid,'No feature-wise p-value or reduced-feature rescue is authorized.\n');
fclose(fid);

delete(src);
end
