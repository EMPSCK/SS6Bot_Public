import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import HistGradientBoostingClassifier
from itertools import combinations

train = pd.read_csv('train.csv')
train = train.drop('smpl', axis=1)
corrmat = train.corr()

relevant_features = corrmat['target'].abs().sort_values(ascending=False)[1:].index.tolist()
relevant_features = relevant_features[0:30]

ans = []
for i in range(1, 31):
    print(f'Используем признаков {i}')
    final_features_list = list(combinations(relevant_features, i))
    max_score = 0
    features = []
    for f in final_features_list:
        final_features = list(f)
        X_train, X_test, y_train, y_test = train_test_split(
            train[final_features], train['target'], random_state=42, stratify=train['target'], test_size=0.3)

        gbdt_clf = HistGradientBoostingClassifier(min_samples_leaf=1,
                                                  max_depth=20,
                                                  max_iter=125,
                                                  random_state=42).fit(X_train, y_train)

        # Получим предсказание с вероятностями для валидационной части тренировочного датасета
        y_pred = gbdt_clf.predict_proba(X_test)

        # Переведем предсказание в формат Series
        y_pred = pd.Series(y_pred[:, 1])

        # Высчитаем метрику roc-auc по валидационным данным
        score = roc_auc_score(y_test, y_pred)
        if score > max_score:
            max_score = score
            features = final_features
    ans.append(f'{max_score}: {features}')

with open("output.txt", "a") as file:
    for line in ans:
        file.write(line + "\n\n")
