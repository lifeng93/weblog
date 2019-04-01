# Register your models here.
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User
from django.contrib.auth import password_validation
import re

class UserCreationForm(forms.ModelForm):
	phone = forms.CharField(label="Phone")
	email = forms.EmailField(label="Email", required=False)
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('phone', 'nickname', 'email')

	def clean_phone(self):
		phone = self.cleaned_data.get("phone")
		if phone and re.match(r'^1[34578]\d{9}$', phone) == None:
			raise forms.ValidationError("Phone don't valid")
		return phone


	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def _post_clean(self):
		super()._post_clean()
		password = self.cleaned_data.get('password2')
		if password:
			try:
				password_validation.validate_password(password, self.instance)
			except forms.ValidationError as error:
				self.add_error('password2', error)

	def save(self, commit=True):
		user = super().save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user

class UserChangeForm(forms.ModelForm):
	"""A form for updating users. Includes all the fields on
	the user, but replaces the password field with admin's
	password hash display field.
	"""
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = User
		fields = ('phone', 'password', 'nickname', 'is_active', 'is_admin')

	def clean_password(self):
		# Regardless of what the user provides, return the initial value.
		# This is done here, rather than on the field, because the
		# field does not have access to the initial value
		return self.initial["password"]

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.contrib.auth.models import Group

class UserAdmin(BaseUserAdmin):

	form = UserChangeForm
	add_form = UserCreationForm

	list_display = ('phone', 'nickname', 'email', 'is_admin')
	list_filter = ('is_admin',)
	fieldsets = (
		(None, {'fields': ('phone', 'password')}),
		('Personal info', {'fields': ('nickname', 'email')}),
		('Permissions', {'fields': ('is_admin',)}),
	)
	# add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
	# overrides get_fieldsets to use this attribute when creating a user.
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('phone', 'nickname', 'email', 'password1', 'password2')}
		),
	)
	search_fields = ('phone',)
	ordering = ('phone',)
	filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)

# 【未测】filter_horizontal（）作用是选择 manytomanyfiled 字段的值。
# 注意：如果user模型中没有 manytomanyfield 需要在admin中修改，一定要加上此句。
# 不然django会自动将groups左右filter_horizontal的参数来供用户选择，
# 而本例中在定义user模型是未定义groups，会导致报错。

# unregister the Group model from admin.
