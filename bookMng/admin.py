from django.contrib import admin

# Register your models here.

from .models import MainMenu
from .models import Book
from .models import Genre


class BookAdmin(admin.ModelAdmin):
    filter_horizontal = ('genres',)


admin.site.register(Genre)

admin.site.register(MainMenu)

admin.site.register(Book, BookAdmin)


