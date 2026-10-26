import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score 
import joblib


data = {
    'math'   :[78,65,45,22,99,66,77,54,76,32],
    'science':[32,65,78,92,54,88,25,44,17,29],
    'english':[30,86,55,43,37,65,50,98,72,99],
    'Result':  ['fail','pass','pass','fail','pass','pass','fail','pass','fail','fail']
}
df=pd.DataFrame(data)
print(df)
df['Result'] = df['Result'].map({'fail':0, 'pass':1}) #ml algo give output as binary

#train the model
x=df[['math','science','english']]
y=df['Result']

x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2) #0.2 = percentage (teat,train)
# 70% i/p 30% i/p 
print(x_train)
print(x_test)

#call the model 
model =LogisticRegression() 
model.fit(x_train,y_train) #train the model

# from sklearn.metrics import accuracy_score 
'''res = model.predict(x_test)
print("Accuracy" , accuracy_score(y_test,res))

new_student =pd.DataFrame([[60,40,30]],columns=['math','science','english'])
predict = model.predict(new_student)
print(predict[0])'''

joblib.dump(model,'model.pkl') #dumping the model to model.pkl

    