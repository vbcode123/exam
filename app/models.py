from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# ---------------------- STUDENT ----------------------
from django.db import models
from django.utils import timezone


class Student(models.Model):

    # BASIC DETAILS
    name = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=15,
        unique=True
    )

    email = models.EmailField(
        unique=True,
        blank=True,
        null=True
    )

    photo = models.ImageField(
        upload_to="students/",
        blank=True,
        null=True
    )

    # OPTIONAL DETAILS
    course = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    center_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    # PASSWORD (hash store karo views me)
    password = models.CharField(max_length=128)

    # 🔥 Razorpay fields
    razorpay_order_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        unique=True
    )

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending"
    )

    # ADMISSION APPROVAL
    is_approved = models.BooleanField(default=False)

    # TIME
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.phone})"



# ---------------------- QUESTIONS ----------------------
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    class Meta:
        unique_together = ('subject', 'name')

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class QuestionBank(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)

    question = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    CORRECT_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )
    correct_answer = models.CharField(max_length=1, choices=CORRECT_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]
    


    
# 🔥 EXAM MODELS
class Exam(models.Model):
    name = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField()
    marks_per_question = models.FloatField()
    negative_marking = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    

    def __str__(self):
        return self.name


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)



#free test
class FreeTestButton(models.Model):
    name = models.CharField(max_length=1)  # A, B, C, D, E
    exam = models.ForeignKey(
        Exam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class FreeTestAttempt(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    button = models.ForeignKey(FreeTestButton, on_delete=models.CASCADE)

    # 🔽 NEW FIELDS
    candidate_name = models.CharField(max_length=100, blank=True)
    candidate_phone = models.CharField(max_length=15, blank=True)
    candidate_address = models.TextField(blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.exam.name} - {self.candidate_name or 'Not Filled'}"


class FreeTestAnswer(models.Model):
    attempt = models.ForeignKey(FreeTestAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(
        max_length=1,
        choices=[('A','A'),('B','B'),('C','C'),('D','D')],
        null=True,
        blank=True
    )



#Referal =============
from django.db import models

# =========================
# REFERRAL CODE (1 PHONE = 1 CODE)
# =========================
class ReferralCode(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    code = models.CharField(max_length=6, unique=True)  # VB1234
    discount_unlocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


# =========================
# REFERRAL USAGE (WHO USED)
# =========================
class ReferralUsage(models.Model):
    referral_code = models.ForeignKey(
        ReferralCode,
        on_delete=models.CASCADE,
        related_name="usages"
    )
    referred_phone = models.CharField(max_length=15, unique=True)
    attempt = models.ForeignKey(
        "FreeTestAttempt",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referral_code.code} → {self.referred_phone}"



#===================================Kali Update Haba ============================================================================
#For Student=======================

# FOR STUDENT EXAM

# models.py

class ExamTask(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    task_name = models.CharField(max_length=200)

    # 🔥 ADMIN WILL SET THIS
    created_at = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.task_name} - {self.exam.name}"


# ================= STUDENT CBT ATTEMPT =================
from django.db import models
from django.utils import timezone


# =====================================================
# STUDENT EXAM ATTEMPT (CBT TIMER + SUBMIT LOCK)
# =====================================================
from django.db import models
from django.utils import timezone

class StudentExamAttempt(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    # ✅ NEW FIELD (migration safe)
    task = models.ForeignKey(
        ExamTask,
        on_delete=models.CASCADE,
        null=True,        # IMPORTANT: migration error avoid
        blank=True
    )

    # ⏱ CBT TIMER (ONLY START TIME)
    start_time = models.DateTimeField(null=True, blank=True)

    # 🔒 FINAL SUBMIT
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.task:
            return f"{self.student.name} - {self.exam.name} - Task {self.task.id}"
        return f"{self.student.name} - {self.exam.name}"

    # ---------------- CBT HELPERS ----------------

    def start_exam(self):
        """Exam start sirf ek baar"""
        if not self.start_time:
            self.start_time = timezone.now()
            self.save(update_fields=["start_time"])

    @property
    def remaining_seconds(self):
        """
        🔥 CBT STANDARD TIMER
        Refresh / Resume safe
        """
        if self.is_submitted:
            return 0

        if not self.start_time:
            return self.exam.duration_minutes * 60

        elapsed = (timezone.now() - self.start_time).total_seconds()
        remaining = (self.exam.duration_minutes * 60) - elapsed

        return max(0, int(remaining))

    def submit_exam(self):
        """Final submit lock"""
        if not self.is_submitted:
            self.is_submitted = True
            self.submitted_at = timezone.now()
            self.save(update_fields=["is_submitted", "submitted_at"])

# =====================================================
# STUDENT CBT ANSWER (NO TIMER, NO AUTO DATE)
# =====================================================
class StudentExamAnswer(models.Model):
    attempt = models.ForeignKey(
        StudentExamAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    exam_question = models.ForeignKey(
        ExamQuestion,
        on_delete=models.CASCADE
    )

    selected_option = models.CharField(
        max_length=1,
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ],
        null=True,
        blank=True
    )

    # 🧠 CBT STATES
    is_marked_review = models.BooleanField(default=False)
    is_visited = models.BooleanField(default=False)

    class Meta:
        unique_together = ("attempt", "exam_question")

    def __str__(self):
        return f"{self.attempt} - Q{self.exam_question.id}"

    # 🎨 CBT PALETTE LOGIC
    def palette_state(self):
        if self.selected_option and self.is_marked_review:
            return "answered-marked"   # 🟠
        elif self.selected_option:
            return "answered"          # 🟢
        elif self.is_marked_review:
            return "marked"            # 🟣
        elif self.is_visited:
            return "visited"           # 🔵
        return "not-visited"           # ⚪



#==================================Kali Updated Haba ==================================================================



# ===========================
# CENTER ADMIN / CENTER MODEL
# ===========================
class Center(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
