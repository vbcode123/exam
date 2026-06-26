from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import FileSystemStorage
from app.models import Student
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student
from django.contrib.admin.views.decorators import staff_member_required


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import (
    Student, Subject, Chapter, QuestionBank,
    Exam, ExamQuestion,
    FreeTestButton, FreeTestAttempt, FreeTestAnswer
)

# =======================
# HOME
# =======================
def home(request):
    return render(request, "home.html")


# =======================
# ADMIN AUTH
# =======================
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )
            if user and user.is_staff:
                login(request, user)
                return redirect("admin_dashboard")
            else:
                return render(request, "admin/login.html", {"error": "Invalid credentials"})
        except User.DoesNotExist:
            return render(request, "admin/login.html", {"error": "Email not found"})

    return render(request, "admin/login.html")


@staff_member_required(login_url="/panel/login/")
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")


def admin_logout(request):
    logout(request)
    return redirect("admin_login")

#NEW VIEW ADDED 29 JANUARY==========================================================================================================
# ADMISSION FORM (PUBLIC)
# -------------------------
import json
import razorpay

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


from .models import Student


# -------------------------
# Admission Form View
# -------------------------
import json
import razorpay

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


# -------------------------
# Admission Form
# -------------------------
def admission_form(request):

    if request.method == "POST":

        student = Student.objects.create(
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            course=request.POST.get("course"),
            center_name=request.POST.get("center_name"),
            address=request.POST.get("address"),

            # ✅ plain password
            password=request.POST.get("password"),

            photo=request.FILES.get("photo"),
            payment_status="pending",
            is_approved=False
        )

        return render(request, "admission/success.html")

    return render(request, "admission/form.html")

# -------------------------
# Create Razorpay Order
# -------------------------
def create_order(request):

    client = razorpay.Client(auth=(
        settings.RAZORPAY_API_KEY,
        settings.RAZORPAY_API_SECRET
    ))

    order = client.order.create({
        "amount": 1 * 100,
        "currency": "INR"
    })

    return JsonResponse(order)


# =======================
# STUDENT MANAGEMENT
# =======================
@staff_member_required(login_url="/panel/login/")
def add_student(request):
    if request.method == "POST":
        Student.objects.create(
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            course=request.POST.get("course"),   # ✅ ADDED
            center_name=request.POST.get("center"),
            address=request.POST.get("address"),
            password=request.POST.get("password"),
            photo=request.FILES.get("photo")
        )
        messages.success(request, "Student added successfully")
        return redirect("student_list")

    return render(request, "admin/student_add.html")


@staff_member_required(login_url="/panel/login/")
def student_list(request):
    students = Student.objects.all()
    return render(request, "admin/student_list.html", {"students": students})


from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Student

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Q

@staff_member_required(login_url="/panel/login/")
def download_all_cards_page(request):
    search_query = request.GET.get("search", "").strip()

    students = Student.objects.all()

    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(center_name__icontains=search_query)
        )

    # ✅ Company Details (Back side fix)
    
    company_address = "IIT Bhubaneswar Research and Entrepreneurship Park, Bhubaneswar, Odisha 751013."
    company_phone = "9692 88 9692"
    company_email = "support@vidyabhaban.com"

    return render(request, "admin/download_all_cards.html", {
        "students": students,
        "search_query": search_query,

        # ✅ THESE ARE IMPORTANT
        
        "company_address": company_address,
        "company_phone": company_phone,
        "company_email": company_email,
    })




@staff_member_required(login_url="/panel/login/")
def student_view(request, id):
    student = get_object_or_404(Student, id=id)
    return render(request, "admin/student_view.html", {
        "student": student
    })

@staff_member_required(login_url="/panel/login/")
def admission_view(request, id):
    student = get_object_or_404(Student, id=id)
    return render(request, "admin/admission_view.html", {
        "student": student
    })

# -------------------------
# ADMIN : APPROVE ADMISSION
# -------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
import requests


# ==========================================
# SEND WHATSAPP MESSAGE
# ==========================================
def send_whatsapp(phone, message):
    url = "https://wchat.online/api/send"

    payload = {
        "number": f"91{phone}",
        "type": "text",
        "message": message,
        "instance_id": "6A32A3AF4A0A2",
        "access_token": "692fbc0826bbd"
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=20
        )
        print("WhatsApp Response:", response.text)

    except Exception as e:
        print("WhatsApp Error:", e)


# ==========================================
# APPROVE ADMISSION
# ==========================================
@staff_member_required(login_url="/panel/login/")
def admission_approve(request, id):

    student = get_object_or_404(
        Student,
        id=id,
        is_approved=False
    )

    # ✅ Approve Student
    student.is_approved = True
    student.save()

    # ==========================================
    # EMAIL
    # ==========================================
    if student.email:
        send_mail(
            subject="Admission Approved – Login Details",
            message=f"""
Hello {student.name},

Your admission has been approved successfully.

Login Details

Phone Number: {student.phone}

Password: {student.password}

Login Link

https://vidyabhaban.in/exam/student/login/

Regards,
Vidyabhaban Team
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[student.email],
            fail_silently=True
        )

    # ==========================================
    # WHATSAPP
    # ==========================================
    whatsapp_message = f"""
🎉 Hello {student.name},

Your admission has been approved successfully. ✅

━━━━━━━━━━━━━━━━━━

📱 Phone:
{student.phone}

🔑 Password:
{student.password}

━━━━━━━━━━━━━━━━━━

🔗 Login Here

https://vidyabhaban.in/exam/student/login/

Regards,
Vidyabhaban Team
"""

    send_whatsapp(student.phone, whatsapp_message)

    return redirect("student_list")

@staff_member_required(login_url="/panel/login/")
def student_edit(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == "POST":

        # Basic info
        student.name = request.POST.get("name")
        student.phone = request.POST.get("phone")
        student.course = request.POST.get("course")
        student.center_name = request.POST.get("center")
        student.address = request.POST.get("address")

        # Email (only update if provided)
        email = request.POST.get("email")
        if email:
            student.email = email

        # Photo (optional)
        if request.FILES.get("photo"):
            student.photo = request.FILES.get("photo")

        # Password (optional)
        pwd = request.POST.get("password")
        if pwd:
            student.password = pwd

        student.save()
        return redirect("student_list")

    return render(request, "admin/student_edit.html", {
        "student": student
    })

@staff_member_required(login_url="/panel/login/")
def student_delete(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect("student_list")


# =======================
# STUDENT AUTH (CHANGE)
# =======================
def student_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        student = Student.objects.filter(
            phone=phone,
            password=password,
            is_approved=True
        ).first()

        if student:
            request.session["student_id"] = student.id
            return redirect("student_dashboard")

        return render(request, "student/login.html", {
            "error": "Invalid credentials or admission not approved"
        })

    return render(request, "student/login.html")


def student_dashboard(request):
    if "student_id" not in request.session:
        return redirect("student_login")

    student = Student.objects.get(id=request.session["student_id"])
    return render(request, "student/dashboard.html", {"student": student})



def student_logout(request):
    request.session.flush()
    return redirect("student_login")

#New====================
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from .models import Student


def student_forgot(request):
    msg = None

    if request.method == "POST":
        email = request.POST.get("email").strip()

        try:
            student = Student.objects.get(email=email, is_approved=True)
        except Student.DoesNotExist:
            student = None

        if student:

            password = student.password

            # 🔥 AUTO FIX hashed passwords
            if password.startswith("pbkdf2"):
                password = "123456"
                student.password = password
                student.save()

            send_mail(
                subject="Student Login Details",
                message=f"""
Hello {student.name},

Here are your login details:

Phone Number: {student.phone}
Password: {password}

Login Link:
https://vidyabhaban.in/exam/student/login/

Regards,
Vidyabhaban Admin Team
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[student.email],
                fail_silently=False
            )

            msg = "Login details sent to your email ✅"

        else:
            msg = "Email not found or not approved ❌"

    return render(request, "student_forgot.html", {"msg": msg})

#=============================Kali Sabu Updated haba========================================================
# =======================
# QUESTION WIZARD
# =======================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Subject, Chapter, QuestionBank


# 🔒 Unicode + HTML safe cleaner
def clean_html(text):
    if not text:
        return ""
    return (
        text.replace("‘", "'")
            .replace("’", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace("–", "-")
            .replace("—", "-")
    )


@staff_member_required(login_url="/panel/login/")
def add_question_wizard(request):

    # STEP 1: Subject & Chapter set nahi hua
    if not request.session.get("subject_chapter_set"):
        if request.method == "POST":
            subject = request.POST.get("subject", "").strip()
            chapter = request.POST.get("chapter", "").strip()

            if not subject or not chapter:
                messages.error(request, "Subject & Chapter required")
                return redirect("add_question")

            request.session["subject"] = subject
            request.session["chapter"] = chapter
            request.session["questions"] = []
            request.session["subject_chapter_set"] = True

            return redirect("add_question")

        return render(request, "admin/set_subject_chapter.html")

    # STEP 2: Questions add ho rahe hain
    if request.method == "POST":

        # FINAL SAVE
        if "final_save" in request.POST:
            subject, _ = Subject.objects.get_or_create(
                name=request.session["subject"].title()
            )
            chapter, _ = Chapter.objects.get_or_create(
                subject=subject,
                name=request.session["chapter"].title()
            )

            for q in request.session.get("questions", []):
                QuestionBank.objects.create(
                    chapter=chapter,
                    question=q["question"],
                    option_a=q["option_a"],
                    option_b=q["option_b"],
                    option_c=q["option_c"],
                    option_d=q["option_d"],
                    correct_answer=q["correct_answer"],
                )

            # Session clear
            for k in ["subject", "chapter", "questions", "subject_chapter_set"]:
                request.session.pop(k, None)

            messages.success(request, "Questions saved successfully")
            return redirect("add_question")

        # SINGLE QUESTION ADD
        q = {
            "question": clean_html(request.POST.get("question")),
            "option_a": clean_html(request.POST.get("option_a")),
            "option_b": clean_html(request.POST.get("option_b")),
            "option_c": clean_html(request.POST.get("option_c")),
            "option_d": clean_html(request.POST.get("option_d")),
            "correct_answer": request.POST.get("correct_answer"),
        }

        request.session["questions"].append(q)
        request.session.modified = True

        return redirect("add_question")

    # STEP 3: Page render
    return render(request, "admin/add_question_step.html", {
        "subject": request.session.get("subject"),
        "chapter": request.session.get("chapter"),
        "count": len(request.session.get("questions", [])) + 1,
    })



# =======================
# (बाकी Exam / Free Test views
#  tumhare existing logic ke
#  saath same rahenge)
# =======================

# app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import Subject, Chapter, QuestionBank


# ---------------- SUBJECT LIST ----------------
@staff_member_required(login_url='/admin-login/')
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, "admin/question/subject_list.html", {
        "subjects": subjects
    })


# ---------------- CHAPTER LIST ----------------
@staff_member_required(login_url='/admin-login/')
def chapter_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    chapters = Chapter.objects.filter(subject=subject)
    return render(request, "admin/question/chapter_list.html", {
        "subject": subject,
        "chapters": chapters
    })


# ---------------- VIEW CHAPTER ----------------
@staff_member_required(login_url='/admin-login/')
def view_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    questions = QuestionBank.objects.filter(chapter=chapter)

    return render(request, "admin/question/view_chapter.html", {
        "chapter": chapter,
        "questions": questions
    })


# ---------------- EDIT CHAPTER + QUESTIONS ----------------
@staff_member_required(login_url='/admin-login/')
def edit_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    questions = QuestionBank.objects.filter(chapter=chapter)

    if request.method == "POST":

        # Update chapter name
        chapter.name = clean_html(request.POST.get("chapter_name", chapter.name))
        chapter.save()

        # Update existing questions
        for q in questions:
            q.question = clean_html(request.POST.get(f"question_{q.id}", q.question))
            q.option_a = clean_html(request.POST.get(f"option_a_{q.id}", q.option_a))
            q.option_b = clean_html(request.POST.get(f"option_b_{q.id}", q.option_b))
            q.option_c = clean_html(request.POST.get(f"option_c_{q.id}", q.option_c))
            q.option_d = clean_html(request.POST.get(f"option_d_{q.id}", q.option_d))
            q.correct_answer = request.POST.get(f"correct_{q.id}", q.correct_answer)
            q.save()

        # Add new questions
        new_questions = request.POST.getlist("new_question[]")
        new_option_a = request.POST.getlist("new_option_a[]")
        new_option_b = request.POST.getlist("new_option_b[]")
        new_option_c = request.POST.getlist("new_option_c[]")
        new_option_d = request.POST.getlist("new_option_d[]")
        new_correct = request.POST.getlist("new_correct[]")

        for i, qtext in enumerate(new_questions):
            if qtext.strip():
                QuestionBank.objects.create(
                    chapter=chapter,
                    question=clean_html(qtext),
                    option_a=clean_html(new_option_a[i]),
                    option_b=clean_html(new_option_b[i]),
                    option_c=clean_html(new_option_c[i]),
                    option_d=clean_html(new_option_d[i]),
                    correct_answer=new_correct[i],
                )

        messages.success(request, "Saved successfully")
        return redirect("edit_chapter", chapter_id=chapter.id)

    return render(request, "admin/question/edit_chapter.html", {
        "chapter": chapter,
        "questions": questions
    })



# ---------------- DELETE CHAPTER ----------------
@staff_member_required(login_url='/admin-login/')
def delete_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    subject_id = chapter.subject.id
    chapter.delete()
    messages.success(request, "Chapter & all questions deleted")
    return redirect("chapter_list", subject_id=subject_id)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import *


# ---------------- ADD EXAM ----------------
@staff_member_required(login_url="/admin-login/")
def add_exam(request):
    if request.method == "POST":
        exam = Exam.objects.create(
            name=request.POST["name"],
            duration_minutes=request.POST["duration"],
            marks_per_question=request.POST["marks"],
            negative_marking=request.POST["negative"]
        )
        return redirect("set_targets", exam_id=exam.id)

    return render(request, "admin/exam/add_exam.html")


# ---------------- SET SUBJECT TARGETS ----------------
@staff_member_required(login_url="/admin-login/")
def set_targets(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    subjects = Subject.objects.all()

    if request.method == "POST":
        targets = {}
        for s in subjects:
            count = int(request.POST.get(f"subject_{s.id}", 0))
            if count > 0:
                targets[s.id] = count

        request.session[f"exam_{exam.id}_targets"] = targets

        first_subject_id = list(targets.keys())[0]
        return redirect(
            "select_subject_questions",
            exam_id=exam.id,
            subject_id=first_subject_id
        )

    return render(request, "admin/exam/set_targets.html", {
        "exam": exam,
        "subjects": subjects
    })

# ---------------- SUBJECT-WISE QUESTION SELECTION ----------------
@staff_member_required(login_url="/admin-login/")
def select_subject_questions(request, exam_id, subject_id):
    exam = get_object_or_404(Exam, id=exam_id)
    subject = get_object_or_404(Subject, id=subject_id)

    targets = request.session.get(f"exam_{exam.id}_targets", {})
    target_count = targets.get(str(subject.id)) or targets.get(subject.id)

    questions = QuestionBank.objects.filter(
        chapter__subject=subject
    )

    if request.method == "POST":
        selected_ids = request.POST.getlist("question_ids")

        if len(selected_ids) != target_count:
            messages.error(
                request,
                f"You must select exactly {target_count} questions"
            )
            return redirect(request.path)

        # Save selected questions
        for qid in selected_ids:
            q = QuestionBank.objects.get(id=qid)
            ExamQuestion.objects.create(
                exam=exam,
                question=q,
                subject=subject
            )

        # Move to next subject
        subject_ids = list(map(int, targets.keys()))
        current_index = subject_ids.index(subject.id)

        if current_index + 1 < len(subject_ids):
            next_subject_id = subject_ids[current_index + 1]
            return redirect(
                "select_subject_questions",
                exam_id=exam.id,
                subject_id=next_subject_id
            )

        # ✅ ALL SUBJECTS DONE → EXAM LIST
        messages.success(request, "Exam created successfully")
        del request.session[f"exam_{exam.id}_targets"]

        return redirect("exam_list")   # 👈 यही main change है

    return render(request, "admin/exam/select_questions.html", {
        "exam": exam,
        "subject": subject,
        "questions": questions,
        "target": target_count
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import Exam, ExamQuestion


# ---------------- EXAM LIST ----------------
@staff_member_required(login_url="/admin-login/")
def exam_list(request):
    exams = Exam.objects.all().order_by("-created_at")

    exam_data = []
    for exam in exams:
        total_q = ExamQuestion.objects.filter(exam=exam).count()
        exam_data.append({
            "exam": exam,
            "total_questions": total_q
        })

    return render(request, "admin/exam/exam_list.html", {
        "exam_data": exam_data
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import Exam, ExamQuestion


# ---------------- EXAM VIEW ----------------
@staff_member_required(login_url="/admin-login/")
def exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    questions = (
        ExamQuestion.objects
        .filter(exam=exam)
        .select_related("question", "subject")
    )

    return render(request, "admin/exam/exam_view.html", {
        "exam": exam,
        "questions": questions
    })


# ---------------- EXAM EDIT ----------------
@staff_member_required(login_url="/admin-login/")
def exam_edit(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == "POST":
        exam.name = request.POST.get("name")
        exam.duration_minutes = request.POST.get("duration")
        exam.marks_per_question = request.POST.get("marks")
        exam.negative_marking = request.POST.get("negative")
        exam.save()

        messages.success(request, "Exam updated successfully")
        return redirect("exam_list")

    return render(request, "admin/exam/exam_edit.html", {
        "exam": exam
    })



# ---------------- DELETE EXAM ----------------
@staff_member_required(login_url="/admin-login/")
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam.delete()
    messages.success(request, "Exam deleted successfully")
    return redirect("exam_list")


#free exam hai

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import (
    Exam, ExamQuestion,
    FreeTestButton, FreeTestAttempt, FreeTestAnswer
)

# ================= USER =================

def free_test_buttons(request):
    buttons = FreeTestButton.objects.filter(exam__isnull=False)
    return render(request, "free_test/buttons.html", {
        "buttons": buttons
    })
from django.shortcuts import render, get_object_or_404, redirect
from .models import FreeTestButton, FreeTestAttempt, FreeTestAnswer, ExamQuestion

from django.shortcuts import render, get_object_or_404, redirect
from .models import FreeTestButton, FreeTestAttempt, FreeTestAnswer, ExamQuestion

from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    FreeTestButton,
    FreeTestAttempt,
    FreeTestAnswer,
    ExamQuestion,
)

# ===============================
# 🔐 PHONE VALIDATION (NO OTP)
# ===============================
def is_valid_phone(phone):
    if not phone:
        return False
    if not phone.isdigit() or len(phone) != 10:
        return False
    if phone[0] not in ["6", "7", "8", "9"]:
        return False
    if phone.count(phone[0]) == 10:   # 1111111111, 0000000000
        return False
    return True


def free_test_instructions(request, btn):
    button = get_object_or_404(FreeTestButton, name=btn)
    exam = button.exam

    # ==================================================
    # 🔹 REFERRAL FROM LINK (GET ?ref=VB1234)
    # ==================================================
    ref_from_link = request.GET.get("ref")
    if ref_from_link:
        request.session["ref_code"] = ref_from_link
        request.session.modified = True

    # ==================================================
    # 🔹 FORM SUBMIT
    # ==================================================
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        # 👉 Manual referral (optional)
        manual_ref = request.POST.get("referral_code")

        # 🔐 Phone validation
        if not is_valid_phone(phone):
            return render(request, "free_test/instructions.html", {
                "exam": exam,
                "error": "Please enter a valid mobile number"
            })

        # ==================================================
        # 🔹 SAVE MANUAL REFERRAL IF GIVEN
        # ==================================================
        if manual_ref:
            request.session["ref_code"] = manual_ref.strip().upper()
            request.session.modified = True

        # ==================================================
        # 🔹 CREATE ATTEMPT (MULTIPLE ATTEMPTS ALLOWED)
        # ==================================================
        attempt = FreeTestAttempt.objects.create(
            exam=exam,
            button=button,
            candidate_name=name,
            candidate_phone=phone,
            candidate_address=address,
        )

        # Create empty answers
        for q in ExamQuestion.objects.filter(exam=exam):
            FreeTestAnswer.objects.create(
                attempt=attempt,
                question=q
            )

        return redirect("start_free_test", attempt.id)

    # ==================================================
    # 🔹 SHOW INSTRUCTION PAGE
    # ==================================================
    return render(request, "free_test/instructions.html", {
        "exam": exam
    })





def start_free_test(request, attempt_id):
    attempt = get_object_or_404(FreeTestAttempt, id=attempt_id)
    questions = ExamQuestion.objects.filter(exam=attempt.exam)

    return render(request, "free_test/exam.html", {
        "attempt": attempt,
        "questions": questions
    })


def submit_free_test(request, attempt_id):
    attempt = get_object_or_404(FreeTestAttempt, id=attempt_id)

    for key, val in request.POST.items():
        if key.startswith("q_"):
            qid = key.split("_")[1]
            ans = FreeTestAnswer.objects.get(
                attempt=attempt,
                question_id=qid
            )
            ans.selected_option = val
            ans.save()

    attempt.submitted_at = timezone.now()
    attempt.save()

    return redirect("analyze_free_test", attempt_id=attempt.id)
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, get_object_or_404
from .models import FreeTestAttempt, FreeTestAnswer
from django.shortcuts import render, get_object_or_404
from .models import FreeTestAttempt, FreeTestAnswer
import random
from django.shortcuts import render, get_object_or_404
from .models import (
    FreeTestAttempt,
    FreeTestAnswer,
    ReferralCode,
    ReferralUsage,
)

def analyze_free_test(request, attempt_id):
    attempt = get_object_or_404(FreeTestAttempt, id=attempt_id)

    answers = FreeTestAnswer.objects.filter(
        attempt=attempt
    ).select_related(
        "question__question",
        "question__subject"
    )

    section = {}

    total_questions = answers.count()
    total_correct = 0
    total_wrong = 0
    total_unattempted = 0

    marks_per_q = float(attempt.exam.marks_per_question)
    negative_per_q = abs(float(attempt.exam.negative_marking))

    # ================= QUESTION ANALYSIS =================
    for ans in answers:
        subject_name = ans.question.subject.name
        question_obj = ans.question.question
        correct_option = question_obj.correct_answer

        if ans.selected_option is None:
            status = "unattempted"
            total_unattempted += 1
        elif ans.selected_option == correct_option:
            status = "correct"
            total_correct += 1
        else:
            status = "wrong"
            total_wrong += 1

        if subject_name not in section:
            section[subject_name] = {
                "total": 0,
                "correct": 0,
                "wrong": 0,
                "unattempted": 0,
                "questions": []
            }

        section[subject_name]["total"] += 1

        if status == "correct":
            section[subject_name]["correct"] += 1
        elif status == "wrong":
            section[subject_name]["wrong"] += 1
        else:
            section[subject_name]["unattempted"] += 1

        section[subject_name]["questions"].append({
            "q": question_obj.question,
            "opt_a": question_obj.option_a,
            "opt_b": question_obj.option_b,
            "opt_c": question_obj.option_c,
            "opt_d": question_obj.option_d,
            "your": ans.selected_option,
            "correct": correct_option,
            "status": status,
        })

    # ================= FINAL MARKS =================
    correct_marks = total_correct * marks_per_q
    negative_marks = total_wrong * negative_per_q
    obtained_marks = correct_marks - negative_marks
    total_marks = total_questions * marks_per_q

    # ================= SUBJECT WISE GRADE =================
    for sub in section.values():
        sub["marks_obtained"] = (
            sub["correct"] * marks_per_q
            - sub["wrong"] * negative_per_q
        )
        sub["total_marks"] = sub["total"] * marks_per_q

        if sub["total_marks"] > 0:
            marks_percentage = (sub["marks_obtained"] / sub["total_marks"]) * 100
            if marks_percentage < 40:
                sub["grade"] = "POOR"
            elif marks_percentage < 70:
                sub["grade"] = "AVERAGE"
            else:
                sub["grade"] = "GOOD"
        else:
            sub["grade"] = "POOR"

    # ==================================================
    # 🔥 REFERRAL LOGIC (ONLY FIXED PART)
    # ==================================================
    referral = None
    referral_count = 0
    discount_unlocked = False

    if attempt.candidate_phone:
        # 1️⃣ GET / CREATE OWN REFERRAL CODE
        referral = ReferralCode.objects.filter(
            phone=attempt.candidate_phone
        ).first()

        if not referral:
            while True:
                code = f"VB{random.randint(1000, 9999)}"
                if not ReferralCode.objects.filter(code=code).exists():
                    break

            referral = ReferralCode.objects.create(
                phone=attempt.candidate_phone,
                code=code
            )

        referral_count = referral.usages.count()
        discount_unlocked = referral.discount_unlocked

        # 2️⃣ COUNT REFERRAL (STRICT RULE)
        ref_code = request.session.get("ref_code")

        if ref_code:
            ref_obj = ReferralCode.objects.filter(code=ref_code).first()

            # ❌ SELF REFERRAL BLOCK
            if ref_obj and ref_obj.phone != attempt.candidate_phone:

                # 🔒 ONE PHONE → ONLY ONE REFERRAL (GLOBAL)
                already_referred = ReferralUsage.objects.filter(
                    referred_phone=attempt.candidate_phone
                ).exists()

                if not already_referred:
                    ReferralUsage.objects.create(
                        referral_code=ref_obj,
                        referred_phone=attempt.candidate_phone,
                        attempt=attempt
                    )

                    # 🔓 Unlock discount safely
                    if ref_obj.usages.count() >= 5 and not ref_obj.discount_unlocked:
                        ref_obj.discount_unlocked = True
                        ref_obj.save()

    # ================= CONTEXT =================
    context = {
        "attempt": attempt,
        "section": section,
        "total_questions": total_questions,
        "total_correct": total_correct,
        "total_wrong": total_wrong,
        "total_unattempted": total_unattempted,
        "total_marks": total_marks,
        "obtained_marks": obtained_marks,
        "correct_marks": correct_marks,
        "negative_marks": negative_marks,

        # 🔥 REFERRAL DATA
        "referral_code": referral.code if referral else None,
        "referral_count": referral_count,
        "discount": discount_unlocked,
    }

    return render(request, "free_test/analyze.html", context)

# ================= ADMIN =================

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Exam, FreeTestButton


@staff_member_required(login_url="/admin-login/")
def admin_free_test_buttons(request):
    """
    Admin can assign exams to Free Test buttons A–E
    All logic handled on single page
    """

    # ensure buttons exist
    for name in ["A", "B", "C", "D", "E"]:
        FreeTestButton.objects.get_or_create(name=name)

    buttons = FreeTestButton.objects.select_related("exam").all()
    exams = Exam.objects.all()

    if request.method == "POST":
        # POST data format: button_A = exam_id
        for b in buttons:
            exam_id = request.POST.get(f"button_{b.name}")
            if exam_id:
                b.exam_id = exam_id
                b.save()

        return redirect("admin_free_test_buttons")

    return render(request, "admin/free_test/button_assign.html", {
        "buttons": buttons,
        "exams": exams
    })



@staff_member_required(login_url="/admin-login/")
def assign_exam_to_button(request, btn):
    button = get_object_or_404(FreeTestButton, name=btn)
    exams = Exam.objects.all()

    if request.method == "POST":
        button.exam_id = request.POST.get("exam")
        button.save()
        return redirect("admin_free_test_buttons")

    return render(request, "admin/free_test/assign_exam.html", {
        "button": button,
        "exams": exams
    })





from django.shortcuts import render
from .models import FreeTestAttempt, ReferralCode

def free_test_participants(request):
    participants = FreeTestAttempt.objects.select_related(
        "exam", "button"
    ).order_by("-started_at")

    # 🔥 attach referral_code to each participant
    for p in participants:
        ref = ReferralCode.objects.filter(
            phone=p.candidate_phone
        ).first()

        # dynamic attribute (model change nahi)
        p.referral_code = ref.code if ref else None

    return render(
        request,
        "admin/free_test_participants.html",
        {
            "participants": participants
        }
    )

from django.shortcuts import render, get_object_or_404
from .models import ReferralCode, ReferralUsage

from django.shortcuts import render, get_object_or_404
from .models import ReferralCode, ReferralUsage

def view_referral_students(request, referral_code):
    referral = get_object_or_404(ReferralCode, code=referral_code)

    usages = ReferralUsage.objects.select_related(
        "attempt__exam"
    ).filter(referral_code=referral)

    total_referrals = usages.count()
    remaining = max(0, 5 - total_referrals)

    return render(
        request,
        "admin/referral_students.html",
        {
            "referral": referral,
            "usages": usages,
            "total_referrals": total_referrals,
            "remaining": remaining,
        }
    )

#Free test dashboard ==============
from django.shortcuts import render, redirect
from .models import ReferralCode


# ---------------------------
# FREE TEST LOGIN
# ---------------------------
def free_test_login(request):
    error = None

    if request.method == "POST":
        phone = request.POST.get("phone")
        code = request.POST.get("code")

        if not phone or not code:
            error = "Both fields required"
        else:
            valid = ReferralCode.objects.filter(
                phone=phone,
                code=code
            ).exists()

            if not valid:
                error = "Invalid phone or referral code"
            else:
                request.session["ref_phone"] = phone
                request.session["ref_code"] = code
                return redirect("free_test_dashboard")

    return render(request, "free_test/login.html", {"error": error})


# ---------------------------
# FREE TEST DASHBOARD
# ---------------------------
from django.shortcuts import render, redirect
from .models import ReferralCode, ReferralUsage

def free_test_dashboard(request):
    phone = request.session.get("ref_phone")
    code = request.session.get("ref_code")

    if not phone or not code:
        return redirect("free_test_login")

    # 🔐 SECURITY CHECK
    try:
        referral = ReferralCode.objects.get(phone=phone, code=code)
    except ReferralCode.DoesNotExist:
        return redirect("free_test_login")

    # 🔥 ONLY THIS REFERRAL → COMPLETED EXAMS
    referral_usages = ReferralUsage.objects.filter(
        referral_code=referral,
        attempt__submitted_at__isnull=False
    ).select_related("attempt").order_by("-attempt__submitted_at")

    total_completed = referral_usages.count()

    return render(request, "free_test/dashboard.html", {
        "total_completed": total_completed,
        "referral_usages": referral_usages,
        "my_referral_code": referral.code
    })


# ---------------------------
# FREE TEST LOGOUT
# ---------------------------
def free_test_logout(request):
    request.session.flush()
    return redirect("free_test_login")

#==========================  Update kali Haba ===============================================================================
#for Student====================
# views.py

from django.utils.dateparse import parse_datetime

@staff_member_required(login_url="/admin-login/")
def exam_task_create(request):
    exams = Exam.objects.all()

    if request.method == "POST":
        exam_id = request.POST.get("exam")
        task_name = request.POST.get("task_name")
        created_at = request.POST.get("created_at")

        exam = get_object_or_404(Exam, id=exam_id)

        ExamTask.objects.create(
            exam=exam,
            task_name=task_name,
            created_at=parse_datetime(created_at)
        )

        return redirect("exam_task_list")

    return render(request, "admin/exam_task/create.html", {
        "exams": exams
    })



@staff_member_required(login_url="/admin-login/")
def exam_task_list(request):
    tasks = ExamTask.objects.select_related("exam").order_by("-created_at")
    return render(request, "admin/exam_task/list.html", {
        "tasks": tasks
    })

@staff_member_required(login_url="/admin-login/")
def toggle_exam_task_status(request, task_id):
    task = get_object_or_404(ExamTask, id=task_id)
    task.is_active = not task.is_active
    task.save()
    return redirect("exam_task_list")

@staff_member_required(login_url="/admin-login/")
def delete_exam_task(request, task_id):
    task = get_object_or_404(ExamTask, id=task_id)
    task.delete()
    return redirect("exam_task_list")

@staff_member_required(login_url="/admin-login/")
def exam_task_students(request, task_id):
    task = get_object_or_404(ExamTask, id=task_id)

    attempts = (
        StudentExamAttempt.objects
        .filter(task=task, is_submitted=True)
        .select_related("student", "exam")
        .order_by("-submitted_at")
    )

    student_data = []

    # 🔥 FULL MARKS
    total_questions = ExamQuestion.objects.filter(exam=task.exam).count()
    marks_per_q = float(task.exam.marks_per_question)
    full_marks = total_questions * marks_per_q

    for attempt in attempts:
        answers = StudentExamAnswer.objects.filter(attempt=attempt)

        negative = abs(float(task.exam.negative_marking))
        obtained = 0.0

        for ans in answers:
            if not ans.selected_option:
                continue

            if ans.selected_option == ans.exam_question.question.correct_answer:
                obtained += marks_per_q
            else:
                obtained -= negative

        student_data.append({
            "attempt_id": attempt.id,  # ✅ NEW
            "name": attempt.student.name,
            "center": attempt.student.center_name,
            "phone": attempt.student.phone,
            "marks": round(obtained, 2),
            "full_marks": full_marks,
            "submitted_at": attempt.submitted_at,  # ✅ optional
        })

    return render(request, "admin/exam_task/view_students.html", {
        "task": task,
        "students": student_data,
        "full_marks": full_marks,
    })




#STUDENT PAGE======================
# views.py
def student_my_tasks(request):
    if "student_id" not in request.session:
        return redirect("/student/login/")

    student_id = request.session["student_id"]

    tasks = ExamTask.objects.filter(is_active=True).select_related("exam")

    task_data = []

    for task in tasks:
        total_questions = ExamQuestion.objects.filter(
            exam=task.exam
        ).count()

        completed = StudentExamAttempt.objects.filter(
            student_id=student_id,
            exam=task.exam,
            task=task,
            is_submitted=True
        ).exists()

        task_data.append({
            "task": task,
            "exam": task.exam,
            "total_questions": total_questions,
            "duration": task.exam.duration_minutes,
            "completed": completed
        })

    return render(request, "student/my_task.html", {
        "task_data": task_data
    })





from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

from app.models import (
    Student,
    Exam,
    ExamQuestion,
    QuestionBank,
    StudentExamAttempt,
    StudentExamAnswer,
)



# =====================================================
# STUDENT : INSTRUCTIONS PAGE
# =====================================================
from django.shortcuts import render, get_object_or_404, redirect

from django.shortcuts import render, get_object_or_404, redirect

def exam_instructions(request, attempt_id):
    if "student_id" not in request.session:
        return redirect("/student/login/")

    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    exam = attempt.exam

    total_questions = ExamQuestion.objects.filter(
        exam=exam
    ).count()

    context = {
        "attempt": attempt,
        "exam": exam,
        "total_questions": total_questions,
        "marks_per_question": exam.marks_per_question,
        "negative_marking": exam.negative_marking,
        "duration_minutes": exam.duration_minutes,
    }

    return render(request, "student/instructions.html", context)




# =====================================================
# STUDENT : START EXAM
# =====================================================


# =====================================================
# STUDENT : EXAM SCREEN (CBT UI)
# =====================================================
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone




from .models import (
    StudentExamAttempt,
    StudentExamAnswer,
    ExamQuestion,
)

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import StudentExamAttempt, StudentExamAnswer, ExamQuestion


# =====================================================
# 2️⃣ STUDENT : START EXAM (ONLY AFTER TICK)
# =====================================================
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone

from .models import (
    StudentExamAttempt,
    StudentExamAnswer,
    ExamQuestion
)

# =====================================================
# START EXAM (CREATE / RESUME ATTEMPT)
# =====================================================
from django.shortcuts import redirect
from django.utils import timezone

def start_exam(request, exam_id, task_id):
    if "student_id" not in request.session:
        return redirect("/student/login/")

    student_id = request.session["student_id"]

    attempt = StudentExamAttempt.objects.filter(
        student_id=student_id,
        exam_id=exam_id,
        task_id=task_id,
        is_submitted=False
    ).first()

    if not attempt:
        attempt = StudentExamAttempt.objects.create(
            student_id=student_id,
            exam_id=exam_id,
            task_id=task_id
        )

    # ✅ instruction page par redirect (ATTEMPT ID)
    return redirect("exam_instructions", attempt.id)

# =====================================================
# CBT EXAM SCREEN (NTA / SSC STYLE)
# =====================================================
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone

from .models import (
    StudentExamAttempt,
    StudentExamAnswer,
    ExamQuestion
)

# =====================================================
# CBT EXAM SCREEN
# =====================================================
def exam_screen(request, attempt_id):
    # ---------- AUTH ----------
    if "student_id" not in request.session:
        return redirect("/student/login/")

    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)

    # ---------- SECURITY ----------
    if attempt.student.id != request.session["student_id"]:
        return redirect("/student/dashboard/")

    # ---------- ALREADY SUBMITTED ----------
    if attempt.is_submitted:
        return redirect("exam_result", attempt.id)

    # ---------- START EXAM (ONLY ONCE) ----------
    attempt.start_exam()

    # ---------- QUESTIONS ----------
    exam_questions = (
        ExamQuestion.objects
        .filter(exam=attempt.exam)
        .select_related("question", "subject")
        .order_by("id")
    )

    # ---------- PRE-CREATE ANSWERS ----------
    for eq in exam_questions:
        StudentExamAnswer.objects.get_or_create(
            attempt=attempt,
            exam_question=eq
        )

    answers = StudentExamAnswer.objects.filter(attempt=attempt)
    answer_map = {a.exam_question_id: a for a in answers}

    # ---------- SUBJECT WISE DATA ----------
    subjects = {}

    for eq in exam_questions:
        ans = answer_map.get(eq.id)
        subject = eq.subject.name

        subjects.setdefault(subject, []).append({
            "eq_id": eq.id,
            "question": eq.question.question,
            "options": {
                "A": eq.question.option_a,
                "B": eq.question.option_b,
                "C": eq.question.option_c,
                "D": eq.question.option_d,
            },
            "selected": ans.selected_option,
            "visited": ans.is_visited,
            "marked": ans.is_marked_review,
            "palette": ans.palette_state(),
        })

    return render(request, "student/exam.html", {
        "attempt": attempt,
        "subjects_json": json.dumps(subjects),
        "remaining_seconds": attempt.remaining_seconds,
    })


# =====================================================
# AJAX : SAVE / CLEAR / MARK REVIEW
# =====================================================
def save_answer(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=400)

    ans = get_object_or_404(
        StudentExamAnswer,
        attempt_id=request.POST.get("attempt_id"),
        exam_question_id=request.POST.get("exam_question_id")
    )

    # ---------- SECURITY ----------
    if ans.attempt.student.id != request.session.get("student_id"):
        return JsonResponse({"status": "unauthorized"}, status=403)

    # ---------- UPDATE ANSWER ----------
    option = request.POST.get("option")

    ans.selected_option = option if option else None
    ans.is_marked_review = request.POST.get("review") == "1"
    ans.is_visited = True
    ans.save()

    # ---------- SAVE TIMER (RESUME SAFE) ----------
    remaining = request.POST.get("remaining")
    if remaining is not None:
        attempt = ans.attempt
        attempt.remaining_seconds = int(remaining)
        attempt.save(update_fields=["remaining_seconds"])

    return JsonResponse({
        "status": "ok",
        "palette": ans.palette_state()
    })


# =====================================================
# MARK QUESTION AS VISITED (ON OPEN)
# =====================================================
def mark_visited(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=400)

    ans = get_object_or_404(
        StudentExamAnswer,
        attempt_id=request.POST.get("attempt_id"),
        exam_question_id=request.POST.get("exam_question_id")
    )

    if ans.attempt.student.id != request.session.get("student_id"):
        return JsonResponse({"status": "unauthorized"}, status=403)

    if not ans.is_visited:
        ans.is_visited = True
        ans.save(update_fields=["is_visited"])

    return JsonResponse({
        "status": "ok",
        "palette": ans.palette_state()
    })


# =====================================================
# SUBMIT EXAM (FINAL LOCK)
# =====================================================
def submit_exam(request, attempt_id):
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)

    # ---------- SECURITY ----------
    if attempt.student.id != request.session.get("student_id"):
        return redirect("/student/dashboard/")

    # ---------- FINAL SUBMIT ----------
    attempt.submit_exam()

    return redirect("exam_result", attempt.id)















# =====================================================
# STUDENT : RESULT PAGE
# =====================================================
from django.shortcuts import render, get_object_or_404
from .models import StudentExamAttempt, StudentExamAnswer


def exam_result(request, attempt_id):
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)

    answers = (
        StudentExamAnswer.objects
        .filter(attempt=attempt)
        .select_related(
            "exam_question__question",
            "exam_question__subject"
        )
    )

    marks_per_q = float(attempt.exam.marks_per_question)

    # 🔒 FORCE NEGATIVE MARKING AS POSITIVE
    negative = abs(float(attempt.exam.negative_marking))

    total_questions = answers.count()

    final_marks = 0.0
    correct = 0
    wrong = 0
    unattempted = 0

    section_stats = {}

    for ans in answers:
        question = ans.exam_question.question
        subject = ans.exam_question.subject.name

        if subject not in section_stats:
            section_stats[subject] = {
                "total": 0,
                "correct": 0,
                "wrong": 0,
                "unattempted": 0,
                "marks": 0.0,
                "max_marks": 0.0,
                "percentage": 0.0,
            }

        section_stats[subject]["total"] += 1
        section_stats[subject]["max_marks"] += marks_per_q

        # 🟡 NOT ATTEMPTED
        if not ans.selected_option:
            unattempted += 1
            section_stats[subject]["unattempted"] += 1
            continue

        # 🟢 CORRECT → ADD ONLY POSITIVE
        if ans.selected_option == question.correct_answer:
            correct += 1
            section_stats[subject]["correct"] += 1

            final_marks += marks_per_q
            section_stats[subject]["marks"] += marks_per_q

        # 🔴 WRONG → SUBTRACT ONLY (NEVER ADD)
        else:
            wrong += 1
            section_stats[subject]["wrong"] += 1

            final_marks -= negative
            section_stats[subject]["marks"] -= negative

    max_marks = total_questions * marks_per_q

    percentage = round((final_marks / max_marks) * 100, 2) if max_marks > 0 else 0

    for subject, data in section_stats.items():
        if data["max_marks"] > 0:
            data["percentage"] = round(
                (data["marks"] / data["max_marks"]) * 100, 2
            )

    return render(request, "student/result.html", {
        "attempt": attempt,
        "answers": answers,

        # COUNTS
        "total": total_questions,
        "correct": correct,
        "wrong": wrong,
        "unattempted": unattempted,

        # MARKS
        "marks": round(final_marks, 2),
        "max_marks": max_marks,
        "percentage": percentage,

        # SECTION
        "section_stats": section_stats,
    })



def student_exam_task_list(request):
    if "student_id" not in request.session:
        return redirect("/student/login/")

    student_id = request.session["student_id"]

    attempts = (
        StudentExamAttempt.objects
        .filter(student_id=student_id, is_submitted=True)
        .select_related("exam", "task")
        .order_by("-submitted_at")
    )

    result_data = []

    for attempt in attempts:
        answers = StudentExamAnswer.objects.filter(attempt=attempt)

        marks_per_q = float(attempt.exam.marks_per_question)
        negative = abs(float(attempt.exam.negative_marking))

        obtained = 0.0

        for ans in answers:
            if not ans.selected_option:
                continue

            if ans.selected_option == ans.exam_question.question.correct_answer:
                obtained += marks_per_q
            else:
                obtained -= negative

        total_questions = answers.count()
        max_marks = total_questions * marks_per_q
        percentage = round((obtained / max_marks) * 100, 2) if max_marks else 0

        result_data.append({
            "attempt": attempt,
            "exam": attempt.exam,
            "task": attempt.task,

            # 🔥 IMPORTANT DATES
            "assigned_at": attempt.task.created_at,     # ✅ ADMIN DATE
            "submitted_at": attempt.submitted_at,       # ✅ STUDENT DATE

            "obtained": round(obtained, 2),
            "max_marks": max_marks,
            "percentage": percentage,
        })

    return render(request, "student/exam_task_list.html", {
        "result_data": result_data
    })


def student_exam_result(request, attempt_id):
    if "student_id" not in request.session:
        return redirect("/student/login/")

    attempt = get_object_or_404(
        StudentExamAttempt,
        id=attempt_id,
        student_id=request.session["student_id"]
    )

    answers = (
        StudentExamAnswer.objects
        .filter(attempt=attempt)
        .select_related(
            "exam_question__question",
            "exam_question__subject"
        )
        .order_by("id")
    )

    marks_per_q = float(attempt.exam.marks_per_question)
    negative = abs(float(attempt.exam.negative_marking))

    total = answers.count()
    correct = wrong = unattempted = 0
    obtained = 0.0

    question_data = []

    for ans in answers:
        question = ans.exam_question.question
        selected = ans.selected_option
        correct_answer = question.correct_answer

        if not selected:
            status = "unattempted"
            unattempted += 1
        elif selected == correct_answer:
            status = "correct"
            correct += 1
            obtained += marks_per_q
        else:
            status = "wrong"
            wrong += 1
            obtained -= negative

        question_data.append({
            "question": question.question,
            "options": {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d,
            },
            "selected": selected,
            "correct": correct_answer,
            "status": status,
            "subject": ans.exam_question.subject.name,
        })

    max_marks = total * marks_per_q
    percentage = round((obtained / max_marks) * 100, 2) if max_marks else 0

    return render(request, "student/exam_result_view.html", {
        "attempt": attempt,

        # summary
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "unattempted": unattempted,

        # marks
        "obtained": round(obtained, 2),
        "max_marks": max_marks,
        "percentage": percentage,

        # questions
        "questions": question_data,
    })





from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required(login_url="/admin-login/")  
def admin_student_attempt_result(request, attempt_id):

    attempt = get_object_or_404(
        StudentExamAttempt.objects.select_related("student", "exam", "task"),
        id=attempt_id,
        is_submitted=True
    )

    answers = (
        StudentExamAnswer.objects
        .filter(attempt=attempt)
        .select_related("exam_question__question", "exam_question__subject")
        .order_by("id")
    )

    marks_per_q = float(attempt.exam.marks_per_question)
    negative = abs(float(attempt.exam.negative_marking))

    total = answers.count()
    correct = wrong = unattempted = 0
    obtained = 0.0

    question_data = []

    for ans in answers:
        q = ans.exam_question.question
        subject_name = ans.exam_question.subject.name

        selected = ans.selected_option
        correct_ans = q.correct_answer

        if not selected:
            status = "unattempted"
            unattempted += 1
        elif selected == correct_ans:
            status = "correct"
            correct += 1
            obtained += marks_per_q
        else:
            status = "wrong"
            wrong += 1
            obtained -= negative

        question_data.append({
            "subject": subject_name,
            "question": q.question,
            "options": {
                "A": q.option_a,
                "B": q.option_b,
                "C": q.option_c,
                "D": q.option_d,
            },
            "selected": selected,
            "correct": correct_ans,
            "status": status,
        })

    max_marks = total * marks_per_q
    percentage = round((obtained / max_marks) * 100, 2) if max_marks else 0

    return render(request, "admin/exam_task/student_attempt_result.html", {
        "attempt": attempt,
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "unattempted": unattempted,
        "obtained": round(obtained, 2),
        "max_marks": max_marks,
        "percentage": percentage,
        "questions": question_data,
    })

#================================Uper Updated kali Haba =====================================================================
#Student See  His Admit Card=======================
# views.py

def student_id_card(request):
    # 🔐 STUDENT LOGIN CHECK
    if "student_id" not in request.session:
        return redirect("student_login")

    student = get_object_or_404(
        Student,
        id=request.session["student_id"]
    )

    return render(
        request,
        "student/id_card.html",
        {"student": student}
    )


#=============Create Center Admin===============================

# =======================
# CENTER MANAGEMENT
# =======================

@staff_member_required(login_url="/panel/login/")
def add_center(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")

        # ✅ confirm password check
        if password != cpassword:
            messages.error(request, "Passwords do not match!")
            return redirect("add_center")

        # ✅ phone unique check
        if Center.objects.filter(phone=phone).exists():
            messages.error(request, "This phone number is already registered!")
            return redirect("add_center")

        Center.objects.create(
            name=name,
            phone=phone,
            password=password
        )

        messages.success(request, "Center added successfully ✅")
        return redirect("center_list")

    return render(request, "admin/center/add_center.html")


@staff_member_required(login_url="/panel/login/")
def center_list(request):
    centers = Center.objects.all().order_by("-id")
    return render(request, "admin/center/center_list.html", {"centers": centers})


@staff_member_required(login_url="/panel/login/")
def center_view(request, id):
    center = get_object_or_404(Center, id=id)
    return render(request, "admin/center/center_view.html", {"center": center})


@staff_member_required(login_url="/panel/login/")
def center_edit(request, id):
    center = get_object_or_404(Center, id=id)

    if request.method == "POST":
        center.name = request.POST.get("name")
        center.phone = request.POST.get("phone")

        pwd = request.POST.get("password")
        cpwd = request.POST.get("cpassword")

        # ✅ password optional
        if pwd:
            if pwd != cpwd:
                messages.error(request, "Passwords do not match!")
                return redirect("center_edit", id=center.id)
            center.password = pwd

        center.save()
        messages.success(request, "Center updated successfully ✅")
        return redirect("center_list")

    return render(request, "admin/center/center_edit.html", {"center": center})


@staff_member_required(login_url="/panel/login/")
def center_delete(request, id):
    center = get_object_or_404(Center, id=id)
    center.delete()
    messages.success(request, "Center deleted successfully ✅")
    return redirect("center_list")


# =======================
# CENTER LOGIN SYSTEM
# =======================

def center_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        center = Center.objects.filter(phone=phone, password=password).first()

        if center:
            request.session["center_id"] = center.id
            return redirect("center_dashboard")
        else:
            return render(request, "center/login.html", {
                "error": "Invalid phone number or password"
            })

    return render(request, "center/login.html")


def center_dashboard(request):
    if "center_id" not in request.session:
        return redirect("center_login")

    center = Center.objects.get(id=request.session["center_id"])

    return render(request, "center/dashboard.html", {
        "center": center
    })


def center_logout(request):
    request.session.pop("center_id", None)
    return redirect("center_login")


#Center Manage Student =============================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Student, Center


# ✅ Center login protect
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, Center


def center_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if "center_id" not in request.session:
            return redirect("center_login")
        return view_func(request, *args, **kwargs)
    return wrapper


@center_login_required
def center_add_student(request):
    center = Center.objects.get(id=request.session["center_id"])

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        course = request.POST.get("course")
        address = request.POST.get("address")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        photo = request.FILES.get("photo")

        if password != cpassword:
            messages.error(request, "Passwords do not match!")
            return redirect("center_add_student")

        if Student.objects.filter(phone=phone).exists():
            messages.error(request, "This phone number is already registered!")
            return redirect("center_add_student")

        Student.objects.create(
            name=name,
            phone=phone,
            photo=photo,
            course=course,
            center_name=center.name,  # ✅ SAVE CENTER NAME
            address=address,
            password=password
        )

        messages.success(request, "Student added successfully ✅")
        return redirect("center_add_student")

    # ✅ IMPORTANT: center pass to template
    return render(request, "center/student_add.html", {"center": center})


# ✅ STUDENT LIST (ONLY OWN CENTER)
@center_login_required
def center_student_list(request):
    center = Center.objects.get(id=request.session["center_id"])

    students = Student.objects.filter(center_name=center.name).order_by("-id")

    return render(request, "center/student_list.html", {
        "students": students
    })


# ✅ VIEW STUDENT
@center_login_required
def center_student_view(request, id):
    center = Center.objects.get(id=request.session["center_id"])

    student = get_object_or_404(Student, id=id, center_name=center.name)

    return render(request, "center/student_view.html", {
        "student": student
    })


# ✅ EDIT STUDENT
@center_login_required
def center_student_edit(request, id):
    center = Center.objects.get(id=request.session["center_id"])

    student = get_object_or_404(Student, id=id, center_name=center.name)

    if request.method == "POST":
        student.name = request.POST.get("name")
        student.phone = request.POST.get("phone")
        student.course = request.POST.get("course")
        student.address = request.POST.get("address")

        if request.FILES.get("photo"):
            student.photo = request.FILES.get("photo")

        pwd = request.POST.get("password")
        cpwd = request.POST.get("cpassword")

        if pwd:
            if pwd != cpwd:
                messages.error(request, "Passwords do not match!")
                return redirect("center_student_edit", id=student.id)
            student.password = pwd

        student.save()
        messages.success(request, "Student updated successfully ✅")
        return redirect("center_student_list")

    return render(request, "center/student_edit.html", {
        "student": student
    })


# ✅ DELETE STUDENT
@center_login_required
def center_student_delete(request, id):
    center = Center.objects.get(id=request.session["center_id"])

    student = get_object_or_404(Student, id=id, center_name=center.name)
    student.delete()

    messages.success(request, "Student deleted successfully ✅")
    return redirect("center_student_list")
