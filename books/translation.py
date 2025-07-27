from modeltranslation.translator import register, TranslationOptions
from .models import Book, Category

@register(Book)
class BookTranslationOptions(TranslationOptions):
    fields = ('title','description', 'author')

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
