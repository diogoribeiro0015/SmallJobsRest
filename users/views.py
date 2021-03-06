from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse, JsonResponse
from rest_framework.authtoken.models import Token
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Skill
from .serializers import SkillSerializer
from jobs.views import get_user
from jobs.serializers import JobSerializer

# Helper methods

def user_exists(email):
    try:
        User.objects.get(email = email)
        return True
    except Exception as e:
        return False

# Views

def signup(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if user_exists(body['email']):
            return JsonResponse({'error': 'This email has already been used'})
        user = User.objects.create_user(body['username'], body['email'], body["password"])
        user.save()
        user.first_name = body['first_name']
        user.last_name = body['last_name']
        user.userprofile.age = body['age']
        user.userprofile.phone_number = body['phone_number']
        user.userprofile.description = body['description']
        for skill_body in body['skills']:
            user.userprofile.skills.add(Skill.objects.get_or_create(name=skill_body.lower())[0])
        user.userprofile.save()
        user.save()
        return JsonResponse({'error': ''})
    else:
        return JsonResponse({"error":"Must be a POST request"})


def login(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        email = body['email']
        password = body['password']
        if not user_exists(email):
            return JsonResponse({"error":"login failed"})
        user = User.objects.get(email = email)
        authenticated = authenticate(username=user.username, password=password)
        if authenticated is not None:
            queryset = user.userprofile.skills
            serializer = SkillSerializer(queryset, many=True)
            token = Token.objects.get_or_create(user=user)
            return JsonResponse({"token": token[0].key,
            "first_name": user.first_name, 
            "last_name": user.last_name,
            "email": user.email, 
            "age": user.userprofile.age, 
            "phone_number":user.userprofile.phone_number, 
            "description": user.userprofile.description, 
            "skills": serializer.data})
        else:
            return JsonResponse({"error":"login failed"})
    else:
        return HttpResponse('POST ONLY')


def previous_jobs(request):
    user = get_user(request)
    if user == False:
        return JsonResponse({'error': 'User not found'})

    jobs = user.employee.all()
    serializer = JobSerializer(jobs, many=True)
    return JsonResponse(serializer.data, safe=False)

def my_created_jobs(request):
    user = get_user(request)
    if user == False:
        return JsonResponse({'error': 'User not found'})

    jobs = user.employer.all()
    serializer = JobSerializer(jobs, many=True)
    return JsonResponse(serializer.data, safe=False)