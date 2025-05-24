from datetime import timedelta
from unicodedata import category
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Category
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, ProfileForm, RegistrationForm
from .models import Profile
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from myapp.utils import send_task_reminder_email
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .forms import CommentForm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
import json
from .models import Task
from django.utils.dateformat import format
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

# Create your views here.
def home(request):
    return render(request, "home.html")

@login_required
@require_GET
def calendar_view(request):
    return render(request, "calendar.html")

@login_required
@require_GET
def tasks_calendar_api(request):
    tasks = Task.objects.filter(user=request.user, due_date__isnull=False)
    events = []
    for task in tasks:
        events.append({
            "id": task.id,
            "title": task.title,
            "start": task.due_date.isoformat(),
            "url": f"/task_detail/{task.id}/",
            "allDay": False,
        })
    return JsonResponse(events, safe=False)


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Task
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json

# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def toggle_task_completion(request):
    task_id = request.POST.get('task_id')
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.is_completed = request.POST.get('is_completed') == 'true'
        task.save()
        return JsonResponse({'success': True})
    except Task.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@login_required
@require_POST
@csrf_exempt
def toggle_task_completion(request):
    task_id = request.POST.get('task_id')
    is_completed = request.POST.get('is_completed') == 'true'

    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.is_completed = is_completed
        task.save()
        return JsonResponse({'success': True, 'is_completed': task.is_completed})
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found or unauthorized'}, status=404)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def reorder_tasks(request):
    try:
        data = json.loads(request.body)
        ordered_task_ids = data.get('ordered_task_ids', [])
        # Update the order field of tasks based on the new order
        for order, task_id in enumerate(ordered_task_ids):
            task = Task.objects.filter(id=task_id, user=request.user).first()
            if task:
                task.order = order
                task.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('task_detail', task_id=task_id)
    else:
        form = CommentForm()

    return render(request, "task_detail.html", {"task": task, "comments": comments, "form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Retrieve failed attempts from session
        failed_attempts = request.session.get("failed_attempts", 0)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Reset failed attempts on successful login
            request.session["failed_attempts"] = 0
            login(request, user)
            messages.success(request, f"You are now logged in as {username}")
            return redirect("task_list")
        else:
            # Increment failed attempts if authentication fails
            failed_attempts += 1
            request.session["failed_attempts"] = failed_attempts
            messages.error(request, "Invalid username or password")

    else:
        # If GET request, just load the page
        failed_attempts = request.session.get("failed_attempts", 0)

    # Show "Forgot Password?" link if failed attempts >= 3
    show_forgot_password = failed_attempts >= 3

    return render(request, "account/login.html", {"show_forgot_password": show_forgot_password})


@csrf_exempt
def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Manual user creation
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                messages.success(request, "Registration successful! Please login.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Error creating user: {str(e)}")
        else:
            # Pass errors to template
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = RegistrationForm()

    return render(request, "account/signup.html", {
        'form': form,
        'preserve_values': {
            'username': request.POST.get('username', ''),
            'email': request.POST.get('email', '')
        }
    })


def logout_view(request):
    logout(request)
    return redirect("home")


from django.db import IntegrityError, models

def task_list(request):
    if not request.user.is_authenticated:
        return redirect("login")

    category_id = request.GET.get("category")
    sort_by = request.GET.get("sort_by")

    # Base query with parent task filtering
    base_query = (
        models.Q(user=request.user) | 
        models.Q(shared_users=request.user)
    ) & models.Q(parent_task__isnull=True)  # Only show parent tasks

    if category_id:
        tasks = Task.objects.filter(base_query, category_id=category_id).distinct()
    else:
        tasks = Task.objects.filter(base_query).distinct()

    # Sorting
    if sort_by == "priority":
        tasks = tasks.order_by('priority')
    elif sort_by == "due_date":
        tasks = tasks.order_by('due_date')
    else:
        tasks = tasks.order_by('created_at')

    categories = Category.objects.filter(user=request.user)
    
    return render(request, 'task_list.html', {
        'tasks': tasks,
        'categories': categories,
        'sort_by': sort_by,
    })


from .forms import TaskForm
@login_required(login_url="login")


@login_required(login_url="login")
def task_create(request):
    # Create default categories if none exist
    if not Category.objects.filter(user=request.user).exists():
        default_categories = ["Work", "Personal", "Shopping", "Health", "Finance",
                             "Education", "Home", "Travel", "Fitness", "Others"]
        for name in default_categories:
            Category.objects.create(name=name, user=request.user)

    categories = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                task = form.save(commit=False)
                task.user = request.user
                
                # Handle category creation/selection
                handle_category(request, task)
                
                task.save()
                form.save_m2m()

                # Recurrence handling
                if task.recurrence != 'none' and task.due_date:
                    from datetime import timedelta
                    recurrence_count = 1
                    current_due_date = task.due_date
                    
                    for _ in range(recurrence_count):
                        current_due_date += timedelta(
                            days=1 if task.recurrence == 'daily' else
                            7 if task.recurrence == 'weekly' else 30
                        )
                        Task.objects.create(
                            user=task.user,
                            title=f"{task.title} (Recurring)",
                            description=task.description,
                            due_date=current_due_date,
                            category=task.category,
                            priority=task.priority,
                            parent_task=task,
                            recurrence='none'
                        )

                messages.success(request, "Task created successfully")
                return redirect("task_list")

            except IntegrityError:
                messages.error(request, "Duplicate task detected!")
            except Exception as e:
                messages.error(request, f"Error creating task: {str(e)}")
            
            return redirect("task_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TaskForm()

    return render(request, "task_create.html", {
        "form": form,
        "categories": categories,
    })
def handle_category(request, task):
    """Handle category creation/selection"""
    new_category_name = request.POST.get('new_category', '').strip()
    
    if new_category_name:
        # Create or get existing category
        category, created = Category.objects.get_or_create(
            name=new_category_name,
            user=request.user,
            defaults={'user': request.user}
        )
        
        if not created:
            messages.info(request, f"Category '{new_category_name}' already exists")
        else:
            messages.success(request, f"Created new category '{new_category_name}'")
        
        task.category = category
    else:
        category_id = request.POST.get('category')
        if category_id:
            try:
                task.category = Category.objects.get(id=category_id, user=request.user)
            except Category.DoesNotExist:
                messages.error(request, "Invalid category selected")
                task.category = None
        else:
            task.category = None

@login_required(login_url="login")
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.user != request.user:
        raise Http404

    categories = Category.objects.filter(user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            try:
                task = form.save(commit=False)
                handle_category(request, task)
                task.save()
                form.save_m2m()
                
                messages.success(request, "Task updated successfully")
                return redirect("task_list")
            
            except IntegrityError:
                messages.error(request, "Duplicate task detected!")
            except Exception as e:
                messages.error(request, f"Error updating task: {str(e)}")
            
            return redirect("task_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TaskForm(instance=task)

    return render(request, "task_create.html", {
        "form": form,
        "categories": categories,
        "task": task
    })

@login_required(login_url="login")
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.delete()
        messages.success(request, "Task delete successfully")
        return redirect("task_list")

    return render(request, "delete_task.html", {"task": task})


from .forms import TaskForm



@login_required(login_url="login")
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('task_detail', task_id=task_id)
    else:
        form = CommentForm()

    return render(request, "task_detail.html", {"task": task, "comments": comments, "form": form})


from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

@login_required
def profile(request):
    # Ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        profile_pic = request.FILES.get('profile_pic')

        profile.bio = bio
        if profile_pic:
            profile.profile_pic = profile_pic
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('profile')  # Redirect after saving

    return render(request, 'profile.html', {'profile': profile})

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = "registration/password_change_form.html"
    success_message = "Password changed successfully!"
    success_url = reverse_lazy('password_change_done')




def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


def update_profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')  # Redirect after saving

    else:
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'profile.html', {'profile_form': profile_form})

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

@login_required
@require_GET
def check_new_notifications(request):
    # For demonstration, return static notifications
    notifications = [
        {"message": "You have a task due soon!"},
    ]
    return JsonResponse({"new_notifications": notifications})

