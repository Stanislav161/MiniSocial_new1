# social_network/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import Profile, Post, Comment


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', placeholder='Введите имя пользователя'),
            Field('email', placeholder='Введите email'),
            Field('password1', placeholder='Введите пароль'),
            Field('password2', placeholder='Повторите пароль'),
            Submit('submit', 'Зарегистрироваться', css_class='btn btn-success w-100 mt-3')
        )

        # Добавляем классы Bootstrap
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[fieldname].label
            })


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'email']:
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control'
            })


class ProfileUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'дд.мм.гггг'
        }),
        input_formats=['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']
    )

    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com'
        })
    )

    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'website', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            # ВАЖНО: ClearableFileInput показывает флажок "Очистить"
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем profile_picture НЕОБЯЗАТЕЛЬНЫМ, чтобы флажок "Очистить" работал
        self.fields['profile_picture'].required = False

        # Остальные поля необязательные
        for field in ['bio', 'location', 'birth_date', 'website']:
            self.fields[field].required = False

        # Начальное значение для даты
        if self.instance and self.instance.birth_date:
            self.fields['birth_date'].initial = self.instance.birth_date.strftime('%Y-%m-%d')


    def clean_profile_picture(self):
        """Валидация поля profile_picture"""
        profile_picture = self.cleaned_data.get('profile_picture')

        # Если поле пустое, это значит "не менять текущее изображение"
        # Django ClearableFileInput обрабатывает очистку через флажок "Очистить"
        return profile_picture

    def save(self, commit=True):
        """Сохраняем форму с обработкой profile_picture"""
        profile = super().save(commit=False)

        # Проверяем, был ли отмечен флажок "Очистить"
        # В Django ClearableFileInput, если пользователь отметил "Очистить",
        # то в cleaned_data будет profile_picture = False
        profile_picture = self.cleaned_data.get('profile_picture')

        if profile_picture is False:
            # Пользователь отметил "Очистить" - удаляем аватарку
            if profile.profile_picture:
                profile.profile_picture.delete(save=False)
            profile.profile_picture = None
        elif profile_picture is None:
            # Пользователь ничего не выбрал - оставляем текущее значение
            if self.instance and hasattr(self.instance, 'profile_picture'):
                profile.profile_picture = self.instance.profile_picture

        if commit:
            profile.save()

        return profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Что у вас нового?'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Напишите комментарий...'
            })
        }