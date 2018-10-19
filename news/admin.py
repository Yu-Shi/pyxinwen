from django.contrib import admin

# Register your models here.
from .models import NewsPiece, Tag, ContentTag

admin.site.register(NewsPiece)
admin.site.register(Tag)
admin.site.register(ContentTag)