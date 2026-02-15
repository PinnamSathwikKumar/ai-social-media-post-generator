⚠️ Important Note for Reviewers (API Quota)

Due to OpenAI free trial limitations, the AI generation feature may return the following error:

429 - insufficient_quota

1.This occurs when the free trial API tokens have been exhausted.

2.If you encounter this issue while testing the project, please follow these steps:

3.Create your own OpenAI account (if you don’t already have one).

4.Generate a new API key from the OpenAI dashboard.

5.Copy the provided .env.example file.

6.Rename it to .env.

Add your credentials, including your OpenAI API key:

-----------------------------------------------------------------------------

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=social_media_generator

OPENAI_API_KEY=your_openai_api_key_here

FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

-----------------------------------------------------------------------------

Restart the application:

python app.py

Once a valid API key with available quota is provided, the AI-powered post generation feature will function normally.

If no API key is provided, the system will automatically use the built-in fallback generator to ensure the application remains functional.