from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Text, Date, Time, Enum
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app import db, app
from datetime import datetime, time, timedelta, UTC
import enum


class Weekday(enum.IntEnum):
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6
    SATURDAY = 7


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))

    def __str__(self):
        return self.name


class User(Base, UserMixin):
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(300),
                    default="https://res.cloudinary.com/dtvg4cpoq/image/upload/v1766309306/nbkvoo9yacn0posek1ej.jpg")
    phone = Column(String(20), nullable=False, unique=True)
    status = Column(Boolean, default=True)
    money = Column(Integer, default=1_000_000_000)
    email = Column(String(255), nullable=False, unique=True)

    enrollment = relationship('Enrollment', backref="user", lazy=True)
    user_role = relationship('UserRole', backref='user', lazy=True)
    bill = relationship('Bill', backref='user', lazy=True)
    teach = relationship('Course', backref='teacher', lazy=True)
    notifications = relationship("Notification", backref="user", lazy=True)

    def has_role(self, role_name):
        return any(ur.role and ur.role.name == role_name
                   for ur in self.user_role)


class Role(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    user_role = relationship('UserRole', backref='role', lazy=True)
    def __str__(self):
        return self.name


class UserRole(db.Model):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    role_id = Column(Integer, ForeignKey(Role.id), primary_key=True)


class Language(Base):
    courses = relationship('Course', backref='language', lazy=True)


class Level(Base):
    description = Column(String(255))
    slogan = Column(String(255))
    course = relationship('Course', backref='level', lazy=True)


class Course(Base):
    fee = Column(Float, default=0.0)
    image = Column(String(255),
                   default="https://res.cloudinary.com/dtvg4cpoq/image/upload/v1766066896/%E1%BA%A3nh_kh%C3%B3a_h%E1%BB%8Dc_ti%E1%BA%BFng_anh_svycnr.jpg")
    description = Column(String(255))
    duration = Column(Integer, default=30)
    lang_id = Column(Integer, ForeignKey(Language.id), nullable=False)
    teacher_id = Column(Integer, ForeignKey(User.id), nullable=False)
    level_id = Column(Integer, ForeignKey(Level.id), nullable=False)

    notifications = relationship("Notification", backref="course", lazy=True)
    goals = relationship("Goal", backref="course", lazy=True)
    enrollment = relationship('Enrollment', backref='course', lazy=True)
    schedule = relationship('Schedule', backref="course", lazy=True)


class Schedule(db.Model):
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey(Course.id), nullable=False)
    weekday = Column(Enum(Weekday), default=Weekday.MONDAY)
    start_time = Column(Time, default=time(18, 0))
    end_time = Column(Time, default=time(20, 0))


class Goal(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text)

    course_id = Column(Integer, ForeignKey(Course.id), nullable=False)

    def __str__(self):
        return self.content


class Enrollment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    course_id = Column(Integer, ForeignKey(Course.id), nullable=False)
    status = Column(Boolean, default=True)
    day_assignment = Column(DateTime, default=datetime.now)
    scores = relationship('Score', backref='enrollment', lazy=True)
    attendance = relationship("Attendance", backref='enrollment', lazy=True)
    bill = relationship("Bill", backref="enrollment", lazy=True)


class Score(Base):
    score = Column(Float)
    rate = Column(Float, default=1.0)
    enrollment_id = Column(Integer, ForeignKey(Enrollment.id), nullable=False)


class Attendance(db.Model):
    id = Column(Integer, primary_key=True)
    enrollment_id = Column(Integer, ForeignKey(Enrollment.id), nullable=False)
    attend_date = Column(Date, default=datetime.date)
    present = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class Bill(Base):
    id_enroll = Column(Integer, ForeignKey(Enrollment.id))
    status = Column(Boolean, default=False)
    id_cashier = Column(Integer, ForeignKey(User.id), nullable=False)


class Notification(Base):
    content = Column(String(255))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey(User.id))
    course_id = Column(Integer, ForeignKey(Course.id))


class Task(Base):
    description = Column(Text)
    deadline = Column(DateTime, default=lambda: datetime.now(UTC) + timedelta(days=2))
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False)
    created_date = Column(DateTime,default=datetime.now)
    course = db.relationship("Course", backref="tasks")


class Submission(Base):
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text)
    file_url = db.Column(db.String(255))
    submitted_at = db.Column(db.DateTime, default=datetime.now)
    task = db.relationship("Task", backref="submissions")
    student = db.relationship("User")


# class Voucher(Base):
#     discount = Column(Float, default=0.0)
#     valid_from = Column(DateTime)
#     expires_at = Column(DateTime)


import hashlib

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.session.commit()

        password = hashlib.md5("123".encode("utf-8")).hexdigest()

        u = User(
            name="admin",
            username="admin",
            password=hashlib.md5("admin".encode()).hexdigest(),
            phone="0909123453",
            email="admin@gmail.com"
        )

        u1 = User(
            name="Phạm Thành Đạt",
            username="dat123",
            password=password,
            phone="0123456789",
            email="dat123@gmail.com"
        )

        u2 = User(
            name="Alex",
            username="alex",
            password=password,
            phone="1234567888",
            email="alex@gmail.com"
        )

        #
        r = Role(name="ADMIN", description="ADMIN")
        r1 = Role(name="STUDENT", description="Hoc vien")
        r3 = Role(name="TEACHER", description="giao vien")
        r4 = Role(name="CASHIER", description="THU NGÂN")

        ur = UserRole()
        ur.user = u
        ur.role = r

        ur1 = UserRole()
        ur1.user = u1
        ur1.role = r1

        ur3 = UserRole()
        ur3.user = u2
        ur3.role = r3

        ur4 = UserRole()
        ur4.user = u1
        ur4.role = r4

        db.session.add_all([r, r1, r3, r4, u, u1, ur, ur1, ur3, ur4])
        db.session.commit()

        lang = Language(name="English")
        lang1 = Language(name="France")

        db.session.add_all([lang, lang1])
        db.session.commit()

        c1 = Course(
            name="Tiếng Anh Giao Tiếp Cơ Bản",
            description="Khóa học dành cho người mới bắt đầu, tập trung nghe nói",
            fee=2500000,
        )

        c2 = Course(
            name="IELTS Foundation",
            description="Xây dựng nền tảng IELTS từ 0 đến 4.5",
            fee=3500000,

        )

        c3 = Course(
            name="IELTS Intensive 6.5+",
            description="Luyện đề chuyên sâu, chiến thuật làm bài",
            fee=6500000,

        )

        c4 = Course(
            name="TOEIC 450+",
            description="Phù hợp sinh viên và người đi làm",
            fee=3000000,

        )

        c5 = Course(
            name="Tiếng Anh Cho Người Đi Làm",
            description="Giao tiếp công sở, email, thuyết trình",
            fee=4000000,

        )
        c1.language = lang
        c2.language = lang
        c3.language = lang
        c4.language = lang
        c5.language = lang

        c1.teacher = u2
        c2.teacher = u2
        c3.teacher = u2
        c4.teacher = u2
        c5.teacher = u2

        l1 = Level(name="STARTER", description="Làm quen ngôn ngữ – dễ hiểu – học từ con số 0",
                   slogan="Nắm vững kiến thức nhập môn")
        l2 = Level(name="BEGINNER", description="Dành cho người mới bắt đầu – xây dựng nền móng vững chắc",
                   slogan="Xây dựng tư duy ngôn ngữ")
        l3 = Level(name="INTERMEDIATE", description="Dành cho học viên đã có nền tảng – nâng cao kỹ năng và phản xạ",
                   slogan="Phát triển kỹ năng chuyên sâu")
        l4 = Level(name="ADVANCED", description="Dành cho học viên muốn sử dụng ngôn ngữ chuyên nghiệp",
                   slogan="Làm chủ ngôn ngữ & ứng dụng")

        c1.level = l1
        c2.level = l2
        c3.level = l3
        c4.level = l4
        c5.level = l3

        c6 = Course(
            name="Tiếng Anh Mất Gốc Toàn Diện",
            description="Học lại từ phát âm, từ vựng đến mẫu câu cơ bản",
            fee=2200000,
        )

        c7 = Course(
            name="Ngữ Pháp Tiếng Anh Cơ Bản",
            description="Hệ thống hóa ngữ pháp nền tảng, dễ hiểu, dễ áp dụng",
            fee=2600000,
        )

        c8 = Course(
            name="Tiếng Anh Giao Tiếp Trung Cấp",
            description="Phản xạ giao tiếp, mở rộng chủ đề đời sống và công việc",
            fee=4200000,
        )

        c9 = Course(
            name="IELTS Pre-Intermediate",
            description="Củng cố nền tảng IELTS, hướng tới band 5.5",
            fee=3800000,
        )

        c10 = Course(
            name="Tiếng Anh Thuyết Trình Chuyên Nghiệp",
            description="Thuyết trình, họp, trình bày ý tưởng bằng tiếng Anh",
            fee=5500000,
        )
        for c in [c6, c7, c8, c9, c10]:
            c.language = lang
            c.teacher = u2

        c6.level = l1
        c7.level = l2
        c8.level = l3
        c9.level = l2
        c10.level = l4
        db.session.add_all([c6, c7, c8, c9, c10])
        db.session.commit()

        db.session.add_all([c1, c2, c3, c4, c5, l1, l2, l3, l4])
        db.session.commit()


        def add_goals(course, goals):
            for g in goals:
                db.session.add(Goal(content=g, course=course))


        add_goals(c1, [
            "Phát âm chuẩn các âm cơ bản trong tiếng Anh",
            "Giao tiếp tự tin trong các tình huống hằng ngày",
            "Nắm vững mẫu câu giao tiếp thông dụng",
            "Nghe – hiểu hội thoại đơn giản",
            "Phản xạ tiếng Anh mà không cần dịch sang tiếng Việt",
            "Giới thiệu bản thân và trò chuyện cơ bản với người nước ngoài"
        ])
        add_goals(c2, [
            "Làm quen cấu trúc đề thi IELTS",
            "Xây dựng nền tảng từ vựng và ngữ pháp học thuật",
            "Nghe – đọc hiểu các dạng bài cơ bản",
            "Làm quen Writing Task 1 và Task 2",
            "Chuẩn bị nền tảng đạt band 4.0 – 4.5"
        ])
        add_goals(c3, [
            "Chiến thuật làm bài IELTS hiệu quả",
            "Luyện đề chuyên sâu 4 kỹ năng",
            "Nâng cao tư duy học thuật và phản xạ tiếng Anh",
            "Cải thiện Writing và Speaking band cao",
            "Mục tiêu đạt IELTS 6.5+"
        ])
        add_goals(c4, [
            "Nắm vững cấu trúc đề thi TOEIC",
            "Luyện nghe – đọc theo format đề thật",
            "Cải thiện từ vựng và ngữ pháp trọng tâm",
            "Nâng cao tốc độ làm bài",
            "Mục tiêu đạt TOEIC 450+"
        ])
        add_goals(c5, [
            "Giao tiếp tiếng Anh trong môi trường công sở",
            "Viết email và báo cáo bằng tiếng Anh",
            "Thuyết trình và họp bằng tiếng Anh",
            "Sử dụng tiếng Anh trong công việc hằng ngày",
            "Tăng sự tự tin khi làm việc với đối tác nước ngoài"
        ])

        add_goals(c6, [
            "Học lại phát âm chuẩn từ đầu",
            "Nắm vững từ vựng và mẫu câu cơ bản",
            "Xây dựng nền tảng ngữ pháp căn bản",
            "Nghe – nói các tình huống đơn giản",
            "Phù hợp người mất gốc hoặc lâu không dùng tiếng Anh"
        ])
        add_goals(c7, [
            "Hệ thống hóa toàn bộ ngữ pháp nền tảng",
            "Hiểu rõ cách sử dụng thì và cấu trúc câu",
            "Áp dụng ngữ pháp vào giao tiếp và viết",
            "Giảm lỗi sai khi nói và viết tiếng Anh",
            "Xây nền tảng vững chắc cho các khóa nâng cao"
        ])
        add_goals(c8, [
            "Mở rộng vốn từ vựng theo chủ đề",
            "Phản xạ giao tiếp nhanh và tự nhiên",
            "Nâng cao kỹ năng nghe – nói",
            "Giao tiếp tự tin trong công việc và đời sống",
            "Chuẩn bị cho các khóa học nâng cao"
        ])
        add_goals(c9, [
            "Củng cố nền tảng IELTS",
            "Nâng cao kỹ năng nghe và đọc hiểu",
            "Làm quen Writing Task 1 & 2",
            "Cải thiện Speaking theo band 5.0 – 5.5",
            "Chuẩn bị cho khóa IELTS Intensive"
        ])
        add_goals(c10, [
            "Thuyết trình tự tin bằng tiếng Anh",
            "Sắp xếp ý tưởng và diễn đạt logic",
            "Giao tiếp trong họp và đàm phán",
            "Sử dụng tiếng Anh chuyên nghiệp",
            "Phù hợp quản lý và nhân sự cấp cao"
        ])

        db.session.commit()
        c_fr1 = Course(
            name="Tiếng Pháp Giao Tiếp Cơ Bản",
            description="Khóa học tiếng Pháp cho người mới bắt đầu",
            fee=2800000,
            language=lang1,
            teacher=u2,
            level=l1
        )

        c_fr2 = Course(
            name="Tiếng Pháp Cho Người Đi Làm",
            description="Giao tiếp tiếng Pháp trong môi trường công việc",
            fee=4500000,
            language=lang1,
            teacher=u2,
            level=l3
        )

        db.session.add_all([c_fr1, c_fr2])
        db.session.commit()
        add_goals(c_fr1, [
            "Phát âm chuẩn bảng chữ cái tiếng Pháp",
            "Giao tiếp cơ bản trong đời sống hằng ngày",
            "Nắm vững mẫu câu chào hỏi, mua sắm",
            "Xây dựng nền tảng từ vựng tiếng Pháp"
        ])

        add_goals(c_fr2, [
            "Giao tiếp tiếng Pháp trong công việc",
            "Viết email và trao đổi cơ bản",
            "Thuyết trình ngắn bằng tiếng Pháp",
            "Tăng sự tự tin khi làm việc với đối tác Pháp"
        ])

        db.session.commit()
        lang_kr = Language(name="Korean")
        lang_jp = Language(name="Japanese")
        lang_cn = Language(name="Chinese")
        lang_de = Language(name="German")

        db.session.add_all([lang_kr, lang_jp, lang_cn, lang_de])
        db.session.commit()
        c_kr1 = Course(
            name="Tiếng Hàn Giao Tiếp Cơ Bản",
            description="Khóa học tiếng Hàn cho người mới bắt đầu",
            fee=2900000,
            language=lang_kr,
            teacher=u2,
            level=l1
        )

        c_kr2 = Course(
            name="TOPIK I (Cấp 1–2)",
            description="Luyện thi TOPIK I cho người học tiếng Hàn",
            fee=3600000,
            language=lang_kr,
            teacher=u2,
            level=l2
        )

        db.session.add_all([c_kr1, c_kr2])
        db.session.commit()
        add_goals(c_kr1, [
            "Làm quen bảng chữ cái Hangul",
            "Giao tiếp cơ bản trong đời sống",
            "Nghe – nói các tình huống đơn giản",
            "Xây dựng từ vựng tiếng Hàn nền tảng"
        ])

        add_goals(c_kr2, [
            "Nắm vững cấu trúc đề thi TOPIK I",
            "Luyện từ vựng và ngữ pháp trọng tâm",
            "Luyện đề theo format đề thật",
            "Mục tiêu đạt TOPIK cấp 2"
        ])
        c_jp1 = Course(
            name="Tiếng Nhật Giao Tiếp Cơ Bản",
            description="Khóa học tiếng Nhật cho người mới bắt đầu",
            fee=3000000,
            language=lang_jp,
            teacher=u2,
            level=l1
        )

        c_jp2 = Course(
            name="JLPT N5",
            description="Luyện thi JLPT N5 từ cơ bản",
            fee=3800000,
            language=lang_jp,
            teacher=u2,
            level=l2
        )

        db.session.add_all([c_jp1, c_jp2])
        db.session.commit()
        add_goals(c_jp1, [
            "Làm quen Hiragana và Katakana",
            "Giao tiếp tiếng Nhật cơ bản",
            "Nghe – nói tình huống đời sống",
            "Xây dựng nền tảng từ vựng"
        ])

        add_goals(c_jp2, [
            "Nắm vững cấu trúc đề JLPT N5",
            "Luyện từ vựng và ngữ pháp N5",
            "Luyện nghe và đọc hiểu",
            "Mục tiêu đậu JLPT N5"
        ])
        c_cn1 = Course(
            name="Tiếng Trung Giao Tiếp Cơ Bản",
            description="Học giao tiếp tiếng Trung từ con số 0",
            fee=2800000,
            language=lang_cn,
            teacher=u2,
            level=l1
        )

        c_cn2 = Course(
            name="HSK 3",
            description="Luyện thi HSK 3 chuẩn cấu trúc đề",
            fee=4200000,
            language=lang_cn,
            teacher=u2,
            level=l3
        )

        db.session.add_all([c_cn1, c_cn2])
        db.session.commit()
        add_goals(c_cn1, [
            "Làm quen Pinyin và thanh điệu",
            "Giao tiếp tiếng Trung cơ bản",
            "Nghe – nói các chủ đề quen thuộc",
            "Xây dựng vốn từ vựng nền tảng"
        ])

        add_goals(c_cn2, [
            "Nắm vững cấu trúc đề HSK 3",
            "Luyện nghe – đọc hiểu nâng cao",
            "Mở rộng từ vựng học thuật",
            "Mục tiêu đạt HSK 3"
        ])
        c_de1 = Course(
            name="Tiếng Đức Giao Tiếp Cơ Bản",
            description="Khóa học tiếng Đức cho người mới bắt đầu",
            fee=3100000,
            language=lang_de,
            teacher=u2,
            level=l1
        )

        c_de2 = Course(
            name="Tiếng Đức A2",
            description="Nâng cao giao tiếp và ngữ pháp tiếng Đức",
            fee=4500000,
            language=lang_de,
            teacher=u2,
            level=l3
        )

        db.session.add_all([c_de1, c_de2])
        db.session.commit()
        add_goals(c_de1, [
            "Phát âm chuẩn tiếng Đức",
            "Giao tiếp các tình huống cơ bản",
            "Nắm vững mẫu câu thông dụng",
            "Xây dựng nền tảng từ vựng"
        ])

        add_goals(c_de2, [
            "Giao tiếp tiếng Đức nâng cao",
            "Nâng cao ngữ pháp và từ vựng",
            "Nghe – nói trong môi trường học tập",
            "Mục tiêu đạt trình độ A2"
        ])
        db.session.commit()

        userStudent = User(
            name="Phạm Thành Đạt",
            username="student",
            password=password,
            phone="0123256789",
            email="student@gmail.com"
        )

        userr = UserRole()
        userr.user = userStudent
        userr.role = r1
        db.session.add_all([userr, userStudent])
        db.session.commit()
        import random

        notifications = []

        for i in range(1, 21):
            noti = Notification(
                name=f"Thông báo {i}",
                content=f"Nội dung thông báo số {i}",
                user_id=1,
                course_id=random.randint(1, 3),
                is_read=False
            )
            notifications.append(noti)
        db.session.add_all(notifications)
        db.session.commit()


        # ====== THÊM THỜI KHÓA BIỂU ======

        def add_schedule(course, weekdays):
            for wd in weekdays:
                db.session.add(Schedule(
                    course_id=course.id,
                    weekday=wd,  # Enum Weekday
                    start_time=time(18, 0),
                    end_time=time(20, 0)
                ))


        # --- Các khóa tiếng Anh ---
        add_schedule(c1, [Weekday.MONDAY, Weekday.WEDNESDAY])
        add_schedule(c2, [Weekday.TUESDAY, Weekday.THURSDAY])
        add_schedule(c3, [Weekday.TUESDAY, Weekday.THURSDAY])
        add_schedule(c4, [Weekday.MONDAY, Weekday.WEDNESDAY])
        add_schedule(c5, [Weekday.FRIDAY])

        add_schedule(c6, [Weekday.MONDAY, Weekday.WEDNESDAY])
        add_schedule(c7, [Weekday.TUESDAY, Weekday.THURSDAY])
        add_schedule(c8, [Weekday.FRIDAY])
        add_schedule(c9, [Weekday.TUESDAY, Weekday.THURSDAY])
        add_schedule(c10, [Weekday.SATURDAY])

        # --- Tiếng Pháp ---
        add_schedule(c_fr1, [Weekday.SATURDAY])
        add_schedule(c_fr2, [Weekday.SUNDAY])

        # --- Tiếng Hàn ---
        add_schedule(c_kr1, [Weekday.MONDAY, Weekday.WEDNESDAY])
        add_schedule(c_kr2, [Weekday.TUESDAY, Weekday.THURSDAY])

        # --- Tiếng Nhật ---
        add_schedule(c_jp1, [Weekday.SATURDAY])
        add_schedule(c_jp2, [Weekday.SUNDAY])

        # --- Tiếng Trung ---
        add_schedule(c_cn1, [Weekday.MONDAY, Weekday.WEDNESDAY])
        add_schedule(c_cn2, [Weekday.TUESDAY, Weekday.THURSDAY])

        # --- Tiếng Đức ---
        add_schedule(c_de1, [Weekday.SATURDAY])
        add_schedule(c_de2, [Weekday.SUNDAY])

        db.session.commit()
