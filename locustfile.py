from locust import HttpUser, task, between

class TodoUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        # Login before starting tasks
        self.client.post("/login/", {
            "username": "testuser",
            "password": "testpass"
        })

    @task(2)
    def view_task_list(self):
        self.client.get("/task_list/")

    @task(1)
    def create_task(self):
        self.client.post("/task_create/", {
            "title": "Load Test Task",
            "description": "Task created during load testing",
            "priority": "Medium",
            "category": "1",  # Adjust category ID as needed
            "recurrence": "none"
        })

    @task(1)
    def update_task(self):
        # Assuming task with ID 1 exists for update
        self.client.post("/task_update/1/", {
            "title": "Updated Load Test Task",
            "description": "Updated during load testing",
            "priority": "High",
            "category": "1",
            "recurrence": "none"
        })
