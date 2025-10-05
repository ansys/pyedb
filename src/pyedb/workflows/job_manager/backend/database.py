# src/pyedb/workflows/job_manager/backend/database.py

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from .job import Job

logger = logging.getLogger(__name__)


class JobDatabase:
    """Database handler for storing and retrieving job information."""

    def __init__(self, database_path: str = "pyedb_jobs.db"):
        self.database_path = database_path
        self._init_database()

    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    project TEXT NOT NULL,
                    simulation_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    batch_system TEXT NOT NULL,
                    resources TEXT NOT NULL,
                    project_file TEXT,
                    submit_time TEXT NOT NULL,
                    start_time TEXT,
                    completion_time TEXT,
                    batch_options TEXT,
                    additional_args TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Job logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    log_level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
            ''')

            conn.commit()

    def add_job(self, job: Job) -> bool:
        """Add a new job to the database."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO jobs (
                        job_id, name, project, simulation_type, status, priority,
                        batch_system, resources, project_file, submit_time,
                        start_time, completion_time, batch_options, additional_args,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.job_id,
                    job.name,
                    job.project,
                    job.simulation_type,
                    job.status,
                    job.priority,
                    job.batch_system,
                    json.dumps(job.resources),
                    job.project_file,
                    job.submit_time.isoformat() if job.submit_time else None,
                    job.start_time.isoformat() if job.start_time else None,
                    job.completion_time.isoformat() if job.completion_time else None,
                    json.dumps(job.batch_options) if job.batch_options else None,
                    job.additional_args,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to add job to database: {e}")
            return False

    def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by its ID."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
                row = cursor.fetchone()

                if not row:
                    return None

                return self._row_to_job(row)

        except Exception as e:
            logger.error(f"Failed to get job from database: {e}")
            return None

    def get_jobs(self, filters: Optional[Dict[str, Any]] = None) -> List[Job]:
        """Retrieve all jobs, optionally filtered."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM jobs"
                params = []

                if filters:
                    conditions = []
                    for key, value in filters.items():
                        conditions.append(f"{key} = ?")
                        params.append(value)
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)

                query += " ORDER BY created_at DESC"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [self._row_to_job(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get jobs from database: {e}")
            return []

    def update_job_status(self, job_id: str, status: str,
                          start_time: Optional[datetime] = None,
                          completion_time: Optional[datetime] = None) -> bool:
        """Update job status and timestamps."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                update_fields = ["status = ?", "updated_at = ?"]
                params = [status, datetime.now().isoformat()]

                if start_time:
                    update_fields.append("start_time = ?")
                    params.append(start_time.isoformat())

                if completion_time:
                    update_fields.append("completion_time = ?")
                    params.append(completion_time.isoformat())

                params.append(job_id)

                cursor.execute(
                    f"UPDATE jobs SET {', '.join(update_fields)} WHERE job_id = ?",
                    params
                )

                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            return False

    def delete_job(self, job_id: str) -> bool:
        """Delete a job from the database."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Delete associated logs first
                cursor.execute('DELETE FROM job_logs WHERE job_id = ?', (job_id,))

                # Delete the job
                cursor.execute('DELETE FROM jobs WHERE job_id = ?', (job_id,))

                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Failed to delete job: {e}")
            return False

    def add_job_log(self, job_id: str, level: str, message: str) -> bool:
        """Add a log entry for a job."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO job_logs (job_id, log_level, message, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (job_id, level, message, datetime.now().isoformat()))

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to add job log: {e}")
            return False

    def get_job_logs(self, job_id: str) -> List[Dict[str, Any]]:
        """Get logs for a specific job."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    'SELECT log_level, message, timestamp FROM job_logs WHERE job_id = ? ORDER BY timestamp',
                    (job_id,)
                )

                rows = cursor.fetchall()
                return [
                    {"level": row[0], "message": row[1], "timestamp": row[2]}
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Failed to get job logs: {e}")
            return []

    def _row_to_job(self, row) -> Job:
        """Convert a database row to a Job object."""
        job = Job()
        job.job_id = row[0]
        job.name = row[1]
        job.project = row[2]
        job.simulation_type = row[3]
        job.status = row[4]
        job.priority = row[5]
        job.batch_system = row[6]
        job.resources = json.loads(row[7]) if row[7] else {}
        job.project_file = row[8]
        job.submit_time = datetime.fromisoformat(row[9]) if row[9] else None
        job.start_time = datetime.fromisoformat(row[10]) if row[10] else None
        job.completion_time = datetime.fromisoformat(row[11]) if row[11] else None
        job.batch_options = json.loads(row[12]) if row[12] else None
        job.additional_args = row[13]

        return job