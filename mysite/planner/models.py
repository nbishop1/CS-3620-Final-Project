from calendar import monthrange
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	THEME_SKY = 'sky'
	THEME_FOREST = 'forest'
	THEME_SUNSET = 'sunset'
	THEME_SLATE = 'slate'

	THEME_CHOICES = [
		(THEME_SKY, 'Sky Blue'),
		(THEME_FOREST, 'Forest Green'),
		(THEME_SUNSET, 'Sunset Orange'),
		(THEME_SLATE, 'Slate Gray'),
	]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	theme = models.CharField(max_length=20, choices=THEME_CHOICES, default=THEME_SKY)
	profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

	def __str__(self):
		return f"{self.user.email} ({self.theme})"


class Note(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
	note_date = models.DateField()
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-note_date', '-updated_at', '-created_at']

	def __str__(self):
		return f"{self.user.email} note on {self.note_date.isoformat()}"


class Event(models.Model):
	COLOR_RED = 'red'
	COLOR_BLUE = 'blue'
	COLOR_GREEN = 'green'
	COLOR_BLACK = 'black'

	COLOR_CHOICES = [
		(COLOR_RED, 'Red'),
		(COLOR_BLUE, 'Blue'),
		(COLOR_GREEN, 'Green'),
		(COLOR_BLACK, 'Black'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
	name = models.CharField(max_length=120)
	color = models.CharField(max_length=10, choices=COLOR_CHOICES, default=COLOR_BLUE)
	is_all_day = models.BooleanField(default=True)
	start_date = models.DateField()
	end_date = models.DateField()
	start_time = models.TimeField(blank=True, null=True)
	end_time = models.TimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-start_date', '-updated_at', '-created_at']

	def __str__(self):
		return f"{self.user.email} event '{self.name}' ({self.start_date.isoformat()} - {self.end_date.isoformat()})"


class Task(models.Model):
	REPEAT_ONE_TIME = 'one_time'
	REPEAT_DAILY = 'daily'
	REPEAT_EVERY_N_DAYS = 'every_n_days'
	REPEAT_EVERY_N_MONTHS = 'every_n_months'

	REPEAT_CHOICES = [
		(REPEAT_ONE_TIME, 'One time'),
		(REPEAT_DAILY, 'Daily'),
		(REPEAT_EVERY_N_DAYS, 'Every N days'),
		(REPEAT_EVERY_N_MONTHS, 'Every N months'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
	title = models.CharField(max_length=160)
	start_date = models.DateField()
	due_date = models.DateField()
	repeat_type = models.CharField(max_length=20, choices=REPEAT_CHOICES, default=REPEAT_ONE_TIME)
	repeat_interval = models.PositiveIntegerField(default=1)
	recurrence_count = models.PositiveIntegerField(default=0)
	is_completed = models.BooleanField(default=False)
	completed_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['due_date', 'created_at', 'pk']

	def __str__(self):
		return f"{self.user.email} task '{self.title}' due {self.due_date.isoformat()}"

	@property
	def is_recurring(self):
		return self.repeat_type != self.REPEAT_ONE_TIME

	def get_repeat_summary(self):
		if self.repeat_type == self.REPEAT_DAILY:
			return 'Daily'
		if self.repeat_type == self.REPEAT_EVERY_N_DAYS:
			suffix = 'day' if self.repeat_interval == 1 else 'days'
			return f"Every {self.repeat_interval} {suffix}"
		if self.repeat_type == self.REPEAT_EVERY_N_MONTHS:
			suffix = 'month' if self.repeat_interval == 1 else 'months'
			return f"Every {self.repeat_interval} {suffix}"
		return 'One time'

	def _get_monthly_occurrence(self, occurrence_index):
		total_months = (self.start_date.month - 1) + (occurrence_index * self.repeat_interval)
		target_year = self.start_date.year + (total_months // 12)
		target_month = (total_months % 12) + 1
		target_day = min(self.start_date.day, monthrange(target_year, target_month)[1])
		return self.start_date.replace(year=target_year, month=target_month, day=target_day)

	def get_occurrence_date(self, occurrence_index):
		if self.repeat_type == self.REPEAT_DAILY:
			return self.start_date + timedelta(days=occurrence_index)
		if self.repeat_type == self.REPEAT_EVERY_N_DAYS:
			return self.start_date + timedelta(days=occurrence_index * self.repeat_interval)
		if self.repeat_type == self.REPEAT_EVERY_N_MONTHS:
			return self._get_monthly_occurrence(occurrence_index)
		return self.start_date

	def advance_after_completion(self):
		if self.repeat_type == self.REPEAT_ONE_TIME:
			self.is_completed = True
			return

		self.recurrence_count += 1
		self.due_date = self.get_occurrence_date(self.recurrence_count)


class TaskCompletion(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_completions')
	task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='completions')
	title_snapshot = models.CharField(max_length=160)
	completed_due_date = models.DateField()
	completed_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-completed_at', '-pk']

	def __str__(self):
		return f"{self.user.email} completed '{self.title_snapshot}'"
