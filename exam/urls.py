from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from app import views
from app.views import add_question_wizard

urlpatterns = [

    # =====================================================
    # HOME
    # =====================================================
    path('', views.home, name='home'),


    # =====================================================
    # CUSTOM ADMIN PANEL (SAFE FOR HOSTING)
    # =====================================================
    path('panel/login/', views.admin_login, name='admin_login'),
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/logout/', views.admin_logout, name='admin_logout'),

    # ---------------- STUDENT MANAGEMENT ----------------
    path('panel/add-student/', views.add_student, name='add_student'),
    path('panel/student-list/', views.student_list, name='student_list'),
    path("panel/student/download-all-cards/", views.download_all_cards_page, name="download_all_cards_page"),

    path('panel/student/view/<int:id>/', views.student_view, name='student_view'),
    path('panel/student/edit/<int:id>/', views.student_edit, name='student_edit'),
    
    # admission(New Added in 29 January)
    path("admission/", views.admission_form, name="admission_form"),
    path("create-order/", views.create_order, name="create_order"),



    # admin
    path("admin/students/", views.student_list, name="student_list"),
    path("admin/admission/<int:id>/view/", views.admission_view, name="admission_view"),
    path("admin/admission/<int:id>/approve/", views.admission_approve, name="admission_approve"),
    path("admin/student/<int:id>/delete/", views.student_delete, name="student_delete"),


    # =====================================================
    # STUDENT PANEL
    # =====================================================
    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/logout/', views.student_logout, name='student_logout'),
    #New Hai
    path("student/forgot/", views.student_forgot, name="student_forgot"),



    # =====================================================
    # QUESTION MANAGEMENT
    # =====================================================
    path('panel/add-question/', add_question_wizard, name='add_question'),
    path('panel/question-list/', views.subject_list, name='subject_list'),
    path('panel/chapters/<int:subject_id>/', views.chapter_list, name='chapter_list'),

    path('panel/chapter/<int:chapter_id>/view/', views.view_chapter, name='view_chapter'),
    path('panel/chapter/<int:chapter_id>/edit/', views.edit_chapter, name='edit_chapter'),
    path('panel/chapter/<int:chapter_id>/delete/', views.delete_chapter, name='delete_chapter'),


    # =====================================================
    # EXAM MANAGEMENT
    # =====================================================
    path('panel/add-exam/', views.add_exam, name='add_exam'),
    path('panel/exam/<int:exam_id>/targets/', views.set_targets, name='set_targets'),
    path(
        'panel/exam/<int:exam_id>/select/<int:subject_id>/',
        views.select_subject_questions,
        name='select_subject_questions'
    ),

    path('panel/exams/', views.exam_list, name='exam_list'),
    path('panel/exam/<int:exam_id>/view/', views.exam_view, name='exam_view'),
    path('panel/exam/<int:exam_id>/edit/', views.exam_edit, name='exam_edit'),
    path('panel/exam/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),


    # =====================================================
    # FREE TEST - STUDENT
    # =====================================================
    path('free-test/', views.free_test_buttons, name='free_test_buttons'),
    path('free-test/<str:btn>/instructions/', views.free_test_instructions, name='free_test_instructions'),
    path('free-test/<int:attempt_id>/start/', views.start_free_test, name='start_free_test'),
    path('free-test/<int:attempt_id>/submit/', views.submit_free_test, name='submit_free_test'),
    path('free-test/<int:attempt_id>/analyze/', views.analyze_free_test, name='analyze_free_test'),


    # =====================================================
    # FREE TEST - ADMIN
    # =====================================================
    path('panel/free-test/', views.admin_free_test_buttons, name='admin_free_test_buttons'),
    path(
        'panel/free-test/<str:btn>/assign/',
        views.assign_exam_to_button,
        name='assign_exam_to_button'
    ),
#see Participaint=================================
    path(
        "admin/free-test-participants/",
        views.free_test_participants,
        name="free_test_participants"
    ),


    path(
    "admin/referrals/<str:referral_code>/",
    views.view_referral_students,
    name="view_referral_students"
),


    path("free-test/login/", views.free_test_login, name="free_test_login"),
    path("free-test/dashboard/", views.free_test_dashboard, name="free_test_dashboard"),
    path("free-test/logout/", views.free_test_logout, name="free_test_logout"),

#================================Kali Update Haba -================================================
#Student Exam=========================
    path("admin/exam-task/", views.exam_task_create, name="exam_task_create"),
    path("admin/exam-task/list/", views.exam_task_list, name="exam_task_list"),
    

    path(
        "panel/exam-task/toggle/<int:task_id>/",
        views.toggle_exam_task_status,
        name="toggle_exam_task_status"
    ),

    path(
        "panel/exam-task/delete/<int:task_id>/",
        views.delete_exam_task,
        name="delete_exam_task"
    ),

    path(
        "panel/exam-task/<int:task_id>/students/",
        views.exam_task_students,
        name="exam_task_students"
    ),
    path(
        "panel/student-attempt-result/<int:attempt_id>/",
        views.admin_student_attempt_result,
        name="admin_student_attempt_result"
    ),


    #Student Page=====================
    path("student/my-task/", views.student_my_tasks, name="student_my_tasks"),

    
    path(
    "instructions/<int:attempt_id>/",
    views.exam_instructions,
    name="exam_instructions"
),

    path(
    "start-exam/<int:exam_id>/<int:task_id>/",
    views.start_exam,
    name="start_exam"
),
    path("exam/<int:attempt_id>/", views.exam_screen, name="exam_screen"),

    # 🔥 AJAX (CBT)
    path("save-answer/", views.save_answer, name="save_answer"),
    path("mark-visited/", views.mark_visited, name="mark_visited"),  # ✅ ADD THIS

    path("submit-exam/<int:attempt_id>/", views.submit_exam, name="submit_exam"),
    path("result/<int:attempt_id>/", views.exam_result, name="exam_result"),



    path(
    "student/exam-task-list/",
    views.student_exam_task_list,
    name="student_exam_task_list"
),   



    path(
        "student/exam-result/<int:attempt_id>/",
        views.student_exam_result,
        name="student_exam_result"
    ),
#====================================== Uper Kali Update Haba =================================================

#Student see his/her I Card ==========================
    path(
        "student/id-card/",
        views.student_id_card,
        name="student_id_card"
    ),
#=============Create Center Admin===============================
    # ---------------- CENTER MANAGEMENT ----------------
    path("panel/add-center/", views.add_center, name="add_center"),
    path("panel/center-list/", views.center_list, name="center_list"),

    path("panel/center/view/<int:id>/", views.center_view, name="center_view"),
    path("panel/center/edit/<int:id>/", views.center_edit, name="center_edit"),
    path("panel/center/delete/<int:id>/", views.center_delete, name="center_delete"),

# =======================
# CENTER LOGIN / DASHBOARD
# =======================
    path("center/login/", views.center_login, name="center_login"),
    path("center/dashboard/", views.center_dashboard, name="center_dashboard"),
    path("center/logout/", views.center_logout, name="center_logout"),


# =======================
# CENTER STUDENT PANEL
# =======================
    path("center/add-student/", views.center_add_student, name="center_add_student"),
    path("center/student-list/", views.center_student_list, name="center_student_list"),

    path("center/student/view/<int:id>/", views.center_student_view, name="center_student_view"),
    path("center/student/edit/<int:id>/", views.center_student_edit, name="center_student_edit"),
    path("center/student/delete/<int:id>/", views.center_student_delete, name="center_student_delete"),

    
    # =====================================================
    # DJANGO DEFAULT ADMIN (SHIFTED)
    # =====================================================
    path('django-admin/', admin.site.urls),
]


# =====================================================
# MEDIA FILES
# =====================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
