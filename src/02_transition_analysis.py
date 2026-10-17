#!/usr/bin/env python3
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from scipy.spatial.distance import braycurtis
from scipy.stats import binomtest

ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/"data/processed/Sundarbans_Multisensor_Feature_Cube_public.csv")
d=df[df["Use_for_species_model"].astype(bool)].copy().reset_index(drop=True)
OUT=ROOT/"outputs"; OUT.mkdir(exist_ok=True)

species=["Sundri","Gewa","Goran","Passur","Kankra","Keora","Baen","Singra","Khalshi","Amur"]
P=d[[f"{s}_Prop" for s in species]].fillna(0).to_numpy(float)
P=P/np.where(P.sum(axis=1,keepdims=True)==0,1,P.sum(axis=1,keepdims=True))
labels=KMeans(n_clusters=4,n_init=100,random_state=42).fit_predict(np.sqrt(P))
means=pd.DataFrame(P,columns=species).assign(cluster=labels).groupby("cluster").mean()
names={}
for c,row in means.iterrows():
    top=row.idxmax()
    names[c]={"Sundri":"Sundri-dominant","Gewa":"Gewa-dominant",
              "Goran":"Goran-dominant","Kankra":"Kankra-mixed"}.get(top,f"{top}-dominant")
d["Fine_Assemblage"]=[names[c] for c in labels]

sal=d.groupby("Fine_Assemblage")["Salinity_PPT"].agg(["mean","std","count"]).reset_index()
sal.to_csv(OUT/"fine_assemblage_salinity.csv",index=False)

rows=[]
for psp,g in d.groupby("PSP"):
    if (g.Year==2010).any() and (g.Year==2024).any():
        a=int(g.index[g.Year==2010][0]); b=int(g.index[g.Year==2024][0])
        rows.append({
            "PSP":psp,
            "Fine_Assemblage_2010":d.loc[a,"Fine_Assemblage"],
            "Fine_Assemblage_2024":d.loc[b,"Fine_Assemblage"],
            "Changed":int(d.loc[a,"Fine_Assemblage"]!=d.loc[b,"Fine_Assemblage"]),
            "BrayCurtis_2010_2024":braycurtis(P[a],P[b]),
            "Delta_Salinity":d.loc[b,"Salinity_PPT"]-d.loc[a,"Salinity_PPT"]
        })
t=pd.DataFrame(rows)
t.to_csv(OUT/"fine_transitions_2010_2024.csv",index=False)

sg=((t.Fine_Assemblage_2010=="Sundri-dominant")&(t.Fine_Assemblage_2024=="Gewa-dominant")).sum()
gs=((t.Fine_Assemblage_2010=="Gewa-dominant")&(t.Fine_Assemblage_2024=="Sundri-dominant")).sum()
n=sg+gs
p=binomtest(sg,n,0.5).pvalue if n else np.nan
print(f"Matched plots: {len(t)}; changed: {t.Changed.mean():.1%}")
print(f"Sundri→Gewa={sg}; Gewa→Sundri={gs}; exact directional p={p:.3f}")
