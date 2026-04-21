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
