from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from django.views import View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
# from .models import Profile
from .forms import UpdateUserForm, UpdateProfileForm
# import logging
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy






import warnings
import os


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise Exception("Please set the OPENAI_API_KEY environment variable")
client = OpenAI(api_key=OPENAI_API_KEY)

conversation = [{"role": "system", "content": "You are a helpful chatbot that answers user queries briefly with some humour in your response"}]

@login_required
@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        while True:
            # Get user input
            user_input = request.POST['user_input']
            conversation.append({"role": "user", "content": user_input})


            # Call the ChatGPT API to get a response
            completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages= conversation,
            temperature=0.5,
            max_tokens=80,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )

            # Extract the response text from the API result
            bot_response = completion.choices[0].message.content
            conversation.append({"role": "system", "content": bot_response})
            # Return the response as JSON
            return JsonResponse({'bot_response': bot_response})
    # If the request is not a POST, render the chatbot template
    return render(request, 'chatbot.html')

def home(request):
    return render(request, 'index.html')



class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='chatbot')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='chatbot')
        
        return super(CustomLoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
    # Authenticate the user
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            # User is authenticated, redirect to chatbot page
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            if self.request.user.is_authenticated:
                    return redirect('chatbot')
            else:
                # Handle the case where the user is not authenticated, e.g., redirect to the login page
                return redirect('login') 
        return super(CustomLoginView, self).form_valid(form)
    
LoginRequiredMixin
class CustomLogoutView(LogoutView):
    """
    Custom logout view.
    """

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # Specify the URL to redirect to after logout
        return reverse_lazy('home')  

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, 'You have been logged out.')
        return super().post(request, *args, **kwargs)

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if hasattr(request.user, 'profile'):
            profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        else:
            profile_form = UpdateProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        if hasattr(request.user, 'profile'):
            profile_form = UpdateProfileForm(instance=request.user.profile)
        else:
            profile_form = UpdateProfileForm()

    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form})


# logger = logging.getLogger(__name__)

@csrf_exempt
def transcribe(request):
    if request.method == 'POST':
        # Get the audio data from the request
        if 'audio_data' in request.FILES:
            audio_file = request.FILES['audio_data']
            # logger.info(f"Received audio data: {audio_file.name}, size: {audio_file.size} bytes, type: {audio_file.content_type}")
            # Save the audio data to a file
            path = default_storage.save('myaudio.webm', audio_file)
            myfile_path = os.path.join(settings.MEDIA_ROOT, path)
            with open(myfile_path, "rb") as myfile:
                # Send the audio data to the Whisper ASR API
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=myfile,
                    response_format="text"
                )
                # logger.info(f"Received transcript: {transcript}")
            
            # Delete the saved audio file
            os.remove(myfile_path)
            # Return the transcribed text
            return JsonResponse({'text': transcript})
        else:
            return JsonResponse({'error': 'No audio data found'})
    
    return "invalid request method"