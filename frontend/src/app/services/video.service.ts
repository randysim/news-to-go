import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Video {
  id: number;
  title: string;
  news_url: string | null;
  news_title: string | null;
  news_content: string | null;
  script: string | null;
  config: string | null;
  created_at: string;
  updated_at: string;
  video_generated: boolean;
}

export interface Job {
  status: string;
  job_type?: 'SCRAPE' | 'SCRIPT' | 'VIDEO';
}

export interface JobPayload {
  job_type: 'SCRAPE' | 'SCRIPT' | 'VIDEO';
  url?: string;
}

export interface JobDTO {
  job: Job;
}

export interface JobCreateDTO {
    message: string;
}

@Injectable({
  providedIn: 'root'
})
export class VideoService {
  constructor(private http: HttpClient) {}

  getVideos(): Observable<Video[]> {
    return this.http.get<Video[]>(`${environment.apiUrl}/videos/`);
  }

  getVideo(id: number): Observable<Video> {
    return this.http.get<Video>(`${environment.apiUrl}/videos/${id}/`);
  }

  updateVideo(id: number, data: Partial<Video>): Observable<Video> {
    return this.http.patch<Video>(`${environment.apiUrl}/videos/${id}/`, data);
  }

  getJobStatus(videoId: number): Observable<JobDTO> {
    return this.http.get<JobDTO>(`${environment.apiUrl}/videos/${videoId}/jobs/`);
  }

  createJob(videoId: number, payload: JobPayload): Observable<JobCreateDTO> {
    return this.http.post<JobCreateDTO>(`${environment.apiUrl}/videos/${videoId}/jobs/`, payload);
  }

  getVideoFile(videoId: number): Observable<Blob> {
    return this.http.get(`${environment.apiUrl}/videos/${videoId}/file/`, {
      responseType: 'blob'
    });
  }

  createVideo(title: string) {
    return this.http.post<Video>(`${environment.apiUrl}/videos/`, { title });
  }

  deleteVideo(id: number): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/videos/${id}/`);
  }
} 