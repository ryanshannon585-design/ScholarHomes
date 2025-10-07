from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.forms import ModelForm
from .models import * 
from django.db import transaction



# Forms for handling student profiles, including image uploads
class StudentProfileform(forms.ModelForm):
    profile_image = forms.ImageField(required=False)

    class Meta: # Specifies the model associated with this form
        model = Student_profile
        # Fields to include in the form
        fields = [ 'email', 'first_name', 'last_name', 'birth_date', 'university', 'degree', 'bio', 'profile_image', 'facebook_link', 'instagram_link', 'linkedin_link', 'personal_page_link']
    

# Form for student user registration using Django's built-in UserCreationForm
class StudentSignupform(UserCreationForm): 

    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = [ 'username', 'password1', 'password2', 'gender'] # Fields to include in the form
    
    
    @transaction.atomic # Ensures database operations are performed atomically
    def save(self):
        user = super().save(commit=False)  # Saves the form data temporarily without committing to the database
        user.is_student = True  # Set custom user attribute 'is_student' to True
        user.save()  # Finally save the user to the database
        return user



#Lister & Student Signup forms and forms for editing user details
class PropListerProfileform(forms.ModelForm):
    profile_image = forms.ImageField(required=False)

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student_profile
        fields = [ 'email', 'first_name', 'last_name', 'birth_date', 'university', 'degree', 'bio', 'profile_image','facebook_link', 'instagram_link', 'linkedin_link', 'personal_page_link']
    
#Form for property lister registration using UserCreationForm
class PropListerSignupform(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = [ 'username', 'password1', 'password2', 'gender']
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False) # save the details but dont put in database
        user.is_student = False
        user.save()
        return user
  
class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
     # Custom placeholders for the form fields
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Your password'}))

    def clean(self):
        cleaned_data = super().clean() # Call the base clean method to ensure base validation
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if  username and password:
             # Custom validation to ensure username is not the same as the password
            if  username == password:
                raise forms.ValidationError("username and password cannot have the same value.")
    
    
class PropertyForm(ModelForm): # Form to handle property listings including name, description, image, and price
    class Meta:
        model = Property
        fields = ['property_name', 'description', 'image', 'price', 'address_line_1', 'address_line_2', 'city',  'post_code']


class RentalApplicationForm(ModelForm): # Form for handling rental applications with just a message field
    class Meta:
        model = RentalApplication
        fields = ['message']  # Include only the message field in the form
