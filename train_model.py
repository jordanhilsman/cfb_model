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


class DataPreparer:
    def __init__(self, raw_data_path: str, processed_data_path: str):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path

    def prep_data(self) -> None:
        raw_data = pd.read_csv(self.raw_data_path)
        n_rows = len(raw_data)
        raw_data['ID'] = np.repeat(range(1, n_rows // 2 + 1), 2)

        df_home = raw_data[raw_data["home"] == 1]
        df_away = raw_data[raw_data["home"] == 0]

        df_home['DID_HOME_WIN'] = [1 if (row['winner'] == 1 and row['home'] == 1) else 0 for _, row in df_home.iterrows()]

        df_away.columns = [f"{col}_away" for col in df_away.columns]
        df_away["ID"] = df_away["ID_away"]

        df_merged = pd.merge(df_away, df_home, on="ID").drop(
                columns = ["winner_away", "home_away", "ID_away", "winner", "points_away",
                           "school_away", "ID", "home", "points", "school"])

        df_merged.to_csv(self.processed_data_path, index=False)

    def get_data(self) -> pd.DataFrame:
        if not os.path.exists(self.processed_data_path):
            self.prep_data
        return pd.read_csv(self.processed_data_path)

class ModelTrainer:
    def __init__(self, classifiers:dict, output_dir:str):
        self.classifiers = classifiers
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def train_and_evaluate(self, X_train, X_test, y_train, y_test) -> None:
        for name, model in self.classifiers.items():
            print(f"Training {name} model")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            metrics = {
                    "accuracy" : accuracy_score(y_test, y_pred),
                    "precision" : precision_score(y_test, y_pred),
                    "f1" : f1_score(y_test, y_pred),
                    "recall" : recall_score(y_test, y_pred),
                }
            for metric_name, value in metrics.items():
                print(f"{metric_name.capitalize()}: {value:.4f}")

            model_path = os.path.join(self.output_dir, f"{name}_model.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(model, f)
            print(f"Saved {name} model at {model_path}.")





def main() -> None:
    data_preparer = DataPreparer("./unprocessed_data/CFB_GAME_DATA_2013_2023.csv",
                                 "processed_training_data.csv")
    data = data_preparer.get_data()
    X = data.drop(columns="DID_HOME_WIN")
    y = data["DID_HOME_WIN"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1337)
    classifiers = {
        "knn": KNeighborsClassifier(2),
        "svm": SVC(kernel="rbf", C=0.025, probability=True),
        "nusvm": NuSVC(probability=True),
        "decisiontree": DecisionTreeClassifier(max_depth=20, min_samples_split=10, min_samples_leaf=4),
        "rf": RandomForestClassifier(),
        "adaboost": AdaBoostClassifier(),
        "gradientboost": GradientBoostingClassifier(),
        "naivebayes": GaussianNB(),
        "lda": LinearDiscriminantAnalysis(solver='lsqr'),
        "qda": QuadraticDiscriminantAnalysis(),
        }
    trainer = ModelTrainer(classifiers, output_dir="./models")
    trainer.train_and_evaluate(X_train, X_test, y_train, y_test)

if __name__ == "__main__":
    main()
