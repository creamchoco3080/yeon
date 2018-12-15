from django.test import TestCase, Client
import json
from authentication.models import Account, Profile, Notification, Post, Group

class AuthenticationTestCase(TestCase):
	def test(self):
		client = Client(enforece_csrf_checks = True)
		response = client.post('api/signup/', json.dumps({'username': 'admin@yeon.com',
			'password': 'admin', 'firstName': 'yeon', 'lastName': 'admin'}),
		content_type = 'application/json')
		#self.assertEqual(response.status_code, 403)

		response = client.get('/api/token/')
		csrftoken = response.cookies['csrftoken'].value

		response = client.post('/api/signup/', json.dumps({'username': 'admin@yeon.com',
			'password': 'admin', 'firstName': 'yeon', 'lastName': 'admin'}),
			content_type = 'application/json', HTTP_X_CSRFTOKEN = csrftoken)
		self.assertEqual(response.status_code, 201)

		response = client.post('/api/signup/', json.dumps({'username': 'friend@yeon.com',
			'password': 'friend', 'firstName': 'yeon', 'lastName': 'admin'}),
			content_type = 'application/json', HTTP_X_CSRFTOKEN = csrftoken)
		self.assertEqual(response.status_code, 201)

		response = client.post('/api/signin/', json.dumps({'username': 'admin@yeon.com',
			'password': 'admin'}), content_type = 'application/json', HTTP_X_CSRFTOKEN = csrftoken)
		self.assertEqual(response.status_code, 200)

		response = client.get('/api/signout/')
		self.assertEqual(response.status_code, 204)

		response = client.post('/api/signin/', json.dumps({'username': 'admin@yeon.com',
			'password': 'admin'}), content_type = 'application/json', HTTP_X_CSRFTOKEN = csrftoken)
		self.assertEqual(response.status_code, 200)		
		response = client.get('/api/graph/')
		self.assertEqual(response.status_code, 200)
		response = client.get('/api/graph/2/')
		self.assertEqual(response.status_code, 200)


class FriendTestCase(TestCase):
	def setUp(self):
		self.account1 = Account.objects.create_user(email='jihyo@twice.com', first_name='Jihyo', last_name='Park', password='jihyo')
		self.account2 = Account.objects.create_user(email='nayeon@twice.com', first_name='Nayeon', last_name='Im', password='nayeon')
		self.account3 = Account.objects.create_user(email='sana@twice.com', first_name='Sana', last_name='Minatozaki', password='sana')
		self.profile1 = Profile.objects.create(account=self.account1)
		self.profile2 = Profile.objects.create(account=self.account2)
		self.profile3 = Profile.objects.create(account=self.account3)

	def test_send_friend_request(self):
		client = Client()

		response = client.post('/api/signin/', json.dumps({'username': 'jihyo@twice.com',
			'password': 'jihyo'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		response = client.post('/api/friend/2/')
		self.assertEqual(response.status_code, 201) #Sent a Friend Request Succeed
		now = response.json()['createdTime']

		response = client.get('/api/friend/')
		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(response.content, [{
				'id': 1,
				'content': 'You sent a friend request to Nayeon Im.',
				'select': False,
				'datetime': now,
				'read': False,
				'sender': 1,
				'receiver': 2
			}])


	def test_read_friend_request(self):
		client = Client()
		notification = Notification(
			content = 'You sent a friend request to Nayeon Im.',
			select = False,
			datetime = '2018-11-24T17:32:19.919Z',
			read = False,
			sender = self.account1,
			receiver = self.account2,
			profile = self.account1,
			)
		notification.save()

		response = client.post('/api/signin/', json.dumps({'username': 'jihyo@twice.com',
			'password': 'jihyo'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		response = client.put('/api/friend/')
		self.assertEqual(response.status_code, 200)
		response = client.get('/api/friend/')
		self.assertJSONEqual(response.content, [{
				'id': 1,
				'content': 'You sent a friend request to Nayeon Im.',
				'select': False,
				'datetime': '2018-11-24T17:32:19.919Z',
				'read': True,
				'sender': 1,
				'receiver': 2
			}])

	
	def test_receive_friend_request(self):
		client = Client()
		notiOfSender = Notification(
			content = 'You sent a friend request to Nayeon Im.',
			select = False,
			datetime = '2018-11-24T17:32:19.919Z',
			read = False,
			sender = self.account1,
			receiver = self.account2,
			profile = self.account1,
			)
		notiOfSender.save()
		notiOfReceiver = Notification(
			content = 'Jihyo Park sent a friend request to you.',
			select = True,
			datetime = '2018-11-24T17:32:19.919Z',
			read = False,
			sender = self.account1,
			receiver = self.account2,
			profile = self.account2,
			)
		notiOfReceiver.save()

		response = client.post('/api/signin/', json.dumps({'username': 'nayeon@twice.com',
			'password': 'nayeon'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		response = client.put('/api/friend/2/', json.dumps({'answer':'accept'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)

		notiOfSenderChanged = Notification.objects.get(id=1)
		notiOfReceiverChanged = Notification.objects.get(id=2)

		self.assertEqual(notiOfSenderChanged.content, 'Nayeon Im accepted a friend request from you.')
		self.assertFalse(notiOfSenderChanged.select)
		self.assertNotEqual(notiOfSenderChanged.datetime, '2018-11-24T17:32:19.919Z')
		self.assertFalse(notiOfSenderChanged.read)


		self.assertEqual(notiOfReceiverChanged.content, 'You accepted a friend request from Jihyo Park.')
		self.assertFalse(notiOfReceiverChanged.select)
		self.assertNotEqual(notiOfReceiverChanged.datetime, '2018-11-24T17:32:19.919Z')
		self.assertFalse(notiOfReceiverChanged.read)

		self.assertIn(self.profile1, self.profile2.friends.all())
		self.assertIn(self.profile2, self.profile1.friends.all())

	def test_notification(self):
		noti1 = Notification(
			content = 'Yes or Yes',
			select = False,
			datetime = '2018-11-24T17:32:19.919Z',
			read = False,
			sender = self.account1,
			receiver = self.account2,
			profile = self.account1
		)
		noti2 = Notification(
			content = 'Likey',
			select = False,
			datetime = '2018-11-24T17:32:19.919Z',
			read = False,
			sender = self.account1,
			receiver = self.account2,
			profile = self.account1
			)
		noti1.save()
		noti2.save()
		client = Client()
		response = client.post('/api/signin/', json.dumps({'username': 'sana@twice.com',
			'password': 'sana'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		response = client.get('/api/friend/')
		self.assertEqual(json.loads(response.content), []) #Get Empty Notification

		response = client.get('/api/signout/')
		self.assertEqual(response.status_code, 204)

		response = client.post('/api/signin/', json.dumps({'username': 'jihyo@twice.com',
			'password': 'jihyo'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		response = client.get('/api/friend/')
		notis = json.loads(response.content)
		self.assertEqual(notis[0]['content'], 'Yes or Yes')
		self.assertEqual(notis[1]['content'], 'Likey')
		self.assertEqual(len(notis),2)


class GraphTestCase(TestCase):
	pass

class SearchTestCase(TestCase):
	def setUp(self):
		self.account1 = Account.objects.create_user(email='jihyo@twice.com', first_name='Jihyo', last_name='Park', password='jihyo')
		self.account2 = Account.objects.create_user(email='nayeon@twice.com', first_name='Nayeon', last_name='Im', password='nayeon')
		self.account3 = Account.objects.create_user(email='sana@twice.com', first_name='Sana', last_name='Minatozaki', password='sana')
		self.account4 = Account.objects.create_user(email='sana@once.com', first_name='Sana', last_name='CuteSexy', password='sana')
		self.profile1 = Profile.objects.create(account=self.account1)
		self.profile2 = Profile.objects.create(account=self.account2)
		self.profile3 = Profile.objects.create(account=self.account3)
		self.profile4 = Profile.objects.create(account=self.account4)
	def test_search(self):
		client = Client()
		response = client.post('/api/signin/', json.dumps({'username': 'nayeon@twice.com',
			'password': 'nayeon'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		response = client.get('/api/search/jihyo/')
		self.assertJSONEqual(response.content, [{'id':1, 'first_name': 'Jihyo', 'last_name': 'Park'}]) #firstName Search Succeed

		response = client.get('/api/search/sana%20minatozaki/')
		self.assertJSONEqual(response.content, [{'id':3, 'first_name': 'Sana', 'last_name': 'Minatozaki'}]) #fullname Search Succeed

		response = client.get('/api/search/sana/')
		self.assertJSONEqual(response.content, [{'id':3, 'first_name': 'Sana', 'last_name': 'Minatozaki'},
		 {'id':4, 'first_name': 'Sana', 'last_name': 'CuteSexy'}]) #Several Results Search Succeed

class GetSelectedUsersTest(TestCase):
	def setUp(self):
		self.account1 = Account.objects.create_user(email='jihyo@twice.com', first_name='Jihyo', last_name='Park', password='jihyo')
		self.account2 = Account.objects.create_user(email='nayeon@twice.com', first_name='Nayeon', last_name='Im', password='nayeon')
		self.account3 = Account.objects.create_user(email='sana@twice.com', first_name='Sana', last_name='Minatozaki', password='sana')
		self.profile1 = Profile.objects.create(account=self.account1)
		self.profile2 = Profile.objects.create(account=self.account2)
		self.profile3 = Profile.objects.create(account=self.account3)
	def test_user(self):
		client = Client()
		response = client.post('/api/signin/', json.dumps({'username': 'nayeon@twice.com',
			'password': 'nayeon'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		response = client.post('/api/user/', json.dumps({'selectedNodes': 
			[{'id': 1, 'label': 'Jihyo'},
			{'id': 2, 'label': 'Nayeon'}]}), content_type = 'application/json')
		self.assertJSONEqual(response.content, [
			{'id': 1, 'first_name': 'Jihyo', 'last_name': 'Park'},
			{'id': 2, 'first_name': 'Nayeon', 'last_name': 'Im'}])

class PostingTest(TestCase):
	def setUp(self):
		self.account1 = Account.objects.create_user(email='jihyo@twice.com', first_name='Jihyo', last_name='Park', password='jihyo')
		self.account2 = Account.objects.create_user(email='nayeon@twice.com', first_name='Nayeon', last_name='Im', password='nayeon')
		self.account3 = Account.objects.create_user(email='sana@twice.com', first_name='Sana', last_name='Minatozaki', password='sana')
		self.profile1 = Profile.objects.create(account=self.account1)
		self.profile2 = Profile.objects.create(account=self.account2)
		self.profile3 = Profile.objects.create(account=self.account3)
	def test_post_write(self):
		client = Client()
		response = client.post('/api/signin/', json.dumps({'username': 'nayeon@twice.com',
			'password': 'nayeon'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		response = client.post('/api/post/write/', json.dumps({
			'selectedUsers': [
				{'id': 1, 'first_name': 'Jihyo', 'last_name': 'Park'},
				{'id': 2, 'first_name': 'Nayeon', 'last_name': 'Im'}
			],
			'content': 'The Best Thing I Ever Did'
			}), content_type = 'application/json')
		newPost = Post.objects.get(id=1)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(newPost.content, 'The Best Thing I Ever Did')
		self.assertEqual(list(newPost.tags.all()), [self.account1, self.account2])
	def test_post_get(self):
		client = Client()
		response = client.post('/api/signin/', json.dumps({'username': 'nayeon@twice.com',
			'password': 'nayeon'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		newPost = Post(content='Likey')
		newPost.save()
		newPost.tags.add(self.account1)
		newPost.tags.add(self.account2)
		response = client.post('/api/post/get/', json.dumps({
			'selectedUsers': [
				{'id': 1, 'first_name': 'Jihyo', 'last_name': 'Park'},
				{'id': 2, 'first_name': 'Nayeon', 'last_name': 'Im'}
			]}), content_type = 'application/json')
		self.assertJSONEqual(response.content, {'posts': [
				{'id':1, 'content': 'Likey', 'tags':[1,2]}
			]})

		response = client.post('/api/post/get/', json.dumps({
			'selectedUsers': [
				{'id': 1, 'first_name': 'Jihyo', 'last_name': 'Park'}
			]}), content_type = 'application/json')
		self.assertJSONEqual(response.content, {'posts': []})

		response = client.post('/api/post/get/', json.dumps({
			'selectedUsers': [
				{'id': 2, 'first_name': 'Nayeon', 'last_name': 'Im'}
			]}), content_type = 'application/json')
		self.assertJSONEqual(response.content, {'posts': []})

		response = client.post('/api/post/get/', json.dumps({
			'selectedUsers': [
				{'id': 1, 'first_name': 'Jihyo', 'last_name': 'Park'},
				{'id': 2, 'first_name': 'Nayeon', 'last_name': 'Im'},
				{'id': 3, 'first_name': 'Sana', 'last_name': 'Minatozaki'},
			]}), content_type = 'application/json')
		self.assertJSONEqual(response.content, {'posts': []})

class ProfileTest(TestCase):
	def setUp(self):
		self.account1 = Account.objects.create_user(email='jihyo@twice.com', first_name='Jihyo', last_name='Park', password='jihyo')
		self.account2 = Account.objects.create_user(email='nayeon@twice.com', first_name='Nayeon', last_name='Im', password='nayeon')
		self.account3 = Account.objects.create_user(email='sana@twice.com', first_name='Sana', last_name='Minatozaki', password='sana')
		self.profile1 = Profile.objects.create(account=self.account1)
		self.profile2 = Profile.objects.create(account=self.account2)
		self.profile3 = Profile.objects.create(account=self.account3)
		self.profile1.friends.add(self.profile2)
		self.profile1.friends.add(self.profile3)
		self.profile2.friends.add(self.profile3)
		self.group1 = Group.objects.create(name='Twice')
		self.group1.members.add(self.profile1, self.profile2, self.profile3)
	def test_get_one_profile(self):
		client = Client()
		response = client.post('/api/signin/', json.dumps({'username': 'nayeon@twice.com',
			'password': 'nayeon'}), content_type = 'application/json')
		self.assertEqual(response.status_code, 200) #SignIn Succeed

		response = client.get('/api/profile/one/1/')
		self.assertJSONEqual(response.content, {'full_name': 'Jihyo Park', 'motto': '', 'groups': ['Twice'],
            'distance': 1, 'mutual_friends': [{'id': 3, 'name': 'Sana Minatozaki'}]})