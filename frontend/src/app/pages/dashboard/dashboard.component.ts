import { Component, OnInit } from "@angular/core"
import { CommonModule } from "@angular/common"
import { Router } from "@angular/router"
import { VideoService, Video } from "../../services/video.service"
import { SnackbarService } from "../../services/snackbar.service"
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { CreateVideoDialogComponent } from '../../components/create-video-dialog/create-video-dialog.component';
import { ConfirmDialogComponent } from '../../components/confirm-dialog/confirm-dialog.component';

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    standalone: true,
    imports: [CommonModule, MatButtonModule, MatDialogModule]
})
export class DashboardComponent implements OnInit {
    videos: Video[] = [];
    loading = true;
    error: string | null = null;

    constructor(
        private videoService: VideoService,
        private router: Router,
        private snackbarService: SnackbarService,
        private dialog: MatDialog
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
                this.snackbarService.show(this.error, 'error');
                this.loading = false;
                console.error('Error loading videos:', error);
            }
        });
    }

    onVideoClick(video: Video): void {
        console.log('Video clicked:', video); // Add logging to debug
        this.router.navigate(['/dashboard', video.id]);
    }

    deleteVideo(video: Video, event: Event): void {
        event.stopPropagation(); // Prevent the card click event from firing
        
        const dialogRef = this.dialog.open(ConfirmDialogComponent, {
            width: '400px',
            data: { title: video.title }
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result) {
                this.videoService.deleteVideo(video.id).subscribe({
                    next: () => {
                        this.snackbarService.show('Video deleted successfully', 'success');
                        this.loadVideos();
                    },
                    error: (error) => {
                        this.snackbarService.show('Failed to delete video', 'error');
                        console.error('Error deleting video:', error);
                    }
                });
            }
        });
    }

    openNewsUrl(url: string | null): void {
        if (url) {
            window.open(url, '_blank');
        }
    }

    openCreateVideoDialog(): void {
        const dialogRef = this.dialog.open(CreateVideoDialogComponent, {
            width: '400px'
        });

        dialogRef.afterClosed().subscribe((result: string | undefined) => {
            if (result) {
                this.videoService.createVideo(result).subscribe({
                    next: (video) => {
                        this.snackbarService.show('Video created successfully', 'success');
                        this.loadVideos();
                    },
                    error: (error) => {
                        this.snackbarService.show('Failed to create video', 'error');
                        console.error('Error creating video:', error);
                    }
                });
            }
        });
    }
}