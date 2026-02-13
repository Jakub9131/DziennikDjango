from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.db.models import Q 
from .models import Grade, User, ClassGroup, Subject, SubjectAssignment
from .forms import (
    ClassGroupForm, TeacherCreationForm, SubjectForm, 
    AssignTeacherForm, StudentBasicForm, ParentBasicForm
)


def role_required(role_name):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role == role_name or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied 
        return _wrapped_view
    return decorator



@login_required
def dashboard_router(request):
    if request.user.role == 'admin' or request.user.is_superuser:
        return redirect('admin_dashboard') 
    elif request.user.role == 'teacher':
        return redirect('teacher_panel')
    elif request.user.role == 'parent':
        return redirect('parent_panel')
    else:
        return redirect('student_panel')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Twoje hasło zostało pomyślnie zmienione!')
            return redirect('dashboard_router')
        else:
            messages.error(request, 'Popraw błędy w formularzu.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'core/change_password.html', {'form': form})



@role_required('student')
def student_panel(request):
    grades_list = Grade.objects.filter(student=request.user).select_related('subject', 'teacher').order_by('subject__name')
    all_values = [g.value for g in grades_list]
    average = round(sum(all_values) / len(all_values), 2) if all_values else 0
    
    return render(request, 'core/student_dashboard.html', {
        'grades_list': grades_list,
        'average': average
    })

@role_required('teacher')
def teacher_panel(request):
    assignments = SubjectAssignment.objects.filter(teacher=request.user).select_related('subject', 'class_group')
    return render(request, 'core/teacher_dashboard.html', {'assignments': assignments})

@role_required('parent')
def parent_panel(request):
    children = User.objects.filter(parent=request.user).prefetch_related(
        'grades_received__subject', 'grades_received__teacher'
    ).select_related('class_group')

    for child in children:
        child.grades_list = child.grades_received.all().order_by('subject__name')
        all_values = [g.value for g in child.grades_list]
        child.average = round(sum(all_values) / len(all_values), 2) if all_values else 0
        child.teachers_contact = {g.teacher for g in child.grades_list}

    return render(request, 'core/parent_dashboard.html', {'children': children})


@role_required('admin')
def admin_dashboard(request):
    stats = {
        'total_students': User.objects.filter(role='student').count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_classes': ClassGroup.objects.count(),
        'total_subjects': Subject.objects.count(),
    }

    student_q = request.GET.get('student_q', '')
    teacher_q = request.GET.get('teacher_q', '')

    classes = ClassGroup.objects.all().order_by('name')
    subjects = Subject.objects.all().order_by('name')
    students = User.objects.filter(role='student').select_related('class_group', 'parent').order_by('last_name')
    teachers = User.objects.filter(role='teacher').order_by('last_name')

    if student_q:
        students = students.filter(Q(last_name__icontains=student_q) | Q(first_name__icontains=student_q) | Q(email__icontains=student_q))
    if teacher_q:
        teachers = teachers.filter(Q(last_name__icontains=teacher_q) | Q(first_name__icontains=teacher_q) | Q(email__icontains=teacher_q))

    class_form = ClassGroupForm()
    subject_form = SubjectForm()
    teacher_form = TeacherCreationForm()
    assign_form = AssignTeacherForm()
    student_f = StudentBasicForm(prefix='student')
    parent_f = ParentBasicForm(prefix='parent')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_class':
            class_form = ClassGroupForm(request.POST)
            if class_form.is_valid():
                obj = class_form.save(commit=False)
                obj.name = obj.name.upper().strip()
                obj.save()
                messages.success(request, f"Klasa {obj.name} dodana!")
                return redirect('/admin-panel/#dashboard-pane')

        elif action == 'add_subject':
            subject_form = SubjectForm(request.POST)
            if subject_form.is_valid():
                subject_form.save()
                messages.success(request, "Przedmiot dodany!")
                return redirect('/admin-panel/#dashboard-pane')

        elif action == 'add_teacher':
            teacher_form = TeacherCreationForm(request.POST)
            if teacher_form.is_valid():
                teacher = teacher_form.save(commit=False)
                teacher.username = teacher.email 
                teacher.role = 'teacher'
                teacher.password = make_password('nauczyciel123')
                teacher.save()
                messages.success(request, f"Nauczyciel {teacher.first_name} utworzony!")
                return redirect('/admin-panel/#staff-pane')

        elif action == 'assign_teacher':
            assign_form = AssignTeacherForm(request.POST)
            if assign_form.is_valid():
                teacher = assign_form.cleaned_data['teacher']
                subject = assign_form.cleaned_data['subject']
                class_group = assign_form.cleaned_data['class_group']
                SubjectAssignment.objects.update_or_create(
                    subject=subject, class_group=class_group, 
                    defaults={'teacher': teacher}
                )
                messages.success(request, f"Przypisano {teacher.last_name} do {subject.name}")
                return redirect('/admin-panel/#staff-pane')

        elif action == 'add_student_parent':
            student_f = StudentBasicForm(request.POST, prefix='student')
            parent_f = ParentBasicForm(request.POST, prefix='parent')
            if student_f.is_valid() and parent_f.is_valid():
                try:
                    with transaction.atomic():
                        parent = parent_f.save(commit=False)
                        parent.username = parent.email
                        parent.role = 'parent'
                        parent.password = make_password('rodzic123')
                        parent.save()
                        student = student_f.save(commit=False)
                        student.username = student.email
                        student.role = 'student'
                        student.password = make_password('uczen123')
                        student.parent = parent
                        student.save()
                    messages.success(request, f"Dodano duet: {student.last_name} + Rodzic")
                    return redirect('/admin-panel/#students-pane')
                except Exception as e:
                    messages.error(request, f"Błąd bazy danych: {e}")

    return render(request, 'core/admin_dashboard.html', {
        'stats': stats, 'classes': classes, 'teachers': teachers, 'subjects': subjects,
        'students': students, 'class_form': class_form, 'subject_form': subject_form,
        'teacher_form': teacher_form, 'assign_form': assign_form,
        'student_f': student_f, 'parent_f': parent_f,
        'student_search': student_q, 'teacher_search': teacher_q
    })


@role_required('admin')
def edit_student_family(request, student_id):
    student = get_object_or_404(User, id=student_id, role='student')
    parent = student.parent
    if request.method == 'POST':
        s_form = StudentBasicForm(request.POST, instance=student, prefix='student')
        p_form = ParentBasicForm(request.POST, instance=parent, prefix='parent') if parent else None
        if s_form.is_valid() and (not p_form or p_form.is_valid()):
            with transaction.atomic():
                s_form.save()
                if p_form: p_form.save()
            messages.success(request, "Zaktualizowano dane rodziny.")
            return redirect('/admin-panel/#students-pane')
    else:
        s_form = StudentBasicForm(instance=student, prefix='student')
        p_form = ParentBasicForm(instance=parent, prefix='parent') if parent else None
    return render(request, 'core/edit_student_family.html', {'s_form': s_form, 'p_form': p_form, 'student': student})

@role_required('admin')
def delete_student_family(request, student_id):
    student = get_object_or_404(User, id=student_id, role='student')
    if student.parent: student.parent.delete()
    student.delete()
    messages.success(request, "Usunięto rodzinę.")
    return redirect('/admin-panel/#students-pane')

@role_required('admin')
def delete_class(request, class_id):
    class_obj = get_object_or_404(ClassGroup, id=class_id)
    if class_obj.user_set.count() > 0:
        messages.error(request, "Klasa posiada uczniów!")
    else:
        class_obj.delete()
        messages.success(request, "Klasa usunięta.")
    return redirect('/admin-panel/#dashboard-pane')

@role_required('admin')
def delete_teacher(request, teacher_id):
    get_object_or_404(User, id=teacher_id, role='teacher').delete()
    messages.success(request, "Nauczyciel usunięty.")
    return redirect('/admin-panel/#staff-pane')

@role_required('admin')
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if SubjectAssignment.objects.filter(subject=subject).exists():
        messages.error(request, "Przedmiot jest przypisany!")
    else:
        subject.delete()
        messages.success(request, "Przedmiot usunięty.")
    return redirect('/admin-panel/#dashboard-pane')

@role_required('admin')
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST, instance=teacher)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.username = teacher.email 
            teacher.save()
            messages.success(request, f"Zaktualizowano nauczyciela {teacher.last_name}")
            return redirect('/admin-panel/#staff-pane')
    else:
        form = TeacherCreationForm(instance=teacher)
    return render(request, 'core/edit_teacher.html', {'form': form, 'teacher': teacher})

@role_required('admin')
def teacher_details(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
    assignments = SubjectAssignment.objects.filter(teacher=teacher).select_related('subject', 'class_group').order_by('class_group__name')
    return render(request, 'core/teacher_details.html', {'teacher': teacher, 'assignments': assignments})

@role_required('admin')
def remove_assignment(request, assignment_id):
    assignment = get_object_or_404(SubjectAssignment, id=assignment_id)
    teacher_id = assignment.teacher.id # Zapamiętujemy ID, żeby wrócić na ten sam profil
    assignment.delete()
    messages.success(request, "Przypisanie zostało usunięte.")
    return redirect('teacher_details', teacher_id=teacher_id)

@role_required('teacher')
def class_grades_detail(request, class_id, subject_id):
    group = get_object_or_404(ClassGroup, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    students = User.objects.filter(class_group=group, role='student').order_by('last_name')
    grades = Grade.objects.filter(subject=subject, student__class_group=group).select_related('student')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_grade':
            student = get_object_or_404(User, id=request.POST.get('student_id'), role='student')
            Grade.objects.create(
                student=student, teacher=request.user, subject=subject,
                value=request.POST.get('value'), comment=request.POST.get('comment', '')
            )
            messages.success(request, f"Dodano ocenę dla: {student.last_name}")
        elif action == 'edit_grade':
            grade = get_object_or_404(Grade, id=request.POST.get('grade_id'), teacher=request.user)
            grade.value = request.POST.get('value')
            grade.comment = request.POST.get('comment', '')
            grade.save()
            messages.success(request, "Zaktualizowano ocenę.")
        elif action == 'delete_grade':
            get_object_or_404(Grade, id=request.POST.get('grade_id'), teacher=request.user).delete()
            messages.success(request, "Usunięto ocenę.")
        return redirect('class_grades_detail', class_id=class_id, subject_id=subject_id)

    return render(request, 'core/class_grades_detail.html', {
        'group': group, 'subject': subject, 'students': students, 'grades': grades,
    })