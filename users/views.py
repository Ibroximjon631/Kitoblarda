from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic import FormView, UpdateView, ListView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from .forms import UserRegistrationForm, UserLoginForm

# Create your views here.

class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('books:book_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, "Muvaffaqiyatli ro'yxatdan o'tdingiz!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Iltimos, xatoliklarni to'g'rilang.")
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Siz allaqachon tizimga kirmissiz.")
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('books:book_list')

    def form_valid(self, form):
        phone = form.cleaned_data.get('phone')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, phone=phone, password=password)
        
        if user is not None:
            login(self.request, user)
            messages.success(self.request, "Muvaffaqiyatli tizimga kirdingiz!")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Telefon raqam yoki parol noto'g'ri.")
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Siz allaqachon tizimga kirmissiz.")
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('books:book_list')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Muvaffaqiyatli tizimdan chiqdingiz!")
        return super().dispatch(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile.html'
    fields = ['first_name', 'phone']
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


    def form_valid(self, form):
        messages.success(self.request, "Profil muvaffaqiyatli yangilandi!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Iltimos, xatoliklarni to'g'rilang.")
        return super().form_invalid(form)
