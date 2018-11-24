from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
#from django.core import serializers
import json
from json.decoder import JSONDecodeError
from .models import Account, Profile, Notification
#from .utilities import dijkstra
from queue import Queue
from django.utils import timezone

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

def totalGraph(request):
    if request.method == 'GET':
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


def levelGraph(request, level):
    if request.method == 'GET':
        closedSet = []
        openSet = Queue()
        edges = []
        loginProfile = Profile.objects.get(account = request.user)
        openSet.put({'node': loginProfile, 'level': 0})

        while not openSet.empty():
            currentNode = openSet.get()
            if currentNode['level'] < level:
                for nextNode in currentNode['node'].friends.all():
                    if nextNode not in map(lambda x: x['node'],closedSet):
                        openSet.put({'node': nextNode, 'level': currentNode['level']+1})
                        edges.append(currentNode['node'].friend_toJSON(nextNode))
            if currentNode['node'] not in map(lambda x: x['node'],closedSet):
                closedSet.append(currentNode)
        nodes = [nodeDictionary['node'].user_toJSON() for nodeDictionary in closedSet]
        return JsonResponse({'users': nodes, 'friends': edges})

    else:
        return HttpResponseNotAllowed(['GET'])


def totalFriendRequest(request):
    if request.method == 'GET':
        #return all notifications of user
        notifications = [noti for noti in request.user.noti_set.all().order_by('-datetime').values(
            'id','content','select','datetime','read')]
        return JsonResponse(notifications, safe=False)

    elif request.method == 'PUT':
        #set all notifications of user as read
        for notReadNotification in request.user.noti_set.filter(read = False):
            notReadNotification.read = True
            notReadNotification.save()
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(['GET', 'PUT'])


def specificFriendRequest(request, id):
    if request.method == 'PUT':
        #change the notifications when receiver seleted 'accept' or 'decline'
        try:
            body = request.body.decode()
            answer = json.loads(body)['answer']
        except(KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()

        receiverNoti = Notification.objects.get(id = id)
        sender = receiverNoti.sender
        receiver = receiverNoti.receiver
        senderNoti = sender.noti_set.get(receiver= receiver)
        now = timezone.now()

        senderNoti.datetime = now
        senderNoti.read = False
        receiverNoti.select = False
        receiverNoti.datetime = now
        receiverNoti.read = False
        
        if answer == 'accept':
            receiverNoti.content = 'You accepted a friend request from {}.'.format(
                sender.get_full_name())
            senderNoti.content = '{} accepted a friend request from you.'.format(
                receiver.get_full_name())
            profileOfSender = Profile.objects.get(account = sender)
            profileOfReceiver = Profile.objects.get(account = receiver)
            profileOfSender.friends.add(profileOfReceiver)
        else: #answer == 'decline'
            receiverNoti.content = 'You declined a friend request from {}.'.format(
                sender.get_full_name())
            senderNoti.content = '{} declined a friend request from you'.format(
                receiver.get_full_name())
        receiverNoti.save()
        senderNoti.save()
        return HttpResponse(status = 200)

    elif request.method == 'POST':
    #create a notification when user send a friend request
        sender = request.user
        receiver = Account.objects.get(id = id)
        now = timezone.now()
        newSenderNoti = Notification(
            content = 'You sent a friend request to {}.'.format(receiver.get_full_name()),
            select = False,
            datetime = now,
            sender = sender,
            receiver = receiver,
            profile = sender,
            )
        newReceiverNoti = Notification(
            content = '{} sent a friend request to you.'.format(sender.get_full_name()),
            select = True,
            datetime = now,
            sender = sender,
            receiver = receiver,
            profile = receiver,
            )
        newSenderNoti.save()
        newReceiverNoti.save()
        return JsonResponse({'createdTime': now}, status=201)
    else:
        return HttpResponseNotAllowed(['PUT', 'POST'])

@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])

