

# Automated Meeting Notes and Task Managment

## Overview

### System operating modes:

 -  Real-time Meeting Transcription using Whisper model for live audio processing
 - Post-meeting Audio Analysis for recorded meetings using BART model

Integrates Gemini API for task extraction and Trello for task management.

## Features
1. **Real-time Transcription**
  - Live audio capture and processing
  - Whisper model integration for accurate transcription

2. **Audio File Processing**
  - Support for pre-recorded meeting uploads
  - Complete transcript generation
  - Meeting summary creation

3. **Intelligent Summarization**
  - BART model implementation
  - Key discussion point extraction
  - Concise meeting summary generation

4. **Task Automation**
  - Gemini API integration for task identification
  - Automatic date extraction
  - Direct Trello task creation
  - Schedule management

5. **Content Organization**
  - Topic-based section breakdown
  - YouTube-style navigation system
  - Meeting summary publication
  - Integrated Trello updates

6. **User Interface**
  - Streamlit-based frontend
  - Intuitive transcription management
  - Summary generation controls

## Tech Stack
- Whisper Model (Live Transcription)
- BART Model (Summarization)
- Gemini API (Task Processing)
- Trello API (Task Management)

### Development
- Streamlit (Frontend)
- Python (Backend)

# Future Enhancements

- Integration with other task management tools like Asana and Notion.
- Support for multilingual transcription and summarization.
- Enhanced NLP models for more accurate task extraction.
- UI/UX dashboard for easier user interactions.
- To build a Chrome extension version of this application.
