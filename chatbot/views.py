from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
from django.contrib import auth
from django.contrib.auth.models import User, AnonymousUser
from .models import Chat
from django.utils import timezone

# openai_api_key = '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'
openai_api_key = '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'
openai.api_key = openai_api_key
def ask_openai(message):
    # response = openai.Completion.create(
    #     model = 'text-davinci-003',
    #     prompt = message,
    #     max_tokens = 150,
    #     n=1,
    #     stop=None,
    #     temperature=0.7
    # )
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages = [
            {"role": "system", "content": "You are an helpful assistant"},
            {"role": "user","content": message}
        ]
    )
    # print('***********',response)
    answer = response.choices[0].message.content.strip()
    return answer
    
def home(request):
    return render(request,'home.html')

# Create your views here.
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)
        if request.user.is_authenticated:
            chat = Chat(user= request.user, message=message,response=response, created_at=timezone.now())
            chat.save()
            return JsonResponse({'message': message, 'response':response})
            # pass
        else:
            guest_user = AnonymousUser()
            chat = Chat(user= guest_user, message=message,response=response, created_at=timezone.now())
            chat.save()
            return JsonResponse({'message': message, 'response':response})
    return render(request,'chatbot.html',{'chats':chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid Username or password'
            return render(request,'login.html',{'error_message':error_message})
    else:
        return render(request,'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']  
        email = request.POST['email']  
        password1 = request.POST['password1']  
        password2 = request.POST['password2']  
        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = "Error while creating account"
                return render(request,'register.html',{'error_message':error_message})
        else:
            error_message = "password doesn't match"
            return render(request,'register.html',{'error_message':error_message})
    return render(request,'register.html')

def logout(request):
    # return render(request,'logout.html')
    auth.logout(request)
    return redirect('home')
