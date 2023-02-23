from django.contrib import admin

from reviews.models import Title, Review, Genre, Comment

admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Genre)
admin.site.register(Comment)
