from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator, ValidationError
from django.contrib.auth.models import User
from datetime import date
from django.utils.timezone import now



# Predefined choices for the gender field in User model
genders = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

# Custom user model extending the default AbstractUser to include additional fields
class User(AbstractUser):
    id = models.AutoField(primary_key=True)  # Unique ID for each user
    is_student = models.BooleanField(default=False)  # Flag to determine if the user is a student
    gender = models.CharField(max_length=20, choices=genders, default="Male")  # User's gender

    def __str__(self):
        return self.username  # Display name for the User model in admin panel

    def followers_count(self):
        return self.followers.count()  # Return the number of followers

    def following_count(self):
        return self.following.count()  # Return the number of following users

# Validator function to ensure a non-negative value
def non_negative_validator(value):
    if value < 0:
        raise ValidationError("Value cannot be negative.")

# Model to represent academic degrees
class Degrees(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=35)  # Name of the degree

    def __str__(self):
        return self.name

# Model to represent universities
class Universities(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)  # Name of the university

    def __str__(self):
        return self.name

# Model to represent types of listers in a property listing system
class Lister_type(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)  # Type of lister

    def __str__(self):
        return self.name


class Student_profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to a User instance
    # Personal details and contact information fields
    email = models.EmailField(max_length=255, null=True)
    phone_number = models.CharField(max_length=10, null=True, validators=[RegexValidator(r'^\d{1,10}$')])
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    birth_date = models.DateField(default=date(2000, 1, 1))  # Birth date with a default value
    degree = models.ForeignKey(Degrees, on_delete=models.CASCADE)  # Foreign key to Degrees model
    university = models.ForeignKey(Universities, on_delete=models.CASCADE, null=True)  # Optional link to Universities
    profile_image = models.ImageField(upload_to='media/', null=True, blank=True)
    facebook_link = models.CharField(max_length=32, null=True, blank=True)
    instagram_link = models.CharField(max_length=32, null=True, blank=True)
    linkedin_link = models.CharField(max_length=32, null=True, blank=True)
    personal_page_link = models.CharField(max_length=32, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    

    def calculate_age(self):
        # Calculate age from birth_date
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age

    def full_name(self):
        # Return concatenated first and last name
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.user.username  # Username as the display name

# Model to represent properties listed by users
class Property(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user listing the property
    # Basic property details
    property_name = models.CharField(max_length=25, default="")
    description = models.TextField(default="")
    image = models.ImageField(upload_to='media/', null=True, blank=True)
    price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        null=False,
        validators=[MinValueValidator(0, message="Price cannot be negative.")],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)
    address_line_1 = models.CharField(max_length=255, default='')
    address_line_2 = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=255, default='')
    post_code = models.CharField(max_length=255, default='')
    ongoing = models.CharField(null=False, default=True, max_length=5)

    def get_full_address(self):
        return f"{self.address_line_1}, {self.address_line_2},{self.city}, {self.post_code}"

    def __str__(self):
        return self.property_name  # Name of the property as the display name

#Applications made by student seekers
class RentalApplication(models.Model):
    id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=255)
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
        default='pending'
    )
    receipt_message = models.TextField(blank=True, null=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('property', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.property.property_name}'

    # Generate a receipt message if the application is accepted
    def create_receipt(self):
        if self.status == 'accepted' and not self.receipt_message:
            self.receipt_message = f"Congratulations, {self.user.username}! Your application for '{self.property.property_name}' has been accepted on {now().date()}."
            self.accepted_at = now()
            self.property.is_active = False
            self.property.save()
            self.save()
            
   # Prevent duplicate applications for the same property by the same user
    class Meta:
        unique_together = ('property', 'user')  

    def __str__(self):
        return self.user.username

# Used to keep track of view count for property listings
class PropertyView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    # Ensure each user can view a property only once
    class Meta:
        unique_together = ('user', 'property')  

    def __str__(self):
        return f"{self.user.username} viewed {self.property.property_name}"
    
#Keeps track of following
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # Ensure each user can follow the same user once
    class Meta:
        unique_together = ('follower', 'followed_user') # Each follow relationship is unique
