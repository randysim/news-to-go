# news-to-go

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-green)](https://www.djangoproject.com/)
[![Angular](https://img.shields.io/badge/Angular-16%2B-red)](https://angular.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Latest-orange)](https://ollama.ai/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/randysim/news-to-go/pulls)

A fullstack application built using Angular, Django/rest-framework, and Ollama. Converts any news article into a short form video! 

Instructions to run the frontend and backend are in the respective directories.

[![DEMO VIDEO](https://img.youtube.com/vi/fRwPuwTgrfM/0.jpg)](https://www.youtube.com/watch?v=fRwPuwTgrfM)
[DEMO VIDEO](https://www.youtube.com/watch?v=fRwPuwTgrfM)

## Usage

1) User creates an account and signs up
2) User creates a video

3) User inputs a url to a news source

4) Scrapes the content and the user can click next

5) Generates the script, and the user can click next or regenerate (client triggers a job and long polls using job id for response)

6) Then, the user can type out keywords for each sentence

7) The user can then click generate video, the video will be stored on the server where they can retrieve it.
