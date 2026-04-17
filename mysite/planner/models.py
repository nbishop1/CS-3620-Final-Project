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
