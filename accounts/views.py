from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import LoginForm, ProfileForm, RegisterForm
from .models import User
from django.db.models import Sum
from orders.models import Order


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        name = self.request.user.first_name or self.request.user.username
        messages.success(self.request, f'Welcome back, {name}!')
        return response


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_redirect(request):
    if request.user.role == User.Role.ADMIN:
        return redirect('admin_dashboard')
    return redirect('customer_dashboard')


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    orders = Order.objects.select_related('customer', 'service')
    revenue = Order.objects.filter(status=Order.Status.COMPLETED).aggregate(
        total=Sum('total_price'))['total'] or 0
    context = {
        'total_users': User.objects.count(),
        'total_customers': User.objects.filter(role=User.Role.CUSTOMER).count(),
        'total_admins': User.objects.filter(role=User.Role.ADMIN).count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status=Order.Status.PENDING).count(),
        'revenue': revenue,
        'recent_orders': orders[:5],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@role_required(User.Role.CUSTOMER)
def customer_dashboard(request):
    orders = Order.objects.filter(customer=request.user).select_related('service')
    active = [Order.Status.PENDING, Order.Status.WASHING, Order.Status.READY]
    context = {
        'total_count': orders.count(),
        'active_count': orders.filter(status__in=active).count(),
        'completed_count': orders.filter(status=Order.Status.COMPLETED).count(),
        'recent_orders': orders[:5],
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})