# news-to-go

A fullstack application built using Angular, Django/rest-framework, and Ollama. Converts any news article into a short form video!

Instructions to run the frontend and backend are in the respective directories.

## Usage

1) User creates an account and signs up
2) User creates a video

3) User inputs a url to a news source

4) Scrapes the content and the user can click next

5) Generates the script, and the user can click next or regenerate (client triggers a job and long polls using job id for response)

6) Then, the user can type out keywords for each sentence

7) The user can then click generate video, the video will be stored on the server where they can retrieve it.