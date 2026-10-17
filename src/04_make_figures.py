#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/"data/results"
OUT=ROOT/"outputs/figures"; OUT.mkdir(parents=True,exist_ok=True)

alg=pd.read_csv(RES/"Algorithm_Comparison.csv")
pv=alg.pivot(index="Model",columns="Validation",values="Balanced_accuracy")
fig,ax=plt.subplots(figsize=(7,4.5))
x=np.arange(len(pv)); w=.34
ax.bar(x-w/2,pv["Random 5-fold"],w,label="Random CV")
ax.bar(x+w/2,pv["Spatial block (5)"],w,label="Spatial-block CV")
ax.axhline(.5,ls="--",lw=.8)
ax.set_xticks(x,pv.index,rotation=20,ha="right")
ax.set_ylim(0,1); ax.set_ylabel("Balanced accuracy")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT/"validation_algorithm_comparison.png",dpi=300,bbox_inches="tight")
plt.close(fig)

sp=pd.read_csv(RES/"Species_Salinity_Effects.csv")
fig,ax=plt.subplots(figsize=(6.5,4.2))
y=np.arange(len(sp)); orv=sp["Odds_ratio_per_ppt"].to_numpy()
lo=sp["CI95_low_OR"].to_numpy(); hi=sp["CI95_high_OR"].to_numpy()
ax.errorbar(orv,y,xerr=[orv-lo,hi-orv],fmt="o",capsize=4)
ax.axvline(1,ls="--",lw=.8)
ax.set_yticks(y,sp["Species"]); ax.invert_yaxis()
ax.set_xlabel("Odds ratio per +1 ppt salinity")
fig.tight_layout()
fig.savefig(OUT/"species_salinity_odds_ratios.png",dpi=300,bbox_inches="tight")
plt.close(fig)
