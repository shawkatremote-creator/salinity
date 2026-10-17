#!/usr/bin/env python3
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/"data/processed/Sundarbans_Multisensor_Feature_Cube_public.csv")
d=df[df["Year"].isin([2010,2020,2024])].copy()
OUT=ROOT/"outputs"; OUT.mkdir(exist_ok=True)

rows=[]
for sp in ["Sundri","Gewa","Goran","Passur"]:
    response=f"{sp}_Prop"
    dat=d[[response,"Salinity_PPT","Year","PSP"]].dropna().copy()
    fit=smf.glm(f"{response} ~ Salinity_PPT + C(Year)",data=dat,
                family=sm.families.Binomial()).fit(
                    cov_type="cluster",cov_kwds={"groups":dat["PSP"]})
    beta=float(fit.params["Salinity_PPT"])
    se=float(fit.bse["Salinity_PPT"])
    rows.append({
        "Species":sp,"Salinity_logit_beta":beta,"Robust_SE":se,
        "p":float(fit.pvalues["Salinity_PPT"]),
        "Odds_ratio_per_ppt":float(np.exp(beta)),
        "CI95_low_OR":float(np.exp(beta-1.96*se)),
        "CI95_high_OR":float(np.exp(beta+1.96*se)),
        "AIC":float(fit.aic)
    })
out=pd.DataFrame(rows)
out.to_csv(OUT/"species_salinity_glm.csv",index=False)
print(out)
