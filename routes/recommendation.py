from fastapi import APIRouter,HTTPException
from models.user_preference import UserPreference
import pandas as pd
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt

recommendation = APIRouter()
recommendations = []
user_preferences = []

@recommendation.get('/recommendation')
def get_recommendations():
    return recommendations


@recommendation.get('/recommendation/{id_rec}')
def get_recommendation_by_id(id_rec:int):
    for recommendation in recommendations:
        if recommendation["id"] == id_rec:
            return recommendation

    raise HTTPException(status_code=404, detail="recommendation not found!")


@recommendation.post('/userpreference')
def post_user_preference(userPreference:UserPreference):
    print(userPreference)
    user_preferences.append(userPreference.dict())
    return user_preferences[-1]


@recommendation.get('/userpreference')
def get_user_preferences():
    return user_preferences


@recommendation.get('/recommendation/userpreference/{user_id}')
def create_recommendation_by_user_preferences(user_id:int):
    equipos = pd.read_csv('datasets/equipos_futbol.csv')
    calificaciones = pd.read_csv('datasets/matriz_calificaciones.csv')
    
    print(equipos)
    equipos['gamestyle'] = equipos.gamestyle.str.split('|') 
    
    equipos_co = equipos.copy()
    for index, row in equipos.iterrows():
        for gamestyle in row['gamestyle']:
            equipos_co.at[index, gamestyle] = 1

    equipos_co = equipos_co.fillna(0)

    calificaciones=calificaciones.drop("timestamp",1)
    
    print(user_id)
    print(user_preferences)
    one_user_preferences = []
    for oneuserPreference in user_preferences:
        if oneuserPreference["userId"] == user_id:
            one_user_preferences.append(oneuserPreference)
    
    print(one_user_preferences)

    entrada_preferences= pd.DataFrame(one_user_preferences)

    entrada_preferences=entrada_preferences.drop("userId",1)

    print(entrada_preferences)

    Id = equipos[equipos['name'].isin(entrada_preferences['name'].tolist())]
    entrada_preferences=pd.merge(Id,entrada_preferences)

    resultado = equipos_co['name'].isin(entrada_preferences['name'])

    resultadocambiado = []

    for index in range(len(resultado)):
            resultadocambiado.append(not resultado[index])

    newmatriz = equipos_co[resultadocambiado]

    print(newmatriz)

    team_user= equipos_co[equipos_co['teamId'].isin(entrada_preferences['teamId'].tolist())]

    team_user = team_user.reset_index(drop=True)
    gender_table = team_user.drop('teamId',1).drop('gamestyle',1).drop('name',1)

    user_profile = gender_table.transpose().dot(entrada_preferences['rating'])

    styles =  newmatriz.set_index(newmatriz['teamId'])
    styles= styles.drop('teamId',1).drop('gamestyle',1).drop('name',1)

    recom = ((styles*user_profile).sum(axis=1))/(user_profile.sum())
    recom = recom.sort_values(ascending = False)
    
    equiposfinal = equipos[equipos['teamId'].isin(recom.head(5).keys())]
    recomfinal = equiposfinal[['name']]
    print("Equipos recomendados segun sus intereses: \n",recomfinal)
    print(type(recomfinal))
    
    print(recomfinal['name'].tolist())
    
    cont = 0
    recommendations_obtain = []

    for _, row in equipos.iterrows():
        for onerecom in recomfinal['name'].tolist():
            if row['name'] == onerecom:
                cont+=1
                recommendations_obtain.append({'id':cont,'teamid': row['teamId'], 'name': onerecom})    

    print(recommendations_obtain)
    
    #Solo el contador de recomendaciones falta colocarlo como ordinal nada mas y ya estaria listo el backend
    
    contrecommendation = 1
    
    recommendations.append({'id':contrecommendation+1,'content':recommendations_obtain}) 

    if len(recommendations) > 0:
        raise HTTPException(status_code=200, detail="Creation of recommendation succeed!")
    else:
        raise HTTPException(status_code=404, detail="No recommendation created!")