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


@recommendation.post('/userpreference')
def post_user_preference(userPreference:UserPreference):
    print(userPreference)
    user_preferences.append(userPreference.dict())
    return user_preferences[-1]


@recommendation.get('/userpreference')
def get_user_preferences():
    return user_preferences


@recommendation.get('/userpreference/{user_id}/team')
def get_teams_by_user(user_id:int):
    team_users = []
    for user in user_preferences:
        if user["userId"] == user_id:
            team_users.append(user)

    if len(team_users) > 0:
        return team_users
    else:        
        raise HTTPException(status_code=404, detail="User not found")


@recommendation.get('/recommendation/user/{user_id}')
def get_recommendation_by_user(user_id:int):
    recommendation_user = []
    for recom in recommendations:
        if recom["userId"] == user_id:
            recommendation_user.append(recom)

    if len(recommendation_user) > 0:
        return recommendation_user
    else:        
        raise HTTPException(status_code=404, detail="User not found")

@recommendation.delete('/userpreference/{user_id}/team/{team_name}')
def delete_user_preference_by_team_name(team_name:str,user_id:int):
    for index,preference in enumerate(user_preferences):
        if preference["name"] == team_name and preference['userId'] == user_id:
            user_preferences.pop(index)
            raise HTTPException(status_code=200, detail="User preference deleted successfully!")        
    raise HTTPException(status_code=404, detail="Post not found")


@recommendation.post('/recommendation/userpreference/{user_id}')
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
    
    
    recommendations.append({'userId':user_id ,'content':recommendations_obtain}) 

    if len(recommendations) > 0:
        return recommendations[-1]
    else:
        raise HTTPException(status_code=404, detail="No recommendation created!")