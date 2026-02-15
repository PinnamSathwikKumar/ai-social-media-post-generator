# AI Social Media Post Generator

An AI-powered application that automatically generates social media posts for events. Create events, generate platform-specific content with different tones, and manage your social media content all in one place.

# IMPORTANT

⚠ Requires MySQL Server to be installed and running locally.


## Features

- **Event Management**: Create, view, and delete events with details like title, date, location, type, and description
- **AI-Powered Post Generation**: Automatically generate social media captions using AI
- **Multi-Platform Support**: Generate posts optimized for LinkedIn, Instagram, Facebook, and Twitter
- **Tone Customization**: Choose from formal, professional, promotional, or friendly tones
- **Post Management**: Track post status (draft, approved, posted) and manage generated content
- **Beautiful UI**: Modern glassmorphism design with Bootstrap

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **AI Engine**: OpenAI GPT-3.5 (with fallback generator)
- **Frontend**: HTML, CSS, Bootstrap (Glassmorphism UI)

## Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- OpenAI API Key (optional, for AI generation)

## Installation

1. **Clone or download the project**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL Database**
   - Create a MySQL database (or the application will create it automatically)
   - Note the database credentials (host, user, password, database name)

4. **Configure Environment Variables**
   - Copy `.env.example` to `.env`
   - Edit `.env` and fill in your configuration:
     ```
     DB_HOST=localhost
     DB_USER=root
     DB_PASSWORD=your_mysql_password
     DB_NAME=social_media_generator
     
     OPENAI_API_KEY=your_openai_api_key_here
     
     FLASK_ENV=development
     FLASK_DEBUG=True
     SECRET_KEY=your_secret_key_here
     ```
5. **Run the Application**
   ```bash
   python app.py
   ```
6. **Access the Application**
   - Open your browser and navigate to `http://localhost:5000`

## Usage

### Creating Events

1. Go to the **Events** tab
2. Fill in the event details:
   - Event Title (required)
   - Event Date (required)
   - Location (optional)
   - Event Type (optional)
   - Description (optional)
3. Click **Save Event**

### Generating Posts

1. Go to the **Generate Posts** tab
2. Select an event from the dropdown
3. Choose the target platform (LinkedIn, Instagram, Facebook, or Twitter)
4. Select the desired tone (Formal, Professional, Promotional, or Friendly)
5. Click **Generate Post**
6. Review the generated content and hashtags
7. Click **Approve** to save the post, or **Regenerate** to create a new version

### Managing Posts

1. Go to the **View Posts** tab
2. Filter posts by event (optional)
3. View all generated posts with their status
4. Update post status:
   - **Approve**: Move from draft to approved
   - **Mark as Posted**: Move from approved to posted
5. Delete posts you no longer need

## API Endpoints

### Events
- `GET /api/events` - Get all events
- `POST /api/events` - Create a new event
- `GET /api/events/<id>` - Get a specific event
- `PUT /api/events/<id>` - Update an event
- `DELETE /api/events/<id>` - Delete an event

### Posts
- `POST /api/generate-post` - Generate a new post
- `GET /api/posts` - Get all posts (optional: `?event_id=<id>`)
- `PUT /api/posts/<id>` - Update post status
- `DELETE /api/posts/<id>` - Delete a post

## Database Schema

### Events Table
- `id` (INT, Primary Key)
- `title` (VARCHAR)
- `date` (DATE)
- `location` (VARCHAR)
- `type` (VARCHAR)
- `description` (TEXT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Generated Posts Table
- `id` (INT, Primary Key)
- `event_id` (INT, Foreign Key)
- `platform` (VARCHAR)
- `tone` (VARCHAR)
- `content` (TEXT)
- `hashtags` (TEXT)
- `status` (VARCHAR: draft/approved/posted)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## AI Generation

The application uses OpenAI's GPT-3.5 model for content generation. If an API key is not provided, it falls back to a template-based generator that still creates platform-appropriate content.

### Platform-Specific Guidelines
- **LinkedIn**: Professional tone, business-focused, 1300 characters max
- **Instagram**: Visual and engaging, emojis, 2200 characters max, 5-10 hashtags
- **Facebook**: Conversational, community-focused, 5000 characters max
- **Twitter**: Concise, 280 characters max, 1-3 hashtags

## Troubleshooting

### Database Connection Issues
- Ensure MySQL server is running
- Verify database credentials in `.env`
- Check if the database exists (it will be created automatically if it doesn't)

### AI Generation Not Working
- Verify your OpenAI API key is correct
- Check your API quota/balance
- The application will use a fallback generator if the API is unavailable

### Port Already in Use
- Change the port in `app.py` (last line)
- Or stop the process using port 5000


## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

