import unittest
import requests
import json
import time
import random
import string
import psutil
import pandas as pd

ENDPOINT = "http://localhost:4567/"

class APITester(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = requests.Session()
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
    
    def generate_random_object_data(self):
        random_data = {
            "title": self.generate_random_string(10),
            "description": self.generate_random_string(20)
        }
        return random_data

    def generate_dict(self, objnum, interval):
        data_dict = {
            'Objects Number': [i for i in range(0, objnum+1, interval)],
            'Sample Time for Add (s)': [],
            'Sample Time for Change (s)': [],
            'Sample Time for Delete (s)': [],
            'Transaction Time for Add (s)': [],
            'Transaction Time for Change (s)': [],
            'Transaction Time for Delete (s)': [],
            'CPU % Use for Add': [],
            'CPU % Use for Change': [],
            'CPU % Use for Delete': [],
            'Available Free Memory for Add (MB)': [],
            'Available Free Memory for Change (MB)': [],
            'Available Free Memory for Delete (MB)': []
        }
        return data_dict
    
    def test_dynamic_category(self):
        num_objects = 10000 # Number of objects to delete
        interval = 500
        data_dict = self.generate_dict(num_objects, interval)
        id_range = []
        total_time = [0]
        #create dictionary: numobj, optime, %cpu, availablemem
        #use psutil for %cpu and avlmem
        #create df
        #create csv
        for i in range(num_objects + 1):
            random_data = self.generate_random_object_data()
            start_time = time.time()
            response = self.client.post(ENDPOINT + 'categories', data=json.dumps(random_data))
            end_time = time.time()
            sample_time = end_time - start_time
            total_time.append(sample_time)
            if i % interval == 0:
                data_dict['Sample Time for Add (s)'].append(sample_time)
                data_dict['Transaction Time for Add (s)'].append(sum(total_time))
                cpu = psutil.cpu_percent()
                data_dict['CPU % Use for Add'].append(cpu)
                mem = psutil.virtual_memory()
                mem_mb = mem.available / (1024 ** 2)
                data_dict['Available Free Memory for Add (MB)'].append(mem_mb)
            if i == 0 or i == num_objects:
                id_range.append(int(json.loads(self.get_response_entity(response))['id']))

        numbers_list = list(range(id_range[0], id_range[1] + 1))
        random.shuffle(numbers_list)
        total_time = []
        count = 0

        for random_id in random.sample(numbers_list, num_objects+1):
        #for random_id in numbers_list:
            updated_data = self.generate_random_object_data()
            start_time = time.time()
            response = self.client.put(ENDPOINT + f'categories/{random_id}', data=json.dumps(updated_data))
            end_time = time.time()
            sample_time = end_time - start_time
            total_time.append(sample_time)
            if count % interval == 0:
                data_dict['Sample Time for Change (s)'].append(sample_time)
                data_dict['Transaction Time for Change (s)'].append(sum(total_time))
                cpu = psutil.cpu_percent()
                data_dict['CPU % Use for Change'].append(cpu)
                mem = psutil.virtual_memory()
                mem_mb = mem.available / (1024 ** 2)
                data_dict['Available Free Memory for Change (MB)'].append(mem_mb)
            count += 1
        total_time = []
        count = 0
        for random_id in random.sample(numbers_list, num_objects+1):
        #for random_id in numbers_list:
            start_time = time.time()
            response = self.client.delete(ENDPOINT + f'categories/{random_id}')
            end_time = time.time()
            sample_time = end_time - start_time
            total_time.append(sample_time)
            if count % interval == 0:
                sample_time = end_time - start_time
                data_dict['Sample Time for Delete (s)'].append(sample_time)
                data_dict['Transaction Time for Delete (s)'].append(sum(total_time))
                cpu = psutil.cpu_percent()
                data_dict['CPU % Use for Delete'].append(cpu)
                mem = psutil.virtual_memory()
                mem_mb = mem.available / (1024 ** 2)
                data_dict['Available Free Memory for Delete (MB)'].append(mem_mb)
            count += 1
        df = pd.DataFrame.from_dict(data_dict)
        df.to_csv('category.csv', index=False)
        
        #average_time = sum(operation_times) / len(operation_times)
        #print(f"Average time taken to create {num_objects} objects:", average_time, "seconds")

if __name__ == '__main__':
    unittest.main()
