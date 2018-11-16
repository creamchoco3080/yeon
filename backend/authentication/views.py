from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
import json
from json.decoder import JSONDecodeError
from .models import Account, Profile

def index(request):
    return HttpResponse("index")

def signup(request):
    if request.method == 'POST':
        try:
            body = request.body.decode()
            new_username = json.loads(body)['username']
            new_password = json.loads(body)['password']
            new_firstname = json.loads(body)['firstName']
            new_lastname = json.loads(body)['lastName']
        except(KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        
        createdUser = Account.objects.create_user(email = new_username, password = new_password,
        	first_name = new_firstname, last_name = new_lastname)
        Profile.objects.create(account = createdUser)
        return HttpResponse(status = 201)
    else:
        return HttpResponseNotAllowed(['POST'])

def signin(request):
    if request.method == 'POST':
        try:
            body = request.body.decode()
            input_username = json.loads(body)['username']
            input_password = json.loads(body)['password']
        except(KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        
        user = authenticate(email=input_username, password=input_password)
        if user is not None:
            login(request, user)
            userJson = {
                'id': user.id,
                'email': user.email,
                'firstname': user.first_name,
                'lastname': user.last_name
            }
            return JsonResponse(userJson)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['POST'])

def signout(request):
    if request.method == 'GET':
        logout(request);
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])

def friend(request):
    if request.method == 'GET':
        #Retrieve all users from Profile and save them into response_user
        response_users = []
        response_friends = []

        for user in Profile.objects.all():
            response_users.append(user.user_toJSON())
            for friend in user.friends.all():
                if user.account.id < friend.account.id:
                    response_friends.append(user.friend_toJSON(friend))

        return JsonResponse({'users': response_users, 'friends': response_friends})
    else:
        return HttpResponseNotAllowed(['GET'])

from .utilities import dijkstra
def shortest_path(request, level):
    if request.method == 'GET':
        users = []
        friends = []

        for user in Profile.objects.all():
            users.append(user.user_toJSON())
            for friend in user.friends.all():
                if user.account.id < friend.account.id:
                    friends.append(user.friend_toJSON(friend))

        #Create edges
        edges = [(str(friend['user_1']), str(friend['user_2']), 1) for friend in friends]

        current_Profile = Profile.objects.get(account = request.user)
        current_id = current_Profile.account.id
        
        result = []
        all_users = Profile.objects.all()
        for user in all_users:
            user_id = user.account.id
            if(current_id == user_id):
                continue
            distance = dijkstra(edges, str(current_id), str(user_id))
            if distance[0] <= level: # get all results within specified distance
                result.append(current_Profile.friend_toJSON(user))
        result_filter = set([res['user_2'] for res in result]) # filter for users
        users = [user for user in users if user['id'] in result_filter] # filter users with result
        users.append(current_Profile.user_toJSON()) # append current user to users array
        # TODO: result is NOT friend relationship
        print({'users': users, 'friends': result})
        return JsonResponse({'users': users, 'friends': result})

    else:
        return HttpResponseNotAllowed(['GET'])

@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])
