from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit






class RegisterForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.is_staff = True  # Gán quyền staff status
        if commit:
            user.save()
        return user


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    class Meta:
        model = Post
        exclude = ['author', 'likes', 'view_count'] 
        # widgets = {
        #     'content': CKEditorWidget(config_name='default')
        # }
        
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Select one or more categories for the post." 
    )
    helper = FormHelper()
    helper.form_method = 'post'
    helper.layout = Layout(
        'categories',
        Submit('submit', 'Create Post')
    )
class UserUpdate(forms.ModelForm):
    
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "avatar"]
        
    def save(self, commit=True):
        user = super(UserUpdate, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user 
    def save_profile(self, commit=True):
        profile, created = UserProfile.objects.get_or_create(user=self.instance)
        profile.avatar = self.cleaned_data['avatar']
        if commit:
            profile.save()
        return profile
        
class CommentForm(forms.ModelForm):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Comment here!',
        'rows': 3,
        'cols': 50
    }))

    class Meta:
        model = Comment
        fields = ['content']


