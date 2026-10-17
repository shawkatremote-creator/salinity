#!/usr/bin/env python3
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, LeaveOneGroupOut
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, roc_auc_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/processed"
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)

df=pd.read_csv(DATA/"Sundarbans_Multisensor_Feature_Cube_public.csv")
d=df[df["Use_for_species_model"].astype(bool)].copy().reset_index(drop=True)
blocks=pd.read_csv(DATA/"PSP_Spatial_Block_Assignments_public.csv")

species=["Sundri","Gewa","Goran","Passur","Kankra","Keora","Baen","Singra","Khalshi","Amur"]
P=d[[f"{s}_Prop" for s in species]].fillna(0).to_numpy(float)
P=P/np.where(P.sum(axis=1,keepdims=True)==0,1,P.sum(axis=1,keepdims=True))
labels=KMeans(n_clusters=2,n_init=100,random_state=42).fit_predict(np.sqrt(P))
means=pd.DataFrame(P,columns=species).assign(cluster=labels).groupby("cluster").mean()
gewa_cluster=int(means["Gewa"].idxmax())
y=(labels==gewa_cluster).astype(int)

meta={'Year','PSP','Salinity_Zone','Salinity_PPT','Tree_Count_Total',
      'Tree_Species_Richness','Shannon_H','Simpson_1-D','Use_for_species_model',
      'Species_Model_Status','Spatial_Block'}
resp={c for c in d.columns if c.endswith("_Tree_Count") or c.endswith("_Prop")}
full=[c for c in d.columns if c not in meta and c not in resp
      and d[c].notna().mean()>=0.50 and d[c].nunique(dropna=True)>1]
harm=[c for c in full if all(g[c].notna().mean()>=0.80 for _,g in d.groupby("Year"))]

models={
"Extra Trees":ExtraTreesClassifier(n_estimators=300,max_features=.7,min_samples_leaf=2,class_weight="balanced",random_state=42,n_jobs=-1),
"Random Forest":RandomForestClassifier(n_estimators=300,max_features=.7,min_samples_leaf=2,class_weight="balanced_subsample",random_state=42,n_jobs=-1),
"XGBoost":XGBClassifier(n_estimators=220,max_depth=4,learning_rate=.035,subsample=.8,colsample_bytree=.8,eval_metric="logloss",random_state=42,n_jobs=-1),
"LightGBM":LGBMClassifier(n_estimators=220,num_leaves=15,learning_rate=.035,subsample=.8,colsample_bytree=.8,random_state=42,verbosity=-1)
}

def score_model(feats, model, splits):
    X=d[feats].replace([np.inf,-np.inf],np.nan)
    pred=np.zeros(len(y),dtype=int); prob=np.zeros(len(y))
    for tr,te in splits:
        pipe=make_pipeline(SimpleImputer(strategy="median"),model)
        pipe.fit(X.iloc[tr],y[tr])
        pred[te]=pipe.predict(X.iloc[te])
        prob[te]=pipe.predict_proba(X.iloc[te])[:,1]
    return dict(
        Accuracy=accuracy_score(y,pred),
        Balanced_accuracy=balanced_accuracy_score(y,pred),
        F1=f1_score(y,pred),
        ROC_AUC=roc_auc_score(y,prob)
    )

rows=[]
for name,model in models.items():
    r=score_model(full,model,StratifiedKFold(5,shuffle=True,random_state=42).split(d,y))
    rows.append({"Model":name,"Validation":"Random 5-fold",**r})
    groups=d["PSP"].map(dict(zip(blocks.PSP,blocks.block_5))).to_numpy()
    r=score_model(full,model,LeaveOneGroupOut().split(d,y,groups))
    rows.append({"Model":name,"Validation":"Spatial block (5)",**r})
pd.DataFrame(rows).to_csv(OUT/"algorithm_comparison.csv",index=False)

sens=[]
for nb in [3,5,10]:
    groups=d["PSP"].map(dict(zip(blocks.PSP,blocks[f"block_{nb}"]))).to_numpy()
    for setname,feats in [("Full multisensor",full),("Harmonized common",harm)]:
        model=ExtraTreesClassifier(n_estimators=300,max_features=.7,min_samples_leaf=2,class_weight="balanced",random_state=42,n_jobs=-1)
        r=score_model(feats,model,LeaveOneGroupOut().split(d,y,groups))
        sens.append({"Blocks":nb,"Feature_set":setname,"Predictors":len(feats),**r})
pd.DataFrame(sens).to_csv(OUT/"spatial_block_sensitivity.csv",index=False)

loyo=[]
X=d[harm].replace([np.inf,-np.inf],np.nan)
for yr in sorted(d.Year.unique()):
    te=np.where(d.Year.to_numpy()==yr)[0]; tr=np.where(d.Year.to_numpy()!=yr)[0]
    pipe=make_pipeline(SimpleImputer(strategy="median"),
        ExtraTreesClassifier(n_estimators=300,max_features=.7,min_samples_leaf=2,class_weight="balanced",random_state=42,n_jobs=-1))
    pipe.fit(X.iloc[tr],y[tr])
    pred=pipe.predict(X.iloc[te]); prob=pipe.predict_proba(X.iloc[te])[:,1]
    yy=y[te]
    loyo.append({"Held_out_year":int(yr),"n":len(te),"Gewa_dominant_n":int(yy.sum()),
                 "Accuracy":accuracy_score(yy,pred),
                 "Balanced_accuracy":balanced_accuracy_score(yy,pred),
                 "ROC_AUC":roc_auc_score(yy,prob) if len(np.unique(yy))==2 else np.nan})
pd.DataFrame(loyo).to_csv(OUT/"leave_one_year_out_harmonized.csv",index=False)

print("Full predictors:",len(full),"Harmonized predictors:",len(harm))
print(pd.DataFrame(rows))
