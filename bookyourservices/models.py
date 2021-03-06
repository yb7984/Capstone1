from utils import db, hash_password, check_password_hash
from flask_sqlalchemy import SQLAlchemy, sqlalchemy
from utils import *
import datetime
import json


class Admin(db.Model):
    """Admin"""
    __tablename__ = 'admins'

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    authorization = db.Column(
        db.String(100), nullable=False, server_default="regular")

    created = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sqlalchemy.func.now()
    )

    pwd_token = db.Column(db.Text, nullable=True , server_default='')

    is_active = db.Column(db.Boolean, nullable=False, server_default="TRUE")

    @property
    def full_name(self):
        """Return the full name of the admin"""
        if len(self.first_name) == 0 and len(self.last_name) == 0:
            return self.username
            
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        e = self
        return f"<Admin {e.username} {e.first_name} {e.last_name} {e.email}>"

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register admin w/hashed password & return admin."""

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hash_password(password), email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, password):
        """Validate that admin exists & password is correct.

        Return admin if valid; else return False.
        """

        u = Admin.query.filter(Admin.username==username, Admin.is_active==True).first()

        if u and check_password_hash(hashed_pwd=u.password, password=password):
            # return admin instance
            return u
        else:
            return False

    @classmethod
    def update_password(cls, username, password):
        """Update password"""

        u = Admin.query.filter(Admin.username == username).first()

        if u:
            u.password = hash_password(password)
            u.pwd_token = ""
            db.session.commit()

            return u
        else:
            return False

    @classmethod
    def update_password_by_token(cls, token, password):
        """Update password by token"""

        u = Admin.query.filter(Admin.pwd_token == token , Admin.is_active==True).first()

        if u:
            u.password = hash_password(password)
            u.pwd_token = ""
            db.session.commit()

            return u

        return False


class User(db.Model):
    """User"""
    __tablename__ = 'users'

    # regualar information
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), server_default='')
    description = db.Column(db.Text, server_default='')
    image = db.Column(db.Text, server_default='')

    # for google calendar use
    calendar_id = db.Column(db.Text, server_default='')
    calendar_email = db.Column(db.String(50), server_default='')

    #provider or customer
    is_provider = db.Column(db.Boolean, nullable=False, server_default="FALSE")

    updated = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sqlalchemy.func.now()
    )
    created = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sqlalchemy.func.now()
    )

    pwd_token = db.Column(db.Text, nullable=True, server_default='')

    is_active = db.Column(db.Boolean, nullable=False, server_default="TRUE")

    # Services
    services = db.relationship(
        "Service", backref="user", cascade="all, delete, delete-orphan", passive_deletes=True)

    # Schedules
    schedules = db.relationship(
        "Schedule", backref="user", cascade="all, delete, delete-orphan", passive_deletes=True)

    @property
    def full_name(self):
        """Return the full name of the admin"""
        if self.first_name == '' and self.last_name == '':
            return self.username

        return f"{self.first_name} {self.last_name}"

    @property
    def image_url(self):
        """Return the image url"""
        if self.image is None or len(self.image) == 0:
            return DEFAULT_IMAGE_USER

        return upload_file_url(self.image, USER_UPLOAD_DIRNAME)

    def __repr__(self):
        """Representation of this class"""
        e = self
        return f"<User {e.username} {e.first_name} {e.last_name} {e.email}>"

    @classmethod
    def register(cls, username, password, email, first_name, last_name, is_provider=False):
        """Register user w/hashed password & return user."""

        # return instance of user w/username and hashed pwd
        return cls(
            username=username,
            password=hash_password(password),
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_provider=is_provider)

    @classmethod
    def authenticate(cls, username, password):
        """Validate that admin exists & password is correct.

        Return admin if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and u.is_active and check_password_hash(u.password, password):
            # return admin instance
            return u
        else:
            return False

    @classmethod
    def update_password(cls, username, password):
        """Update password"""

        u = User.query.filter(User.username == username).first()

        if u:
            u.password = hash_password(password)
            db.session.commit()

            return u
        else:
            return False

    @classmethod
    def update_password_by_token(cls, token, password):
        """Update password by token"""

        u = User.query.filter(User.pwd_token == token, User.is_active==True).first()

        if u:
            u.password = hash_password(password)
            u.pwd_token = ''
            db.session.commit()

            return u

        return False

    def serialize(self):
        """Serialize a User SQLAlchemy obj to dictionary."""

        return {
            "username": self.username,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "description": self.description,
            "image": self.image,
            "image_url": self.image_url,
            "is_provider": self.is_provider,
            "updated": self.updated,
            "created": self.created,
            "is_active": self.is_active
        }


class Category(db.Model):
    """Categories"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, server_default="true")

    categories_services = db.relationship(
        "CategoryService", backref="category", cascade="all, delete, delete-orphan", passive_deletes=True)
    services = db.relationship(
        "Service", secondary="categories_services", backref="categories")

    def __repr__(self):
        """Representation of this class"""
        e = self
        return f"<Category id={e.id} name={e.name}>"

    def serialize(self):
        """Serialize a Category SQLAlchemy obj to dictionary."""

        return {
            "id": self.id,
            "name": self.name,
            "is_active": self.is_active
        }


class Service(db.Model):
    """Services from the providers"""
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), db.ForeignKey(
        'users.username', ondelete="CASCADE"))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False, server_default='')
    image = db.Column(db.Text, server_default='')
    updated = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sqlalchemy.func.now()
    )
    created = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sqlalchemy.func.now()
    )
    is_active = db.Column(db.Boolean, nullable=False, server_default="TRUE")

    categories_services = db.relationship(
        "CategoryService", backref="service", cascade="all, delete, delete-orphan", passive_deletes=True)

    @property
    def image_url(self):
        """Return the image url"""
        if self.image is None or len(self.image) == 0:
            return DEFAULT_IMAGE_SERVICE

        return upload_file_url(self.image, dirname=SERVICE_UPLOAD_DIRNAME)

    def set_categoiry_ids(self, ids=[]):
        """Set categories with category_id list"""

        self.categories_services.clear()
        for category_id in ids:
            self.categories_services.append(CategoryService(
                category_id=int(category_id), service_id=self.id))

    def get_category_ids(self):
        """Return the list of the category_ids"""

        ids = []
        for item in self.categories_services:
            ids.append(item.category_id)

        return ids

    def __repr__(self):
        """Representation of this class"""
        e = self
        return f"<Service name={e.name} username={e.username}>"

    def serialize(self):
        """Serialize a Service SQLAlchemy obj to dictionary."""

        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "image_url": self.image_url,
            "updated": self.updated,
            "created": self.created,
            "is_active": self.is_active,
            "categories": [category.serialize() for category in self.categories],
            "category_ids": self.get_category_ids(),
            "provider": self.user.full_name
        }


class CategoryService(db.Model):
    """Categories to Services"""
    __tablename__ = 'categories_services'

    category_id = db.Column(db.Integer, db.ForeignKey(
        "categories.id", ondelete="CASCADE"), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey(
        "services.id", ondelete="CASCADE"), primary_key=True)

    def __repr__(self):
        """Representation of this class"""
        e = self
        return f"<CategoryService category_id={e.category_id} service_id={e.service_id}>"

    def serialize(self):
        """Serialize a CategoryService SQLAlchemy obj to dictionary."""

        return {
            "category_id": self.category_id,
            "service_id": self.service_id
        }


class Schedule(db.Model):
    """Schedule setting for providers"""
    __tablename__ = 'schedules'

    username = db.Column(db.String(20), db.ForeignKey(
        'users.username', ondelete="CASCADE"), primary_key=True)
    date_exp = db.Column(db.String(20), nullable=False, primary_key=True)
    schedules = db.Column(db.Text, nullable=False, server_default="")
    is_active = db.Column(db.Boolean, nullable=False, server_default="TRUE")

    @property
    def schedule_name(self):
        """Return the schedule type display name"""

        if self.date_exp in [str(item) for item in range(7)]:
            # for weekly schedules return the day of the week
            return WEEKDAYS[int(self.date_exp)]

        # for other schedule, return the date
        return datetime.date.fromisoformat(self.date_exp).strftime(DATE_FORMAT)

    @property
    def schedule_list(self):
        """Return the current schedule list"""

        if len(self.schedules) > 0:
            return json.loads(self.schedules)

        return []

    def available_times(self, date):
        """Return the list of available time for specific date"""

        list = self.schedule_list

        if len(self.date_exp) == 1:
            if date.isoweekday() % 7 != int(self.date_exp):
                # not the day of the week
                return []
        elif date.isoformat() != self.date_exp:
            # not the specific date
            return []

        return [(f"{item['start']}-{item['end']}", f"{item['start']} to {item['end']}") for item in list if Schedule.check_available(self.username, date, item)]

    @staticmethod
    def check_available(username, date, item):
        """Check if a schedule time frame is available"""

        start_time = datetime.time.fromisoformat(item["start"])
        end_time = datetime.time.fromisoformat(item["end"])

        start = datetime.datetime.combine(date, start_time)
        end = datetime.datetime.combine(date, end_time)

        return Appointment.check_available(username, start, end)

    def __repr__(self):
        """Representation of this class"""
        e = self
        return f"<Schedule date_exp={e.date_exp} username={e.username}>"

    def serialize(self):
        """Serialize a Schedule SQLAlchemy obj to dictionary."""

        return {
            "username": self.username,
            "date_exp": self.date_exp,
            "schedules": self.schedules,
            "schedule_name": self.schedule_name,
            "is_active": self.is_active
        }


class Appointment(db.Model):
    """Appointments"""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # available after generated google calendar event
    event_id = db.Column(db.Text, server_default="")
    provider_username = db.Column(db.String(20), db.ForeignKey(
        'users.username', ondelete="CASCADE"))
    customer_username = db.Column(db.String(20), db.ForeignKey(
        'users.username', ondelete="CASCADE"))
    start = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    end = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey(
        'services.id', ondelete="CASCADE"))
    note = db.Column(db.Text, nullable=False, server_default="")
    updated = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sqlalchemy.func.now()
    )
    created = db.Column(
        db.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sqlalchemy.func.now()
    )
    is_active = db.Column(db.Boolean, nullable=False, server_default="TRUE")

    provider = db.relationship("User", foreign_keys=[provider_username], backref=db.backref(
        "appointments_as_provider", lazy="dynamic"))

    customer = db.relationship("User", foreign_keys=[customer_username], backref=db.backref(
        "appointments_as_customer", lazy="dynamic"))

    service = db.relationship("Service", foreign_keys=[service_id])

    @property
    def summary(self):
        """Return the google calendar summary"""

        return f"{self.service.name} with {self.customer.full_name}"

    @property
    def description(self):
        """Return the google calendar description"""

        return f"""Service:{self.service.name}
Customer:{self.customer.full_name}
Provider:{self.provider.full_name}
Time:{self.start} to {self.end}
Note:{self.note}"""


    def __repr__(self):
        """Representation of this class"""
        e = self
        return f"<Appointment id={e.id} provider_username={e.provider_username} customer_username={e.customer_username} start={e.start} end={e.end}>"

    @staticmethod
    def check_available(username, start, end, appointment_id=0):
        """Check if there is a conflict with a schedule"""
        count = Appointment.query.filter(
            (Appointment.is_active == True) &
            (Appointment.provider_username == username) &
            (Appointment.id != appointment_id) &
            (
                (
                    ((Appointment.start <= start) & (Appointment.end > start)) |
                    ((Appointment.start < end)
                     & (Appointment.end >= end))
                ) |
                (
                    ((Appointment.start >= start) & (Appointment.start < end)) |
                    ((Appointment.end > start)
                     & (Appointment.end <= end))
                )
            )).count()

        return (count == 0)

    @property
    def available(self):
        """Check if the time frame is available"""

        return Appointment.check_available(self.provider_username, self.start, self.end, self.id)

    def serialize(self):
        """Serialize a Appointment SQLAlchemy obj to dictionary."""

        return {
            "id": self.id,
            "event_id": self.event_id,
            "provider_username": self.provider_username,
            "customer_username": self.customer_username,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "service_id": self.service_id,
            "note": self.note,
            "summary": self.summary,
            "description": self.description,
            "updated": self.updated,
            "created": self.created,
            "is_active": self.is_active,
            "provider": self.provider.full_name,
            "customer": self.customer.full_name,
            "service": self.service.name
        }
