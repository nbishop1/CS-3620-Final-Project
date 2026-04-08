from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, SignUpForm
from .models import UserProfile


def _get_theme_for_user(user):
	default_theme = UserProfile.THEME_SKY
	if not user.is_authenticated:
		return default_theme

	try:
		return user.profile.theme
	except UserProfile.DoesNotExist:
		return default_theme


def login_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	form = LoginForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		email = form.cleaned_data['email']
		password = form.cleaned_data['password']
		user = authenticate(request, username=email, password=password)
		if user is not None:
			login(request, user)
			return redirect('dashboard')
		form.add_error(None, 'Invalid email or password.')

	return render(
		request,
		'planner/login.html',
		{'form': form, 'title': 'Login', 'current_theme': _get_theme_for_user(request.user)},
	)


def signup_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	form = SignUpForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		user = form.save()
		login(request, user)
		return redirect('dashboard')

	return render(
		request,
		'planner/signup.html',
		{'form': form, 'title': 'Create Account', 'current_theme': _get_theme_for_user(request.user)},
	)


@login_required
def dashboard_view(request):
	return render(
		request,
		'planner/dashboard.html',
		{'title': 'Dashboard', 'current_theme': _get_theme_for_user(request.user)},
	)


def logout_view(request):
	logout(request)
	return redirect('login')
