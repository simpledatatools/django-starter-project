
# Django Starter Project Web App

## To Run the App

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the application using either:
   ```bash
   daphne -p 8000 core.asgi:application
   ```
   or
   ```bash
   python3 manage.py runserver
   ```
   in one terminal.

3. Start the Celery worker in another terminal:
   ```bash
   celery -A core worker -l info
   ```

4. Ensure you have `redis-server` running locally.