# This file has an sqlite database to store concurrent analysis requests with their result, a tracker for the job queue system

from sqlalchemy import create_engine, Text, Column, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from datetime import datetime, timezone
import os
from uuid import uuid4

Base = declarative_base()

class DocumentAnalysisJobs(Base):
    """Table schema definition"""
    __tablename__ = "document_analysis_jobs"

    job_id = Column(String, primary_key=True, default=lambda: f"Job_{str(uuid4())}")
    file_path = Column(String, nullable=False)
    analysis_query = Column(String, nullable=False)
    job_status = Column(String, default="In Queue")
    job_result = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class DocumentAnalysisJobDB:
    """Manager class for the Job database"""

    def __init__(self, db_path:str=None):
        """
        Initialize the DB connection via SQLite.

        Args:
        db_path (str, optional): Path to the SQLite Database File, if None, will use the `job_database` folder
        """

        if db_path is None:
            db_dir = "job_database"
            db_path = f"{db_dir}/analysis_jobs.db"

        self.db_url = f'sqlite:///{db_path}'
        self.engine = create_engine(self.db_url, connect_args={"check_same_thread" : False})

        Base.metadata.create_all(bind=self.engine)

    def get_local_session(self):
        # autocommit=False: Manual transaction control for better consistency - helps in batching db commits, can rollback transaction in case of issues
        # autoflush=True: Automatic flushing ensures queries see latest changes
        return sessionmaker(autocommit=False, autoflush=True, bind=self.engine)