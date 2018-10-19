from django.db import models

# Create your models here.

class NewsPiece(models.Model):
	news_title = models.CharField(max_length=200)
	news_content = models.CharField(max_length=10000)
	pub_date = models.CharField(max_length=200)
	news_abstract = models.CharField(max_length=200)
	def __str__(self):
		return self.news_title

class Tag(models.Model):
	newspiece = models.ForeignKey(
		NewsPiece, 
		on_delete=models.CASCADE, 
	)
	name = models.CharField(max_length=255)
	def __str__(self):
		return self.name

class ContentTag(models.Model):
	newspiece = models.ForeignKey(
		NewsPiece,
		on_delete=models.CASCADE,
	)
	name = models.CharField(max_length=255)
	def __str__(self):
		return self.name
