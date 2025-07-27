from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Book, Category, BookImage, BookVideo
from googletrans import Translator

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1

class BookVideoInline(admin.TabularInline):
    model = BookVideo
    extra = 1

@admin.register(Book)
class BookAdmin(TranslationAdmin):
    inlines = (BookImageInline, BookVideoInline)
    list_display = ('title', 'author', 'category', 'price', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'author', 'description')
    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        translator = Translator()

        if 'title_uz' in form.changed_data and 'title_ru' not in form.changed_data:
            obj.title_ru = translator.translate(obj.title_uz, src='uz', dest='ru').text

        if 'description_uz' in form.changed_data and 'description_ru' not in form.changed_data:
            obj.description_ru = translator.translate(obj.description_uz, src='uz', dest='ru').text

        if 'author_uz' in form.changed_data and 'author_ru' not in form.changed_data:
            obj.author_ru = translator.translate(obj.author_uz, src='uz', dest='ru').text

        super().save_model(request, obj, form, change)

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
        )