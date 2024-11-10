import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, NuSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
import os

classifiers = {
    "knn": KNeighborsClassifier(3),
    "svm": SVC(kernel="rbf", C=0.025, probability=True),
    "nusvm": NuSVC(probability=True),
    "decisiontree": DecisionTreeClassifier(),
    "rf": RandomForestClassifier(),
    "adaboost": AdaBoostClassifier(),
    "gradientboost": GradientBoostingClassifier(),
    "naivebayes": GaussianNB(),
    "lda": LinearDiscriminantAnalysis(),
    "qda": QuadraticDiscriminantAnalysis(),
}


def prep_data():
    raw_data = pd.read_csv("CFB_GAME_DATA_2013_2023.csv")

    n_rows = len(raw_data)

    raw_data["ID"] = np.repeat(range(1, n_rows // 2 + 1), 2)

    df_home = raw_data[raw_data["home"] == 1]
    df_away = raw_data[raw_data["home"] == 0]

    lister = []
    for _, row in df_home.iterrows():
        if (row["winner"] == 1) & (row["home"] == 1):
            lister.append(1)
        else:
            lister.append(0)

    df_home["DID_HOME_WIN"] = lister

    df_away.columns = [f"{col}_away" for col in df_away.columns]
    df_away["ID"] = df_away["ID_away"]

    df_merged = pd.merge(df_away, df_home, on="ID")

    df_merged.drop(
        columns=[
            "winner_away",
            "home_away",
            "ID_away",
            "winner",
            "points_away",
            "school_away",
            "ID",
            "home",
            "points",
            "school",
        ],
        inplace=True,
    )
    df_merged.to_csv("processed_training_data.csv", index=False)


def main() -> None:
    if "processed_training_data.csv" not in os.listdir():
        prep_data()
    df = pd.read_csv("processed_training_data.csv")
    X = df.drop(columns="DID_HOME_WIN")
    y = df["DID_HOME_WIN"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1337)
    for name, clf in classifiers.items():
        print(f"Training {name} model.")
        lr = clf
        lr.fit(X_train, y_train)
        y_pred = lr.predict(X_test)
        accuracy = accuracy_score(y_pred, y_test)
        precision = precision_score(y_pred, y_test)
        f1 = f1_score(y_pred, y_test)
        recall = recall_score(y_pred, y_test)
        print(f"Test Accuracy: {accuracy}")
        print(f"Test Precision: {precision}")
        print(f"Test F1: {f1}")
        print(f"Test Recall: {recall}")
        with open(f"{name}_model.pkl", "wb") as f:
            pickle.dump(lr, f)
        print(f"Saved {name} model!")


if __name__ == "__main__":
    main()
