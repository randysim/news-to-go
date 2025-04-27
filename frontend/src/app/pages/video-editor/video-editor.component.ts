import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { VideoService, Video } from '../../services/video.service';
import { interval, Subscription } from 'rxjs';
import { switchMap, takeWhile } from 'rxjs/operators';
import { SnackbarService } from '../../services/snackbar.service';

import { Job, JobDTO } from '../../services/video.service';

@Component({
  selector: 'app-video-editor',
  templateUrl: './video-editor.component.html',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule]
})
export class VideoEditorComponent implements OnInit, OnDestroy {
  video: Video | null = null;
  loading = true;
  error: string | null = null;
  currentStep = 1;
  totalSteps = 4;
  pendingJob = false;
  pendingJobType: 'SCRAPE' | 'SCRIPT' | 'VIDEO' | undefined = undefined;
  jobPollingSubscription: Subscription | null = null;
  newsUrl = '';
  news_content = '';
  script = '';
  config = '';
  videoGenerated = false;
  videoUrl: string | null = null;
  invalidIndices: string[] = [];
  configValid = false;
  configCards: any[] = [];
  selectedType: 'keyword' | 'image' | 'video' = 'keyword';
  keywordInput = '';
  mediaUrl = '';
  keywordErrors: { [key: number]: string } = {};

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private videoService: VideoService,
    private snackbarService: SnackbarService
  ) {}

  ngOnInit(): void {
    const videoId = this.route.snapshot.paramMap.get('id');
    if (!videoId) {
      this.router.navigate(['/dashboard']);
      return;
    }

    this.loadVideo(parseInt(videoId));
  }

  ngOnDestroy(): void {
    if (this.jobPollingSubscription) {
      this.jobPollingSubscription.unsubscribe();
    }
    if (this.videoUrl) {
      URL.revokeObjectURL(this.videoUrl);
    }
  }

  private loadVideo(id: number): void {
    this.loading = true;
    this.error = null;

    this.videoService.getVideo(id).subscribe({
      next: (video) => {
        this.video = video;
        this.newsUrl = video.news_url || '';
        this.script = video.script || '';
        this.news_content = video.news_content || '';
        this.config = video.config || '';
        this.videoGenerated = video.video_generated || false;
        this.loading = false;
        this.checkPendingJob();
        this.updateCurrentStep();
        this.updateConfigCards();
        this.onConfigChange();
        if (this.videoGenerated) {
          this.loadVideoFile();
        }
      },
      error: (error) => {
        this.error = 'Failed to load video. Please try again later.';
        this.loading = false;
        console.error('Error loading video:', error);
      }
    });
  }

  private loadVideoFile(): void {
    if (!this.video) return;

    this.videoService.getVideoFile(this.video.id).subscribe({
      next: (blob) => {
        if (this.videoUrl) {
          URL.revokeObjectURL(this.videoUrl);
        }
        this.videoUrl = URL.createObjectURL(blob);
      },
      error: (error) => {
        console.error('Error loading video file:', error);
        this.error = 'Failed to load video file. Please try again later.';
      }
    });
  }

  private updateCurrentStep(): void {
    if (!this.video) return;

    // If there's a pending job, stay on the current step
    if (this.pendingJob) {
      if (this.pendingJobType === 'SCRAPE') {
        this.currentStep = 1;
      } else if (this.pendingJobType === 'SCRIPT') {
        this.currentStep = 2;
      } else if (this.pendingJobType === 'VIDEO') {
        this.currentStep = 4;
      }
      return;
    }

    // If video is already generated, go to step 4
    if (this.videoGenerated) {
      this.currentStep = 4;
      return;
    }

    // Step 1: Scrape Article - Check if news_content exists
    if (!this.video.news_content) {
      this.currentStep = 1;
      return;
    }

    // Step 2: Generate Script - Check if script exists
    if (!this.video.script) {
      this.currentStep = 2;
      return;
    }

    // Step 3: Configure - Check if config is valid
    try {
      const config = JSON.parse(this.video.config || '{}');
      const hasValidConfig = Object.entries(config).every(([index, value]: [string, any]) => {
        if (value.keyword_override) {
          return value.keyword_override.type && value.keyword_override.url;
        }
        return Array.isArray(value.keywords) && value.keywords.length > 0;
      });

      if (!hasValidConfig) {
        this.currentStep = 3;
        return;
      }
    } catch (e) {
      this.currentStep = 3;
      return;
    }

    // Step 4: Generate Video
    this.currentStep = 4;
  }

  private checkPendingJob(): void {
    if (!this.video) return;

    this.videoService.getJobStatus(this.video.id).subscribe({
      next: (job) => {
        this.pendingJob = job.job.status !== 'FINISHED';
        this.pendingJobType = job.job.job_type;
        
        if (this.pendingJob) {
          this.startJobPolling();
        } else {
          // If job is finished, make sure to stop polling
          if (this.jobPollingSubscription) {
            this.jobPollingSubscription.unsubscribe();
            this.jobPollingSubscription = null;
          }
          this.pendingJobType = undefined;
        }
      },
      error: (error) => {
        console.error('Error checking job status:', error);
        this.pendingJob = false;
        this.pendingJobType = undefined;
        if (this.jobPollingSubscription) {
          this.jobPollingSubscription.unsubscribe();
          this.jobPollingSubscription = null;
        }
      }
    });
  }

  private startJobPolling(): void {
    if (!this.video || this.jobPollingSubscription) return;

    this.jobPollingSubscription = interval(5000).pipe(
      takeWhile(() => this.pendingJob),
      switchMap(() => this.videoService.getJobStatus(this.video!.id))
    ).subscribe({
      next: (job) => {
        if (job.job.status === 'FINISHED') {
          this.pendingJob = false;
          this.pendingJobType = undefined;
          this.jobPollingSubscription?.unsubscribe();
          this.jobPollingSubscription = null;
          this.loadVideo(this.video!.id);
          this.snackbarService.show('Job completed successfully!', 'success');
        }
      },
      error: (error) => {
        console.error('Error polling job status:', error);
        this.pendingJob = false;
        this.pendingJobType = undefined;
        this.jobPollingSubscription?.unsubscribe();
        this.jobPollingSubscription = null;
      }
    });
  }

  onScrape(): void {
    if (!this.video || !this.newsUrl) return;

    this.pendingJob = true;
    this.pendingJobType = 'SCRAPE';
    this.videoService.createJob(this.video.id, {
      job_type: 'SCRAPE',
      url: this.newsUrl
    }).subscribe({
      next: () => {
        this.startJobPolling();
      },
      error: (error) => {
        this.pendingJob = false;
        this.pendingJobType = undefined;
        this.error = 'Failed to start scraping job. Please try again.';
        console.error('Error starting scrape job:', error);
      }
    });
  }

  onGenerateScript(): void {
    if (!this.video) return;

    this.pendingJob = true;
    this.pendingJobType = 'SCRIPT';
    this.videoService.createJob(this.video.id, {
      job_type: 'SCRIPT'
    }).subscribe({
      next: () => {
        this.startJobPolling();
      },
      error: (error) => {
        this.pendingJob = false;
        this.pendingJobType = undefined;
        this.error = 'Failed to start script generation. Please try again.';
        console.error('Error starting script job:', error);
      }
    });
  }

  onConfigChange(): void {
    this.configValid = this.isConfigValid();
  }

  isConfigValid(): boolean {
    if (!this.config) return false;
    
    try {
      const config = JSON.parse(this.config);
      this.invalidIndices = [];
      
      // Check if the config has the required structure
      if (!config.keywords || !Array.isArray(config.keywords)) {
        this.invalidIndices.push('Missing or invalid keywords array');
        return false;
      }

      // Check each keyword entry
      config.keywords.forEach((entry: any) => {
        if (!Array.isArray(entry.keyword) || !entry.keyword.some((k: string) => k && k.trim() !== '')) {
          this.invalidIndices.push(`index ${entry.idx}`);
        }
      });
      
      // Check if there are any keyword errors
      if (Object.values(this.keywordErrors).some(error => error !== '')) {
        return false;
      }
      
      return this.invalidIndices.length === 0;
    } catch (e) {
      this.invalidIndices = ['Invalid JSON'];
      return false;
    }
  }

  onSaveConfig(): void {
    if (!this.video || !this.configValid) return;

    this.videoService.updateVideo(this.video.id, {
      config: this.config
    }).subscribe({
      next: () => {
        this.snackbarService.show('Config saved successfully!', 'success');
      },
      error: (error) => {
        this.error = 'Failed to save config. Please try again.';
        console.error('Error saving config:', error);
        this.snackbarService.show('Failed to save config. Please try again.', 'error');
      }
    });
  }

  onGenerateVideo(): void {
    if (!this.video) return;

    this.pendingJob = true;
    this.pendingJobType = 'VIDEO';
    this.videoService.createJob(this.video.id, {
      job_type: 'VIDEO'
    }).subscribe({
      next: () => {
        this.startJobPolling();
      },
      error: (error) => {
        this.pendingJob = false;
        this.pendingJobType = undefined;
        this.error = 'Failed to start video generation. Please try again.';
        console.error('Error starting video job:', error);
      }
    });
  }

  nextStep(): void {
    if (this.currentStep < this.totalSteps && this.isCurrentStepComplete()) {
      this.currentStep++;
    }
  }

  previousStep(): void {
    if (this.currentStep > 1) {
      this.currentStep--;
    }
  }

  isCurrentStepComplete(): boolean {
    if (!this.video) return false;

    switch (this.currentStep) {
      case 1: // Scrape Article
        return !!this.video.news_content;
      case 2: // Generate Script
        return !!this.video.script;
      case 3: // Configure
        return this.configValid;
      case 4: // Generate Video
        return true; // Always allow going to video generation
      default:
        return false;
    }
  }

  isStepComplete(step: number): boolean {
    if (!this.video) return false;

    switch (step) {
      case 0: // Scrape Article
        return true;
      case 1: // Scrape Article
        return !!this.news_content;
      case 2: // Generate Script
        return !!this.script;
      case 3: // Configure
        return this.isConfigValid();
      case 4: // Generate Video
        return this.videoGenerated;
      default:
        return false;
    }
  }

  private updateConfigCards(): void {
    if (!this.video?.news_content) return;

    try {
      const config = JSON.parse(this.config || '{}');
      const keywords = config.keywords || [];
      
      this.configCards = keywords.map((keywordConfig: any) => {
        return {
          index: parseInt(keywordConfig.idx) + 1,
          fragment: keywordConfig.fragment,
          config: keywordConfig,
          inputValue: keywordConfig.keyword.join(' ')
        };
      });
    } catch (e) {
      console.error('Error parsing config:', e);
      this.configCards = [];
    }
  }

  onKeywordChange(cardIndex: number, keyword: string): void {
    const card = this.configCards[cardIndex];
    const words = keyword.trim().split(/\s+/);
    
    if (words.length > 2) {
      this.keywordErrors[cardIndex] = 'Maximum 2 words allowed';
      // Only take the first two words
      words.splice(2);
      card.inputValue = words.join(' ');
    } else {
      this.keywordErrors[cardIndex] = '';
      card.inputValue = keyword;
    }
    
    this.updateConfigFromCards();
  }

  private updateConfigFromCards(): void {
    const config: any = {
      keywords: [],
      keyword_image_overrides: {}
    };

    this.configCards.forEach(card => {
      const idx = (card.index - 1).toString();
      const words = card.inputValue.trim().split(/\s+/);
      config.keywords.push({
        idx,
        keyword: [words[0] || '', words[1] || ''],
        fragment: card.fragment
      });
      
      // Maintain any existing overrides
      if (this.video?.config) {
        try {
          const existingConfig = JSON.parse(this.video.config);
          if (existingConfig.keyword_image_overrides?.[idx]) {
            config.keyword_image_overrides[idx] = existingConfig.keyword_image_overrides[idx];
          }
        } catch (e) {
          console.error('Error parsing existing config:', e);
        }
      }
    });

    this.config = JSON.stringify(config, null, 2);
    this.onConfigChange();
  }

  getScriptSection(section: 'HOOK' | 'BODY' | 'OUTRO'): string {
    if (!this.script) return '';
    
    const regex = new RegExp(`<${section}>(.*?)</${section}>`, 's');
    const match = this.script.match(regex);
    return match ? match[1].trim() : '';
  }
} 