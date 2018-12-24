import pandas as pd
import sys
sys.path.append("..")
from sklearn.model_selection import train_test_split

#df read the csv or latest version of data
df=pd.read_csv('../raw_data/2018-12-22_00-43-41.csv',header=0,sep=',')
df["Res"] = df["Res"] / 1000000
#df = df[df["Xw"] >= 10]
print(df)
df['sCtnNum'] = df["CtnNum"].shift(1)
df['sUw_cpu'] = df["Uw_cpu"].shift(1)
df['sXw'] = df["Xw"].shift(1)
df['sRes'] = df["Res"].shift(1)
df = df.fillna(df.mean())
df['dCtnNum'] = df["sCtnNum"] - df["CtnNum"]
df['dUw_cpu'] = df["sUw_cpu"] - df["Uw_cpu"]
df['dXw'] = df["sXw"] - df["Xw"]
df['dRes'] = df["sRes"] - df["Res"]
x = df[["dUw_cpu", "dXw", "dRes"]]#"CtnNum", , "sUw_cpu", "sXw", "sRes"
y=df[["dCtnNum"]]
print(x, y)

X_train, X_test, y_train, y_test = train_test_split(x, y)

X_train.to_pickle("X_train.pkl")
X_test.to_pickle("X_test.pkl")
y_train.to_pickle("y_train.pkl")
y_test.to_pickle("y_test.pkl")
