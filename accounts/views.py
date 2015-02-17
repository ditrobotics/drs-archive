from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import login as django_login_view
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.generic import ListView

from .models import Profile
from .forms import EmailForm

# Create your views here.

def login_view(request):
    if request.user.is_authenticated():
        return redirect(request.user.profile)
    else:
        return django_login_view(request, template_name='accounts/login.html')


def registration_view(request):
    if request.user.is_authenticated():
        return redirect(request.user.profile)
    context = {}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        email_form = EmailForm(request.POST)
        if form.is_valid() and email_form.is_valid():
            user = form.save()
            login(request,
                authenticate(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                )
            )
            user.email = email_form.cleaned_data['email']
            user.save()
            Profile.objects.create(user=user)
            messages.success(request, '註冊成功！請點選 VERIFY 以驗證你的 Email')
            return redirect(request.user.profile)
    else:
        form = UserCreationForm()
        email_form = EmailForm()
    context['form'] = form
    context['email_form'] = email_form
    return render(request, 'accounts/registration.html', context)

def profile(request, username=None):
    context = {}
    if username is None:
        if request.user.is_authenticated():
            context['profileuser'] = request.user
        else:
            return redirect('login')
    else:
         context['profileuser'] = get_object_or_404(User, username=username)
    context['isself'] = (request.user == context['profileuser'])
    return render(request, 'accounts/profile.html', context)

@login_required
def get_email_token(request):
    context = {}
    if request.user.profile.email_verified:
        context['error'] = 'Your email is already verified.'
    else:
        if request.method == 'GET':
            if not request.user.profile.email_token_alive:
                context['error'] = 'The email verification link does not exist.'
            return render(request, 'accounts/email-sent.html', context)

        body_template = '''\
Dear {username},
Please visit the link below to verify your email address:
http://{link}

DIT Robotics Site'''

        if request.user.email:
            token = request.user.profile.get_email_token()
            try:
                success = send_mail(
                    'ditrobotics.tw email verification',
                    body_template.format(
                        username=request.user.username,
                        link=request.get_host() + reverse('verify_email', args=[token]),
                    ),
                    'noreply.ditrobotics@gmail.com',
                    [request.user.email],
                )
            except Exception:
                import traceback
                context['error'] = traceback.format_exc().splitlines()[-1]
            else:
                if success:
                    request.user.profile.email_token_refresh()
                    return redirect('get_email_token')
                else:
                    context['error'] = 'The server failed to send an email to {}'.format(request.user.email)
        else:
            context['error'] = 'You have not set your email yet!'
    return render(request, 'accounts/email-sent.html', context)

def verify_email(request, token):
    context = {}
    vuser = get_object_or_404(Profile, email_token=token).user
    context['vuser'] = vuser
    if vuser.profile.email_token_expire > timezone.now():
        vuser.profile.set_email_verified()
        return render(request, 'accounts/email-verified.html', context)
    else:
        return render(request, 'accounts/email-link-expired.html', context)

class UserList(ListView):
    context_object_name = 'all_users'
    queryset = User.objects.all()
    template_name = 'accounts/userlist.html'
