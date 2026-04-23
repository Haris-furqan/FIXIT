import enum
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey, Enum, CheckConstraint, text
from database import Base

class UserRole(str, enum.Enum):
    customer = 'customer'
    worker = 'worker'


class JobStatus(str, enum.Enum):
    active = 'active'
    assigned = 'assigned'
    completed = 'completed'
    cancelled = 'cancelled'


class BidStatus(str, enum.Enum):
    active = 'active'
    selected = 'selected'
    cancelled = 'cancelled'


class InvoiceStatus(str, enum.Enum):
    pending = 'pending'
    held = 'held'
    released = 'released'
    disputed = 'disputed'



class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone_number = Column(String(25), nullable=False)
    firebase_uid = Column(String(255), nullable=False)
    cnic = Column(String(25), nullable=False)
    role = Column(Enum(UserRole), nullable=False)


class Worker(Base):
    __tablename__ = "workers"

    worker_id = Column(Integer, primary_key=True, index=True)
    # Note the ondelete="CASCADE" to match Person A's constraint exactly
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    profession = Column(String(255), nullable=False)


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_description = Column(String(255), nullable=False)
    status = Column(Enum(JobStatus), nullable=False)
    x_coords = Column(DECIMAL(9, 6), nullable=False)
    y_coords = Column(DECIMAL(9, 6), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))


class Bid(Base):
    __tablename__ = "bids"

    bid_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    bid_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(BidStatus), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=False)
    comment = Column(String(255), nullable=True)
    stars = Column(Integer, CheckConstraint('stars >= 1 AND stars <= 5'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))


class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id = Column(Integer, primary_key=True, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.worker_id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))
    status = Column(Enum(InvoiceStatus), nullable=False, server_default='pending')


class InvoiceHistory(Base):
    __tablename__ = "invoice_history"

    history_id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.invoice_id"), nullable=False)
    status = Column(Enum(InvoiceStatus), nullable=False)
    changed_at = Column(TIMESTAMP, server_default=text("NOW()"))