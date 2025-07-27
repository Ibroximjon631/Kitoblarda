from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .models import Category, Book

class BookListView(ListView):
    model = Book
    template_name = 'books/book/list.html'
    context_object_name = 'books'
    paginate_by = 12  # Har bir sahifada 12 ta kitob

    def get_queryset(self):
        queryset = Book.objects.select_related('category').all()
        category_slug = self.kwargs.get('category_slug')
        search_query = self.request.GET.get('q')
    
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            # messages.info(self.request, f"'{search_query}' uchun qidiruv natijalari")

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = getattr(self, 'category', None)
        context['search_query'] = self.request.GET.get('q', '')
        
        # Pagination
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        
        context['books'] = books
        return context

class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book/detail.html'
    context_object_name = 'book'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Book.objects.select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        
        # Tegishli kitoblarni qo'shamiz
        context['related_books'] = Book.objects.filter(
            category=book.category
        ).exclude(
            id=book.id
        )[:4]  # Bir xil kategoriyadan 4 ta kitob
        
        return context

class CategoryListView(ListView):
    model = Category
    template_name = 'books/category/list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_books'] = Book.objects.count()
        return context
