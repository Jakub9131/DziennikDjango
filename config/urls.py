from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Logowanie i wylogowanie
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Strony dziennika
    path('', views.dashboard_router, name='dashboard_router'),
    path('student/', views.student_panel, name='student_panel'),
    path('teacher/', views.teacher_panel, name='teacher_panel'),
    path('parent/', views.parent_panel, name='parent_panel'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/delete-class/<int:class_id>/', views.delete_class, name='delete_class'),
    path('admin-panel/edit-teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('admin-panel/delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('admin-panel/teacher/<int:teacher_id>/', views.teacher_details, name='teacher_details'),
    path('admin-panel/delete-family/<int:student_id>/', views.delete_student_family, name='delete_student_family'),
    path('admin-panel/delete-subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('admin-panel/edit-family/<int:student_id>/', views.edit_student_family, name='edit_student_family'),
    path('teacher/class/<int:class_id>/subject/<int:subject_id>/', views.class_grades_detail, name='class_grades_detail'),
    path('change-password/', views.change_password, name='change_password'),
    path('assignment/<int:assignment_id>/delete/', views.remove_assignment, name='remove_assignment'),

]