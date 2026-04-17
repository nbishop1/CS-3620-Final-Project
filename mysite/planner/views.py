from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, ProfileUpdateForm, SignUpForm
from .models import UserProfile


def _get_or_create_profile(user):
	profile, _ = UserProfile.objects.get_or_create(user=user)
	return profile


def _get_theme_for_user(user):
	default_theme = UserProfile.THEME_SKY
	if not user.is_authenticated:
		return default_theme

	return _get_or_create_profile(user).theme or default_theme


def _get_user_display_name(user):
	full_name = user.get_full_name().strip()
	if full_name:
		return full_name
	if user.first_name:
		return user.first_name
	return user.email


def _get_user_avatar_initial(user):
	display_name = _get_user_display_name(user)
	return display_name[:1].upper() if display_name else ''


def _build_authenticated_context(user, title):
	profile = _get_or_create_profile(user)
	return {
		'title': title,
		'current_theme': profile.theme,
		'user_profile': profile,
		'display_name': _get_user_display_name(user),
		'avatar_initial': _get_user_avatar_initial(user),
	}


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
	return render(request, 'planner/dashboard.html', _build_authenticated_context(request.user, 'Dashboard'))


@login_required
def profile_view(request):
	profile = _get_or_create_profile(request.user)
	form = ProfileUpdateForm(request.user, request.POST or None, request.FILES or None)

	if request.method == 'POST' and form.is_valid():
		form.save()
		return redirect('profile')

	return render(
		request,
		'planner/profile.html',
		{
			'title': 'Profile',
			'form': form,
			'current_theme': profile.theme,
			'user_profile': profile,
			'display_name': _get_user_display_name(request.user),
			'avatar_initial': _get_user_avatar_initial(request.user),
		},
	)


@login_required
def task_create_view(request):
	context = _build_authenticated_context(request.user, 'Add Task')
	context['selected_date'] = request.GET.get('date', '')
	return render(request, 'planner/task_create.html', context)


@login_required
def event_create_view(request):
	context = _build_authenticated_context(request.user, 'Add Event')
	context['selected_date'] = request.GET.get('date', '')
	return render(request, 'planner/event_create.html', context)


@login_required
def note_create_view(request):
	context = _build_authenticated_context(request.user, 'Add Note')
	context['selected_date'] = request.GET.get('date', '')
	return render(request, 'planner/note_create.html', context)


def logout_view(request):
	logout(request)
	return redirect('login')
