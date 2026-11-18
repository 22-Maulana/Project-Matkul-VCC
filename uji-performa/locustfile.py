from locust import HttpUser, task, between
class APIUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def uji_api(self):
        self.client.get("/berat")
