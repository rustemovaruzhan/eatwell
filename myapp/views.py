from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, UserUpdateForm, AvatarUpdateForm
from django.contrib.auth.decorators import login_required
from .models import NutritionProgram
from .models import UserProfile, WorkoutProgram, NotificationNew, ChatMessage, MessageForm, Message, Avatar, Blogs, RegistrationForm
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Max, OuterRef, Subquery, Prefetch, Exists
from django.utils.formats import date_format
from django.utils import timezone


apiKey = "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"


def welcome(request):
    return render(request, 'welcome.html')


def start(request):
    return render(request, 'start.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('form')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup_redirect(request):
    messages.error(request, "Something wrong here, it may be that you already have account!")
    return redirect("homepage")


@login_required
def home_view(request):
    workout_programs = WorkoutProgram.objects.all()
    programs = NutritionProgram.objects.all()
    user_name = request.user.username
    return render(request, 'home.html', {'programs': programs, 'workout_programs': workout_programs, 'user_name':user_name})


@login_required
def notification(request):
    notifications = NotificationNew.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        saved_workouts = user_profile.saved_workouts.all()
        saved_recipes = user_profile.saved_recipes.all()
    except UserProfile.DoesNotExist:
        saved_recipes = []
        saved_workouts = []

    user_name = request.user.username
    user = request.user
    avatar, created = Avatar.objects.get_or_create(user=user, defaults={'image': 'profile picture.png'})

    try:
        registration_form = RegistrationForm.objects.get(user=user)
    except RegistrationForm.DoesNotExist:
        registration_form = None

    return render(request, 'profile.html', {'saved_recipes': saved_recipes, 'saved_workouts' : saved_workouts, 'user_name': user_name, 'user': user, 'avatar': avatar, 'registration_form': registration_form })


@login_required
def messages(request):
    user_query = request.GET.get('q', '')
    current_user = request.user
    avatars = Avatar.objects.all()
    avatar_prefetch = Prefetch('avatar', queryset=avatars, to_attr='user_avatar')

    if user_query:
        users = User.objects.exclude(id=current_user.id).filter(username__icontains=user_query)
    else:
        users = User.objects.exclude(id=current_user.id).annotate(
            has_messages=Exists(
                Message.objects.filter(
                    Q(sender=OuterRef('pk'), receiver=current_user) |
                    Q(sender=current_user, receiver=OuterRef('pk'))
                )
            )
        ).filter(has_messages=True)

    users_with_last_message = users.prefetch_related(avatar_prefetch).annotate(
        last_message_time=Subquery(
            Message.objects.filter(
                Q(sender=OuterRef('pk'), receiver=current_user) |
                Q(sender=current_user, receiver=OuterRef('pk'))
            ).order_by('-timestamp').values('timestamp')[:1]
        ),
        last_message_text=Subquery(
            Message.objects.filter(
                Q(sender=OuterRef('pk'), receiver=current_user) |
                Q(sender=current_user, receiver=OuterRef('pk'))
            ).order_by('-timestamp').values('text')[:1]
        )
    ).order_by('-last_message_time')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        users_data = [{
            'id': user.id,
            'username': user.username,
            'avatar_url': user.user_avatar.image.url if hasattr(user, 'user_avatar') and user.user_avatar.image.url != '/media/profile%20picture.png' else static('assets/img/profile_picture.png'),
            'last_message_text': getattr(user, 'last_message_text', 'No messages yet'),
            'last_message_time': date_format(getattr(user, 'last_message_time', None), "DATETIME_FORMAT") if getattr(user, 'last_message_time', None) else 'No recent messages'
        } for user in users_with_last_message]
        return JsonResponse(users_data, safe=False)
    else:
        return render(request, 'messages.html', {'users': users_with_last_message})

@login_required
def message(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        message_text = data.get('message')
        if message_text:
            new_message = Message.objects.create(sender=request.user, receiver=other_user, text=message_text)
            return JsonResponse({
                'sender': new_message.sender.username,
                'text': new_message.text,
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    return render(request, 'message.html', {
        "messages": messages,
        "other_user": other_user,
        "form": MessageForm()
    })

@login_required
def add_recipe(request, program_id):
    program = get_object_or_404(NutritionProgram, id=program_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.saved_recipes.add(program)

    return JsonResponse({"message": "Recipe added successfully."})


@login_required
def add_workout(request, workout_id):
    workout_program = get_object_or_404(WorkoutProgram, id=workout_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.saved_workouts.add(workout_program)

    return JsonResponse({"message": "Workout added successfully."})


@login_required
def logout(request):
    return render(request, 'logout.html')


@login_required
def chat(request):
    return render(request, 'chatbot.html')


@csrf_exempt
def generate_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('user_message')
        current_user = request.user

        ChatMessage.objects.create(user=current_user, message=user_message, role='user')

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            proxies={
                'http': 'http://117.250.3.58:8080',  # Используйте актуальный IP и порт прокси-сервера для HTTP
                'https': 'http://117.250.3.58:8080'  # Используйте актуальный IP и порт прокси-сервера для HTTPS
            },
            headers={"Authorization": "Bearer " + str(apiKey)},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    },
                    {
                        "role": "system",
                        "content": "Ты помощник по питанию. Твоя задача консультировать по этому направлению."
                    }
                ]
            }
        )
        print(response)
        # Get the response from the OpenAI API
        response_json = response.json()
        print(response_json)
        content = response_json['choices'][0]['message']['content']
        assistant_response = content

        # Save the assistant's response to the database with the role 'assistant'
        ChatMessage.objects.create(user=current_user, message=assistant_response, role='assistant')

        return JsonResponse({'response': assistant_response})

    else:
        return JsonResponse({'error': 'Invalid request method'})


def chat_history(request):
    chat_messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    messages_json = [{
        'role': message.role,
        'message': message.message,
        'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for message in chat_messages]
    return JsonResponse({'chat_messages': messages_json})


# API Webhook
# view that receives a JSON payload with the event details
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# from orders.models import Order


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    return HttpResponse(payload)
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET)

    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # check if the event received is checkout.session.completed.
    # this event indicates that the checkout session has been successfully completed.
    if event.type == 'checkout.session.completed':

        # if we recieve this event, we retrieve the session object
        session = event.data.object

        # check if session mode is payment because this is the expected mode for one-off payments.
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            # mark order as paid,if the order exists.
            order.paid = True
            # save the order to the database.
            order.save()

    return HttpResponse(status=200)


@login_required
def blogs(request):
    articles = Blogs.objects.all()
    return render(request, 'blogs.html', {'articles': articles})

@login_required
def blog(request, article_id):
    article = get_object_or_404(Blogs, id=article_id)
    return render(request,'blog.html', {'article': article})

@login_required
def settings(request):
    try:
        avatar_instance = request.user.avatar
    except Avatar.DoesNotExist:
        avatar_instance = None

    u_form = UserUpdateForm(instance=request.user)
    p_form = AvatarUpdateForm(instance=avatar_instance)

    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST.get('action')
            if action == 'update_username':
                u_form = UserUpdateForm(request.POST, instance=request.user)
                if u_form.is_valid():
                    u_form.save()
                    return redirect('settings')
            elif action == 'update_avatar':
                p_form = AvatarUpdateForm(request.POST, request.FILES, instance=avatar_instance)
                if p_form.is_valid():
                    p_form.save()
                    return redirect('settings')

    user = request.user
    avatar, created = Avatar.objects.get_or_create(user=user, defaults={'image': 'profile picture.png'})
    context = {
        'user': user,
        'avatar': avatar,
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'settings.html', context)



@login_required
def form(request):
    if request.method == 'POST':
        user = request.user
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        daily_activity = request.POST.get('activity')

        RegistrationForm.objects.update_or_create(
            user=user,
            defaults={
                'gender': gender,
                'age': age,
                'height': height,
                'weight': weight,
                'daily_activity': daily_activity
            }
        )

        return redirect('home')

    return render(request, 'gender.html')

