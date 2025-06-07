# ToDoListTask Project

## Setup Instructions for Running on Another Device

To run this Django project on a new device, follow these steps:

1. **Clone the repository**  
   ```bash
   git clone <repository-url>
   cd TodoListTask-main
   ```

2. **Create and activate a virtual environment**  
   On Windows:  
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```  
   On macOS/Linux:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Redis server**  
   This project uses Redis for Django Channels and Celery.  
   - Install Redis on your machine.  
   - Start the Redis server on the default port 6379.  
   For Windows, you can use [Microsoft's Redis port](https://github.com/microsoftarchive/redis/releases) or run Redis via WSL.

5. **Apply database migrations**  
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**  
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**  
   ```bash
   python manage.py runserver
   ```

8. **Run Celery worker (optional, if using Celery tasks)**  
   ```bash
   celery -A todo worker -l info
   ```

9. **Run Celery beat scheduler (optional)**  
   ```bash
   celery -A todo beat -l info
   ```

## Notes

- Ensure Redis is running before starting the Django development server to avoid connection errors.
- Email settings are configured for Gmail SMTP; update credentials in `todo/settings.py` as needed.
- Real-time notifications require Django Channels and Redis.

This README provides the essential steps to get the project running on a new device.
"# ToDoList-Latest-Version" 
"# Latest_Version_Code" 
