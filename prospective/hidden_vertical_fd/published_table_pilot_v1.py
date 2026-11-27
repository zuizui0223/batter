"""Exploratory published-table audit, no site-level inference.
Peters et al. 2006 DOI:10.1111/j.1523-1739.2006.00526.x, table 2.
Silva et al. 2020 DOI:10.3390/d12020067, table 1 (CC BY).
Peters is a mean of above-median species scores, NOT animal counts.
Silva is a provisional transcription with a printed margin discrepancy.
Blank table cells coded zero; no silent corrections; NOT admitted for inference.
"""
import json
import numpy as np

# guild order: frugivore, nectarivore, aerial insectivore, gleaning insectivore,
# gleaning omnivore, carnivore, sanguivore.
# columns logged U,C, unlogged U,C
P=np.array([[7.4,6.,5.,4.2],[.8,.8,.4,0],[.6,1.5,1.6,.2],
[.8,.3,1.4,.2],[.4,.8,.8,.8],[.4,0,.8,0],[0,0,.2,.2]])
# Rows: original publisher species order, excluding family and subfamily headers.
# CF U,LM,UM,SC then fragment U,LM,UM,SC
S=np.array([
[139,2,0,0,75,3,1,0],
[25,4,1,0,32,1,1,0],[0,0,0,0,1,0,0,0],[330,22,14,6,709,51,46,9],[132,11,8,2,220,23,42,8],
[0,1,3,11,0,2,3,1],[12,4,9,4,13,2,12,1],[7,9,13,6,15,11,31,10],[12,8,7,1,10,5,10,5],[28,8,11,11,8,15,21,4],[39,1,4,4,33,5,5,1],[10,1,1,1,8,1,2,0],[0,0,0,3,0,0,0,0],[23,3,12,6,6,1,3,2],[0,0,2,1,0,0,1,0],[1,2,1,0,1,2,4,2],[0,0,1,1,4,0,3,0],[16,3,6,1,8,1,2,1],[1,0,1,0,3,0,0,0],[0,1,0,0,0,0,0,0],
[4,0,0,0,2,0,0,0],[4,0,0,0,0,0,0,0],[1,1,0,0,0,0,0,0],[0,0,0,0,1,0,0,0],[1,0,0,0,0,0,0,0],[1,0,1,0,2,0,0,0],[5,0,0,0,4,0,0,0],[49,0,0,0,17,1,1,0],[0,0,0,0,1,0,0,0],[2,0,0,0,2,0,0,0],[5,0,0,0,3,0,0,0],[0,0,0,2,0,0,0,0],[0,0,0,0,1,0,0,0],[22,1,0,0,26,0,0,0],[9,0,0,0,7,0,0,0],[3,6,7,1,3,38,42,0],[18,0,0,0,6,0,0,0],[1,0,0,0,1,1,2,0],[35,3,6,0,32,4,3,0],[70,1,0,0,29,0,0,0],[4,0,0,0,2,2,2,0],
[1,0,0,0,1,0,1,0],[1,0,1,0,6,0,0,0],[2,0,1,0,5,0,1,0],[24,0,0,0,16,1,0,0],[8,0,0,0,3,0,0,0]])
def H(p):
    p=p[p>0]
    return -(p*np.log(p)).sum()
def metrics(x):
    assert np.all(x >= 0) and np.all(x.sum(0)>0)
    p=x/x.sum(0)
    m=p.mean(1)
    q=lambda y:1-(y*y).sum()
    gamma=q(m)
    alpha=np.mean([q(y) for y in p.T])
    beta=gamma-alpha
    assert np.isclose(beta, np.mean(np.sum((p-m[:,None])**2,axis=0)))
    return dict(alpha=float(alpha),gamma=float(gamma),beta=float(beta),
        beta_share=float(beta/gamma),JSD=float(H(m)-np.mean([H(y) for y in p.T])),
        richness=int((x.sum(1)>0).sum()))
def main():
    # Validate full count, separate forest totals, species richness;
    # explicitly flag the conflicting printed stratum margins.
    printed=np.array([1046,92,110,61,1316,170,238,45])
    assert S.shape==(46,8) and S.sum()==3077
    assert S[:,:4].sum()==1308 and S[:,4:].sum()==1769
    assert ((S[:,:4].sum(1)>0).sum(),(S[:,4:].sum(1)>0).sum())==(42,40)
    assert not np.array_equal(S.sum(0),printed)
    common=(S[:,:4].sum(1)>0)&(S[:,4:].sum(1)>0)
    assert common.sum()==36
    result={"peters_guild_scores_descriptive":{"logged":metrics(P[:,:2]),"unlogged":metrics(P[:,2:])},
      "silva_nonadmitted":{"printed_margins":printed.tolist(),"transcribed_margins":S.sum(0).tolist(),
      "CF":metrics(S[:,:4]),"fragment":metrics(S[:,4:]),
      "common_CF":metrics(S[common,:4]),"common_fragment":metrics(S[common,4:])}}
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    main()
