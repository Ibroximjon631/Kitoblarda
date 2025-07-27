from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from googletrans import Translator

class Category(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True, max_length=200)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name

class Book(models.Model):
    COVER_CHOICES = [
        ('hard', _('Hard cover')),
        ('soft', _('Soft cover')),
    ]
    title = models.CharField(_('Title'), max_length=200)
    author = models.CharField(_('Author'), max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books', verbose_name=_('Category'))
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    description = models.TextField(_('Description'))
    cover_type = models.CharField(_('Cover type'), max_length=4, choices=COVER_CHOICES)
    pages = models.PositiveIntegerField(_('Number of pages'))
    image = models.ImageField(_('Book image'), upload_to='books/')
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    slug = models.SlugField(_('Slug'), unique=True, max_length=200)

    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images', verbose_name=_('Book'))
    image = models.ImageField(_('Additional image'), upload_to='books/images/')
    uploaded_at = models.DateTimeField(_('Uploaded at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Book image')
        verbose_name_plural = _('Book images')

    def __str__(self):
        return f"Image for {self.book}"

class BookVideo(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='videos', verbose_name=_('Book'))
    url = models.URLField(_('YouTube URL'), blank=True, null=True)
    uploaded_at = models.DateTimeField(_('Uploaded at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Book video')
        verbose_name_plural = _('Book videos')

    def __str__(self):
        return f"Video for {self.book}"

@receiver(pre_save, sender=Book)
def translate_book_fields(sender, instance, **kwargs):
    try:
        old = Book.objects.get(pk=instance.pk)
    except Book.DoesNotExist:
        old = None

    translator = Translator()

    if old is None or (instance.title != old.title and instance.title_ru == old.title_ru):
        instance.title_ru = translator.translate(instance.title, src='uz', dest='ru').text

    if old is None or (instance.description != old.description and instance.description_ru == old.description_ru):
        instance.description_ru = translator.translate(instance.description, src='uz', dest='ru').text

    if old is None or (instance.author != old.author and instance.author_ru == old.author_ru):
        instance.author_ru = translator.translate(instance.author, src='uz', dest='ru').text


@receiver(pre_save, sender=Category)
def translate_category_fields(sender, instance, **kwargs):
    translator = Translator()
    if old is None or (instance.title != old.name and instance.name_ru == old.name_ru):
        instance.name_ru = translator.translate(instance.title, src='uz', dest='ru').text