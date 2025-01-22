import unittest
import requests
import json
import time
import random
import string
import psutil

ENDPOINT = "http://localhost:4567/"

class APITester(unittest.TestCase):
    number_of_objects = 2
    created_ids = [1, 2]
    client = requests.Session()
    POST_transaction_time = 0.0
    PUT_transaction_time = 0.0
    DELETE_transaction_time = 0.0

    @classmethod
    def setUpClass(cls):
        #cls.client = requests.Session()
        cls.connection = None
    
    @classmethod
    def tearDownClass(cls):
        if cls.connection:
            cls.connection.close()
    
    def setUp(self):
        try:
            self.connection = requests.get(ENDPOINT)
            self.assertEqual(200, self.connection.status_code)
        except Exception as err:
            print("Failure to connect")
            print("Please try to start a new session")
            print(err)
    
    @staticmethod
    def tearDown():
        pass
    
    def get_response_entity(self, response):
        return response.text
    
    def get_status(self, response):
        return response.status_code
    
    def get_json_object(self, response_entity, type):
        response_json = json.loads(response_entity)
        todos_list = response_json[type]
        todo = todos_list[0]
        return todo
    
    def add_parameters(self, request, json_data):
        request.headers['Content-Type'] = 'application/json'
        request.data = json.dumps(json_data)
        return request
    
    def generate_random_string(self, length):
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    def generate_random_boolean(self):
        return random.choice([True, False])
    
    def generate_random_todos_data(self):
        random_data = {
            "title": self.generate_random_string(10),
            "doneStatus": self.generate_random_boolean(),
            "description": self.generate_random_string(20)
        }
        return random_data

    def record_cpu_memory_usage(self):
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # Convert bytes to megabytes
        return f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage:.2f} MB"
    
    def create_todos_with_random_data(self):
        random_data = self.generate_random_todos_data()
        # To count sample time
        start_time = time.perf_counter()
        # send request
        response = self.client.post(ENDPOINT + 'todos', data=json.dumps(random_data))
        end_time = time.perf_counter()
        # Record Mem and CPU use
        usage = self.record_cpu_memory_usage()
        sample_time = end_time - start_time
        # Keep track of many objects (todos)
        self.number_of_objects += 1
        # Calculating total transaction time
        self.POST_transaction_time += sample_time
        
        if self.number_of_objects % 500 == 0:
            print(f"{self.number_of_objects} todos - ADD todos")
            print("Sample time: ", sample_time, " Transaction_time: ", self.POST_transaction_time)
            print(usage)
        
        # Keep track of all the generated ids, for later PUT & DELETE use
        id = json.loads(self.get_response_entity(response))['id']
        self.created_ids.append(id)
        
    def update_todos_with_random_data(self):
        random_id = random.choice(self.created_ids)
        updated_data = self.generate_random_todos_data()
        start_time = time.perf_counter()
        response = self.client.put(ENDPOINT + f'todos/{random_id}', data=json.dumps(updated_data))
        end_time = time.perf_counter()
        usage = self.record_cpu_memory_usage()
        sample_time = end_time - start_time
        self.PUT_transaction_time += sample_time
        if self.number_of_objects % 500 == 0:
            print(f"{self.number_of_objects} todos - EDIT todos")
            print("Sample time: ", sample_time, " Transaction_time: ", self.PUT_transaction_time)
            print(usage)
            
        
    def delete_random_todos(self):
        start_time = time.perf_counter()
        random_id = random.choice(self.created_ids)
        response = self.client.delete(ENDPOINT + f'todos/{random_id}')
        end_time = time.perf_counter()
        usage = self.record_cpu_memory_usage()
        sample_time = end_time - start_time
        self.DELETE_transaction_time += sample_time
        
        if self.number_of_objects % 500 == 0:
            print(f"{self.number_of_objects} todos - DELETE todos")
            print("Sample time: ", sample_time, " Transaction_time: ", self.DELETE_transaction_time)
            print(usage)
            
        # Delete random_id from created ids
        self.created_ids.remove(random_id)
        # One less object 
        self.number_of_objects -= 1

        
if __name__ == '__main__':
    tester = APITester()
    for i in range(10000):
        tester.create_todos_with_random_data()
        tester.update_todos_with_random_data()
    
    for i in range(10000):
        tester.delete_random_todos()

    
