# models.py

from django.db import models

# 1. 반 정보 테이블
class Classroom(models.Model):
    class_name = models.CharField(max_length=10, unique=True)  # 예: 1반, 2반
    teacher = models.CharField(max_length=50)  # 예: 김선생님
	"""
	의미
	- 반이라는 개념 자체를 하나의 테이블로 분리   
	- 반 이름만 알면 → 담임 선생님을 알 수 있음
	- 3NF(이행 종속 제거)의 결과
	"""

    def __str__(self):
        return f"{self.class_name} ({self.teacher})"


# 2. 학생 테이블
class Student(models.Model):
    name = models.CharField(max_length=50)
    classroom = models.ForeignKey(
	    Classroom, 
	    on_delete=models.CASCADE, 
	    related_name='students'
	)
	"""
	의미
	- 학생은 반에 소속됨 
	- 그래서 classroom은 ForeignKey
	"""
    def __str__(self):
        return f"{self.name} - {self.classroom.class_name}"


# 3. 연락처 테이블
class Phone(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='phones'
    )
    number = models.CharField(max_length=20)
	"""
	의미
	- 학생 1명은 전화번호를 여러 개 가질 수 있음  
	- 그래서 연락처를 학생 테이블에 넣지 않고 분리
	"""
    def __str__(self):
        return f"{self.student.name}: {self.number}"


# 4. 성적 테이블
class Score(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='scores'
    )
    subject = models.CharField(max_length=30)
    score = models.PositiveIntegerField()

    class Meta:
        unique_together = ('student', 'subject')  # 복합키 대체
	"""
	의미
	- 학생 + 과목이 하나의 성적  
	- 같은 학생이 같은 과목을 두 번 가질 수 없음 
	- Django에서는 복합 PK 대신 `unique_together`로 구현
	"""
    def __str__(self):
        return f"{self.student.name} - {self.subject}: {self.score}"

        