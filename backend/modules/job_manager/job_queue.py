from collections import deque
from threading import Lock, Thread
from ..utils import debug_print

class JobQueue:
    def __init__(self):
        self._queue = deque()
        self._lock = Lock()
        self._is_job_running = False
        self._current_job = None
        # Make indexing jobs faster
        self._video_id_index = {}
    
    def enqueue_job(self, video_id: int, job):
        debug_print(f"Enqueuing job for video {video_id}, total of {len(self._queue)} jobs in queue")

        if self.get_job_by_video_id(video_id):
            raise ValueError(f"Job already exists for video {video_id}")
        
        with self._lock:
            self._queue.append({
                "video_id": video_id,
                "job": job,
                "status": "PENDING",
                "successful": None,
                "error": None,
            })
            self._video_id_index[video_id] = job # keep last job in here for video
        
        self.start_next_job()
    
    def start_next_job(self):
        with self._lock:
            if self._is_job_running:
                return None
        
            if not self._queue:
                return None

            self._is_job_running = True
            self._current_job = self._queue.popleft()
            self._current_job["status"] = "RUNNING"

            debug_print(f"Starting job for video {self._current_job['video_id']}, total of {len(self._queue)} jobs in queue")

            # Start the job in a new thread
            thread = Thread(target=self._run_job)
            thread.daemon = True
            thread.start()

            return self._current_job
    
    def _run_job(self):
        successful = True
        error = None
        try:
            self._current_job["job"]()
        except Exception as e:
            successful = False
            error = e
        finally:
            self.finish_current_job(successful, error)
    
    def finish_current_job(self, successful: bool, error: Exception):
        debug_print(f"Finishing job for video {self._current_job['video_id']}, total of {len(self._queue)} jobs in queue")
        
        with self._lock:
            if not self._is_job_running:
                return None
            
            self._current_job["status"] = "FINISHED"
            self._is_job_running = False
            self._current_job = None
            self._current_job["successful"] = successful
            self._current_job["error"] = str(error) if error else None
            
            if self._queue:
                self.start_next_job()
            return True
        
        
    def get_job_by_video_id(self, video_id: int):
        with self._lock:
            return self._video_id_index.get(video_id)
    
job_queue = JobQueue()