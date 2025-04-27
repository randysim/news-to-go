import { Component, OnInit } from "@angular/core"
import { CommonModule } from "@angular/common"
import { Router } from "@angular/router"
import { VideoService, Video } from "../../services/video.service"

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    standalone: true,
    imports: [CommonModule]
})
export class DashboardComponent implements OnInit {
    videos: Video[] = [];
    loading = true;
    error: string | null = null;

    constructor(
        private videoService: VideoService,
        private router: Router
    ) {}
    
    ngOnInit(): void {
        this.loadVideos();
    }

    private loadVideos(): void {
        this.loading = true;
        this.error = null;
        
        this.videoService.getVideos().subscribe({
            next: (videos) => {
                this.videos = videos;
                this.loading = false;
            },
            error: (error) => {
                this.error = 'Failed to load videos. Please try again later.';
                this.loading = false;
                console.error('Error loading videos:', error);
            }
        });
    }

    onVideoClick(video: Video): void {
        console.log('Video clicked:', video); // Add logging to debug
        this.router.navigate(['/dashboard', video.id]);
    }

    openNewsUrl(url: string | null): void {
        if (url) {
            window.open(url, '_blank');
        }
    }
}