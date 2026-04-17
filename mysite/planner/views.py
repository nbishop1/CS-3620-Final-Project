from datetime import date, datetime, timedelta
from urllib.parse import urlencode

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import LoginForm, NoteForm, ProfileUpdateForm, SignUpForm
from .models import Note, UserProfile


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


def _apply_sort_filter_context(context, request):
	sort_value = request.GET.get('sort', 'newest')
	context['sort_newest_selected'] = 'selected' if sort_value not in ('oldest', 'recent_edits') else ''
	context['sort_oldest_selected'] = 'selected' if sort_value == 'oldest' else ''
	context['sort_recent_edits_selected'] = 'selected' if sort_value == 'recent_edits' else ''


def _apply_selected_date_context(context, request):
	selected_date_raw = request.GET.get('date', '')
	selected_date_value = None

	if selected_date_raw:
		try:
			selected_date_value = datetime.strptime(selected_date_raw, '%Y-%m-%d').date()
		except ValueError:
			selected_date_value = None

	if selected_date_value is None:
		selected_date_value = date.today()

	context['selected_date'] = selected_date_value.isoformat()
	context['selected_date_display'] = selected_date_value.strftime('%A, %B %d, %Y')
	context['selected_date_prev'] = (selected_date_value - timedelta(days=1)).isoformat()
	context['selected_date_next'] = (selected_date_value + timedelta(days=1)).isoformat()


def _parse_optional_date(value):
	if not value:
		return None

	try:
		return datetime.strptime(value, '%Y-%m-%d').date()
	except ValueError:
		return None


def _build_note_list_query(user, request):
	notes = Note.objects.filter(user=user)
	keyword = request.GET.get('keyword', '').strip()
	start_date = _parse_optional_date(request.GET.get('start_date', '').strip())
	end_date = _parse_optional_date(request.GET.get('end_date', '').strip())
	sort_value = request.GET.get('sort', 'newest')

	if keyword:
		notes = notes.filter(Q(content__icontains=keyword))

	if start_date:
		notes = notes.filter(note_date__gte=start_date)

	if end_date:
		notes = notes.filter(note_date__lte=end_date)

	if sort_value == 'oldest':
		notes = notes.order_by('note_date', 'created_at')
	elif sort_value == 'recent_edits':
		notes = notes.order_by('-updated_at', '-created_at')
	else:
		notes = notes.order_by('-note_date', '-created_at')

	return notes


def _build_note_filter_query(request):
	query_data = {}
	for key in ('keyword', 'start_date', 'end_date', 'sort'):
		value = request.GET.get(key, '').strip()
		if value:
			query_data[key] = value

	return urlencode(query_data)


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
	context = _build_authenticated_context(request.user, 'Dashboard')
	note_day_first_ids = {}
	for note in (
		Note.objects.filter(user=request.user)
		.order_by('note_date', 'created_at', 'pk')
	):
		note_day_first_ids.setdefault(note.note_date.isoformat(), note.pk)

	recent_notes = list(
		Note.objects.filter(user=request.user)
		.order_by('-note_date', '-updated_at', '-created_at')[:3]
	)
	context['recent_notes'] = recent_notes
	context['note_dates'] = sorted(note_day_first_ids.keys())
	context['note_day_first_ids'] = note_day_first_ids
	return render(request, 'planner/dashboard.html', context)


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
	_apply_selected_date_context(context, request)
	_apply_sort_filter_context(context, request)
	return render(request, 'planner/task_create.html', context)


@login_required
def event_create_view(request):
	context = _build_authenticated_context(request.user, 'Add Event')
	_apply_selected_date_context(context, request)
	_apply_sort_filter_context(context, request)
	return render(request, 'planner/event_create.html', context)


@login_required
def note_create_view(request):
	context = _build_authenticated_context(request.user, 'Add Note')
	_apply_selected_date_context(context, request)
	_apply_sort_filter_context(context, request)
	selected_note = None
	selected_note_id = request.GET.get('note', '').strip()

	if selected_note_id:
		try:
			selected_note = Note.objects.get(pk=selected_note_id, user=request.user)
		except (Note.DoesNotExist, ValueError):
			raise Http404('Note not found.')

	if request.method == 'POST':
		posted_note_id = request.POST.get('note_id', '').strip()
		if posted_note_id:
			try:
				selected_note = Note.objects.get(pk=posted_note_id, user=request.user)
			except (Note.DoesNotExist, ValueError):
				raise Http404('Note not found.')

		note_form = NoteForm(request.POST, instance=selected_note)
		if note_form.is_valid():
			note = note_form.save(commit=False)
			note.user = request.user
			note.note_date = _parse_optional_date(request.POST.get('selected_date', '')) or date.today()
			note.save()
			redirect_query = {'date': note.note_date.isoformat(), 'note': str(note.pk)}
			return redirect(f"{request.path}?{urlencode(redirect_query)}")
	else:
		note_form = NoteForm(instance=selected_note)

	notes = _build_note_list_query(request.user, request)
	context['note_form'] = note_form
	context['notes'] = notes
	context['selected_note'] = selected_note
	context['selected_note_id'] = str(selected_note.pk) if selected_note else ''
	context['note_filter_query'] = _build_note_filter_query(request)
	return render(request, 'planner/note_create.html', context)


def logout_view(request):
	logout(request)
	return redirect('login')
