from django.contrib import admin
from .models import Account, Profile, UploadedImage
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField


# Register your models here.
admin.site.register(Profile)
admin.site.register(UploadedImage)

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label = 'Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label = 'Password Confirmation', widget = forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'last_name', 'first_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit = True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Account
        fields = ('email', 'password', 'last_name', 'first_name', 'is_active', 'is_admin')

    def clean_password(self):
        return self.initial["password"]

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
            (None, {'fields': ('email', 'password')}),
            ('First Name', {'fields': ('first_name',)}),
            ('Last Name', {'fields': ('last_name',)}),
            ('Permissions', {'fields': ('is_admin',)}),
            )

    add_fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': ('email', 'last_name', 'first_name', 'password1', 'password2')
                }
                ),
            )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(Account, UserAdmin)
