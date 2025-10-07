from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.views.generic import CreateView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .forms import StudentProfileForm 
from .forms import StudentProfileForm, PropertyForm


#returns the index page for unauthorized users, student dashboard for students, and property owner dashboard for property owners
from django.shortcuts import render

def index(request):
        user = request.user
        if user.is_anonymous: 
            #if user isnt logged in  
            return render(request, 'index.html')
        
        elif user.is_student:
            # user is student
            return render(request, 'seeker_dashboard.html')
        elif not user.is_student:
            # user is teacher 
            return render(request, 'Lister_dashboard.html')
        else:
            # not logged in at all 
            # either show generic landing page 
            # or redirect to login 
            return render(request, 'index.html')


    

# directs user to student signup form
def StudentSignupView(request):
    #if user submits
    if request.method == 'POST':
        user_form = StudentSignupform(request.POST)
        profile_form = StudentProfileform(request.POST, request.FILES)#REQUEST.FILES saves images submitted via form, important

        #if both user and profile forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save() #save form details as user variable
            user.is_student = True #set student to seeker
            user.save() #save user variable to db
            
            profile = profile_form.save(commit=False)#save form details as profile variable
            profile.user = user # set user as profile owner
            profile.save()#save user variable to db

            return redirect('registration_successful')  # Redirect to a success page
    else: #else return to form
        user_form = StudentSignupform()
        profile_form = StudentProfileform()
    return render(request, 'student_signup.html', {'user_form': user_form, 'profile_form': profile_form})


#direct to success page
def registration_successful(request):
    return render(request, 'registration_successful.html')


# directs user to property Lister signup form/Lister profile form
def PropListerSignupView(request):
    #if user submits
    if request.method == 'POST':
        user_form = StudentSignupform(request.POST)
        profile_form = StudentProfileform(request.POST, request.FILES)#REQUEST.FILES saves images submitted via form, important

        #if both user and profile forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()#save form details as user variable
            user.is_student = False #set student to Lister
            user.save()  #save user variable to db
            
            profile = profile_form.save(commit=False) #save form details as profile variable
            profile.user = user # set user as profile owner
            profile.save() #save user variable to db

            return redirect('registration_successful')  # Redirect to a success page
    else: #else return to form
        user_form = StudentSignupform()
        profile_form = StudentProfileform()
    return render(request, 'Lister_signup.html', {'user_form': user_form, 'profile_form': profile_form})
    

# uses built in django login form to log in user
class LoginView(LoginView):
    template_name = 'login.html'


# function to log out user and directs them to index page
def logout_user(request):
    logout(request)
    return redirect("/")


# retrieves all properties from database and displays them on the property list page
def property_list(request):
    properties = Property.objects.exclude(ongoing=False).order_by('-created_at')  # Order by creation date, newest first

    # Filter based on property_name
    property_name_query = request.GET.get('property_name')
    if property_name_query:
        properties = properties.filter(property_name__icontains=property_name_query)

    # Filter based on price
    price_query = request.GET.get('price')
    if price_query:
        properties = properties.filter(price__lte=price_query)
    
    # Filter based on property lister's Degree 
    selected_degree = request.GET.get('degree')
    if selected_degree:
        properties = properties.filter(user__student_profile__degree__name=selected_degree)

    # Filter based on property lister's university
    selected_university = request.GET.get('university')
    if selected_university:
        properties = properties.filter(user__student_profile__university__name=selected_university)

    # Retrieve all degrees and universities
    all_degrees = Degrees.objects.all()
    all_universities = Universities.objects.all()

    context = {'properties': properties, 'all_degrees': all_degrees, 
               'selected_degree': selected_degree, 'all_universities': all_universities}
    return render(request, 'property_list.html', context)


#directs user to apply for rent form, must be logged in to access
@login_required
def apply_for_rent(request, property_id):
    property = Property.objects.get(pk=property_id)

   #if user submits
    if request.method == 'POST':
        form = RentalApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.property = property
            application.save()
            return redirect('application_successful')
    else:
        form = RentalApplicationForm()

    return render(request, 'apply_for_rent.html', {'form': form, 'property': property})


#directs user to create listing form, must be logged in to access
@login_required
def create_listing(request):

    #if user submits
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES) #REQUEST.FILES saves images submitted via form, important
        #if form is valid
        if form.is_valid():
            application = form.save(commit=False) #set form infomation as application variable
            application.user = request.user #set applications user to the user filling out form
            application.save() #save to db
            return redirect('application_successful')
    else: #else resubmit form
        form = PropertyForm()

    return render(request, 'create_listing.html', {'form': form})

#View user profile who's ID has been passed in the url
def view_profile(request, user_id):
    user = User.objects.get(id=user_id)
    is_following = False  # Initialize the variable indicating the user is not following (used in template)
    
    #if following
    if Follow.objects.filter(follower=request.user, followed_user=user).exists():
        is_following = True # Changes the variable to following
    
    #if the user is a lister, pass properties
    if user.is_student == False:
        properties = Property.objects.filter(user=user)
        return render(request, 'view_profile.html', {'user': user, 'properties': properties, 'is_following': is_following})
    else:
        return render(request, 'view_profile.html', {'user': user, 'is_following': is_following})


#directs user to application successful page
def application_successful(request):
    return render(request, 'application_successful.html')


#directs user to owner dashboard, must be logged in to access, displays all properties user created and applications for each property
@login_required
def Listing_hub(request):
    properties = Property.objects.filter(user=request.user) #filter to be user's properties
    applications = RentalApplication.objects.filter(property__in=properties).exclude(status='declined') #Filter to be user's applications who have not been declined

    return render(request, 'Listings_hub.html', {'properties': properties, 'applications': applications})


#directs my applications page, must be logged in to access, displays all applications user created
@login_required
def my_applications(request):
    # Retrieve applications for the current user
    applications = RentalApplication.objects.filter(user=request.user) #retrieve user's applications

    return render(request, 'my_applications.html', {'applications': applications})


#directs user to individual property page, displays all information about the individual property passed in the url
def property_individual(request, prodid):
    property = Property.objects.get(id=prodid) #retrieve property that has the id passed in the url
    user_already_applied = RentalApplication.objects.filter(property=property, user=request.user).exists() #creates variable stating if user has already applied (used in template)
    
    #if user has not viewed before
    if not PropertyView.objects.filter(user=request.user, property=property).exists():
        # If not, create a new PropertyView instance
        PropertyView.objects.create(user=request.user, property=property)

        # Increment the view count
        property.view_count += 1
        property.save()

    return render(request, 'Individual_property.html', {'property': property, 'user_already_applied': user_already_applied})


#Accepting an applicants application
def accept_applicant(request, application_id):
    # Use get_object_or_404 to get an Application object or raise a 404 error if not found
    app_instance = get_object_or_404(RentalApplication, id=application_id)
    
    app_instance.status = 'accepted' #set application status to accepted
    app_instance.save() #save to db
    app_instance.create_receipt()  # Generate the receipt upon acceptance
    
    #Close listing from Public
    property = app_instance.property #set applied property as property variable
    property.ongoing = False #sets Ongoing variable to false, taking it off the main site
    property.save() #save to db

    # Render the accept template with appropriate context
    return render(request, 'accept_applicant.html', {'application': app_instance})


#Declining an applicant
def decline_applicant(request, application_id):
    # Use get_object_or_404 to get an Application object or raise a 404 error if not found
    app_instance = get_object_or_404(RentalApplication, id=application_id)
    
    app_instance.status = 'declined' #set application status o decline
    app_instance.save() #save to db

    # Render the decline template with appropriate context
    return render(request, 'decline_applicant.html', {'application': app_instance})


#Function passed to intiate following a user
def follow_user(request, followed_user_id):
    #if user is logged in
    if request.user.is_authenticated:
        is_following = True  # Initialize the variable indicating whether the user is following
        followed_user = User.objects.get(pk=followed_user_id)  #set followed user to the user who's ID was passed in the URL
        properties = Property.objects.filter(user=followed_user) #get followed users properties
        if followed_user != request.user:  # Ensure user can't follow themselves
            Follow.objects.get_or_create(follower=request.user, followed_user=followed_user) #create Follow object in models
    #go to followed users page
    return render(request,'view_profile.html', {'user':followed_user, 'is_following': is_following, 'properties':properties})  # Update to the correct profile URL pattern


#Function passed to intiate unfollowing a user
def unfollow_user(request, followed_user_id):
    is_following = False  # Initialize the variable indicating whether the user is following
    #if user is logged in
    if request.user.is_authenticated:
        followed_user = User.objects.get(pk=followed_user_id) #set followed user to the user who's ID was passed in the URL
        properties = Property.objects.filter(user=followed_user) #get followed users properties
        Follow.objects.filter(follower=request.user, followed_user=followed_user).delete() #delete follow obj in models
    #go to unfollowed users page
    return render(request,'view_profile.html', {'user':followed_user, 'is_following': is_following, 'properties':properties}) 


#View all followers of User who's ID was passed in the URL
def followers_view(request, user_id):
    user = User.objects.get(pk=user_id)
    followers = user.followers.all()
    properties = Property.objects.filter(user=user)
    return render(request, 'followers.html', {'user': user, 'followers': followers, 'properties':properties})


#View all users being followed by the User who's ID was passed in the URL
def following_view(request, user_id):
    user = User.objects.get(pk=user_id)
    following = user.following.all()
    properties = Property.objects.filter(user=user)
    return render(request, 'following.html', {'user': user, 'following': following, 'properties':properties})


@login_required
def edit_profile(request):
    #if user Submits
    if request.method == 'POST':
        user_profile_form = StudentProfileForm(request.POST, request.FILES, instance=request.user.student_profile)
        user = request.user
        property_forms = [PropertyForm(request.POST, request.FILES, instance=property, prefix=f"property_{property.id}") for property in Property.objects.filter(user=user)]
        
        # Check if all forms are valid then save form and return to view_profile
        if user_profile_form.is_valid() and all(form.is_valid() for form in property_forms):
            user_profile_form.save() #Save changes made to DB 
            for form in property_forms:
                form.save() #Save changes made to DB 
            return redirect('view_profile', user_id=request.user.id)
    else: #else resubmit form 
        user_profile_form = StudentProfileForm(instance=request.user.student_profile)
        property_forms = [PropertyForm(instance=property, prefix=f"property_{property.id}") for property in Property.objects.filter(user=request.user)]

    # Pass both the user profile form and the property forms to the edit_profile template
    return render(request, 'edit_profile.html', {'user_profile_form': user_profile_form,'property_forms': property_forms})


#Allows users to delete an application they have made
@login_required
def delete_application(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(RentalApplication, id=application_id)
        # Check if the logged-in user owns this application or if they have permission to delete it
        if application.user == request.user:
            application.delete()
            applications = RentalApplication.objects.filter(user=request.user)
            return render(request, 'my_applications.html', {'applications': applications})
        else:
            error_msg = 'Unable to delete application due to internal error, please contact support team'
            applications = RentalApplication.objects.filter(user=request.user)
            return render(request, 'my_applications.html', {'applications': applications, 'error_msg':error_msg})
    else:
        # Handle GET request if needed
        pass


#Delete a property listing
@login_required
def delete_property(request, property_id):
    #if form is submitted (Delete property button)
    if request.method == 'POST':
        property = get_object_or_404(Property, id=property_id)
        # Check if the logged-in user owns this property or if they have permission to delete it
        if property.user == request.user:
            property.delete() #delete the property passed in the url
            properties = Property.objects.filter(user=request.user) # retrieve properties owned by user
            applications = RentalApplication.objects.filter(property__in=properties) # retreieve applications for properties
            return render(request, 'Listings_hub.html', {'properties': properties, 'applications': applications})
        else: #else resubmit
            properties = Property.objects.filter(user=request.user)
            applications = RentalApplication.objects.filter(property__in=properties)
            return render(request, 'Listings_hub.html', {'properties': properties, 'applications': applications})
    else:
        pass

