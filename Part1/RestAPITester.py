import unittest
import requests
import json
import random

ENDPOINT = "http://localhost:4567/"

# Random Order Helper
class RandomTestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testCaseClass):
        test_names = super().getTestCaseNames(testCaseClass)
        random.shuffle(test_names)
        return test_names

class APITester(unittest.TestCase):
    # Initialization
    @classmethod
    def setUpClass(cls):
        cls.client = requests.Session()
        cls.connection = None
        print("--- TODOS TEST STARTS --- ")
    
    @classmethod
    def tearDownClass(cls):
        if cls.connection :
            cls.connection.close()
            requests.get(ENDPOINT+"shutdown")
            
    def setUp(self):
        try :
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
    
    ##############################
    
    # Todos

    # Test 1: GET /todos 
    def test_todos_get(self):
        response = self.client.get(ENDPOINT+'todos')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        self.assertTrue(2 <= len(json.loads(self.get_response_entity(response))['todos'])) 
        
    # Test 2: HEAD /todos 
    def test_todos_head(self):
        response = self.client.head(ENDPOINT+'todos')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        #Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)
        
    # Test 3: POST /todos using JSON 
    def test_todos_post_JSON(self):
        test_input = {
            'title': "Watch 409 recording",
            'doneStatus': False,
            'description': "watch thursday recording"
            }
        
        response = self.client.post(ENDPOINT+'todos', json = test_input)
        self.assertEqual(self.get_status(response), 201) # Check the status code
        output = json.loads(self.get_response_entity(response))
        # Check if the output JSON has the same properties + an id
        self.assertTrue(4 == len(output))
        self.assertTrue('id' in output)
        self.assertEqual(output['title'], test_input['title'])
        self.assertEqual(output['description'], test_input['description'])
        doneStatus = output['doneStatus'] == 'true'
        self.assertEqual(doneStatus, test_input['doneStatus'])
        
    # Test 4: POST /todos using XML (included id -> FAILURE)
    def test_todos_post_XML(self):
        # According to documentation, XML should look like that, but we get an error 
        xml_input = """ 
        <todo>
            <doneStatus>false</doneStatus>
            <description>Do laundry before 3pm</description>
            <id>null</id>
            <title>Laundry</title>
        </todo>
        """
        
        xml_headers = {"Content-Type": "application/xml"}
        
        response = self.client.post(ENDPOINT+'todos', headers=xml_headers, data=xml_input)
        # Check bad requests status code
        self.assertEqual(self.get_status(response), 400) 
        # Check if there is an errorMessage 
        self.assertTrue('errorMessages' in json.loads(self.get_response_entity(response)))
        
    # Test 5: POST /todos using XML 
    def test_todos_post_XML(self):
        xml_input = """ 
        <todo>
            <doneStatus>false</doneStatus>
            <description>Do laundry before 3pm</description>
            <title>Laundry</title>
        </todo>
        """
        
        xml_headers = {"Content-Type": "application/xml"}
        
        response = self.client.post(ENDPOINT+'todos', headers=xml_headers, data=xml_input)
        self.assertEqual(self.get_status(response), 201) # Check the status code
        output = json.loads(self.get_response_entity(response))
        # Check if the output JSON has the same properties + an id
        self.assertTrue(4 == len(output))
        self.assertTrue('id' in output)
        self.assertEqual(output['title'], "Laundry")        
        self.assertEqual(output['doneStatus'], "false")
        self.assertEqual(output['description'], "Do laundry before 3pm")
        
    ############################
    
    # Test 6: GET /todos/:id 
    def test_todos_id_get(self):
        response = self.client.get(ENDPOINT+'todos/1')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        output = json.loads(self.get_response_entity(response))['todos'][0]
        self.assertTrue(4 <= len(output)) 
        # Check if the returned todo has the wanted id
        self.assertEqual('1', output['id'])
        
    # Test 7: GET /todos/:id (non existing id -> failure)
    def test_todos_wrong_id_get(self):
        response = self.client.get(ENDPOINT+'todos/101')
        self.assertEqual(self.get_status(response), 404) # Check the status code
        # Check if there is an errorMessage 
        self.assertTrue('errorMessages' in json.loads(self.get_response_entity(response)))
    
    # Test 8: HEAD /todos/:id
    def test_todos_head(self):
        response = self.client.head(ENDPOINT+'todos/1')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        #Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)
    
    # Test 9: Post /todos/:id using JSON
    def test_todos_post_id_JSON(self):
        test_input = {
            'title': "Post this task",
            'doneStatus': True,
            'description': "Amend todo with POST"
            }
        
        response = self.client.post(ENDPOINT+'todos/1', json = test_input)
        self.assertEqual(self.get_status(response), 200) # Check the status code
        output = json.loads(self.get_response_entity(response))
        # Check if the output JSON has the same properties + an id
        self.assertTrue(4 <= len(output))
        self.assertEqual(output['id'], '1') # Check that the id did not change
        self.assertEqual(output['title'], test_input['title'])
        self.assertEqual(output['description'], test_input['description'])
        doneStatus = output['doneStatus'] == 'true'
        self.assertEqual(doneStatus, test_input['doneStatus'])
        
    # Test 10: PUT /todos/:id using JSON
    def test_todos_put_id_JSON(self):
        test_input = {
            'title': "Updating todo 1",
            'doneStatus': True,
            'description': "Change the field of todo 1"
            }
        
        response = self.client.put(ENDPOINT+'todos/1', json = test_input)
        self.assertEqual(self.get_status(response), 200) # Check the status code
        output = json.loads(self.get_response_entity(response))
        # Check if the output JSON has the same properties + an id
        self.assertTrue(4 <= len(output))
        self.assertEqual(output['id'], '1') # Check that the id did not change
        self.assertEqual(output['title'], test_input['title'])
        self.assertEqual(output['description'], test_input['description'])
        doneStatus = output['doneStatus'] == 'true'
        self.assertEqual(doneStatus, test_input['doneStatus'])
        
    # Test 11: PUT /todos/:id using JSON (Undocumented behavior)
    # Undocumented behavior: PUT can update tasks field of a project
    def test_todos_put_id_tasks(self):
        # Add a project-todo relation 
        xml_input = """ 
        <project>
            <active>true</active>
            <description>429 Project part 1</description>
            <completed>false</completed>
            <title>429 Project</title>
        </project>
        """
        
        xml_headers = {"Content-Type": "application/xml"}
        
        response_post = self.client.post(ENDPOINT+'todos/1/tasksof', headers=xml_headers, data=xml_input)
        self.assertEqual(self.get_status(response_post), 201) # Check the status code
        response_get = self.client.get(ENDPOINT+'todos/1')
        self.assertEqual(self.get_status(response_get), 200) # Check the status code
        get_output = json.loads(self.get_response_entity(response_get))['todos'][0]
        self.assertTrue('tasksof' in get_output) #check projects had being added to todo

        # Update todo, where we change the tasks to empty   
        test_input = {
            'title': "Updating todo 1",
            'doneStatus': True,
            'description': "Change the field of todo 1",
            'tasks' : []
            }
        
        response = self.client.put(ENDPOINT+'todos/1', json = test_input)
        self.assertEqual(self.get_status(response), 200) # Check the status code
        output = json.loads(self.get_response_entity(response))
        # Make sure tasks had been deleted
        self.assertFalse('tasksof' in output)
        
    # Test 12: POST /todos/:id (Undocumented behavior)
    # Undocumented behavior: POST cannot update tasks field of a project
    def test_todos_post_tasks(self):
        # Add a project-todo relation 
        xml_input = """ 
        <project>
            <active>true</active>
            <description>429 Project part 1</description>
            <completed>false</completed>
            <title>429 Project</title>
        </project>
        """
        
        xml_headers = {"Content-Type": "application/xml"}
        
        response_post = self.client.post(ENDPOINT+'todos/1/tasksof', headers=xml_headers, data=xml_input)
        self.assertEqual(self.get_status(response_post), 201) # Check the status code
        response_get = self.client.get(ENDPOINT+'todos/1')
        self.assertEqual(self.get_status(response_get), 200) # Check the status code
        get_output = json.loads(self.get_response_entity(response_get))['todos'][0]
        self.assertTrue('tasksof' in get_output) #check projects had being added to todo

        # Update todo, where we change the tasks to empty
        test_input = {
            'title': "Updating todo 1",
            'doneStatus': True,
            'description': "Change the field of todo 1",
            'tasks' : []
            }
        
        response = self.client.post(ENDPOINT+'todos/1', json = test_input)
        self.assertEqual(self.get_status(response), 200) # Check the status code
        output = json.loads(self.get_response_entity(response))
        # Tasks still exist, POST does not update
        self.assertTrue('tasksof' in output)
        
    # Test 13: DELETE /todos using JSON
    def test_todos_delete_JSON(self):
        todo_data = {
            'title': "Delete this",
            'doneStatus': False,
            'description': "Create todo and delete it"
            }
        
        post_response = self.client.post(ENDPOINT+'todos', json = todo_data)
        self.assertEqual(self.get_status(post_response), 201) # Check the status code
        post_output = json.loads(self.get_response_entity(post_response))
        tid = post_output['id']
        
        response = self.client.delete(ENDPOINT+'todos/'+tid)
        status = self.get_status(response)
        self.assertTrue(status == 200 or status == 404)
        # Test deletion of an todo 
        if (status == 200) :
            output = self.get_response_entity(response)
            self.assertTrue(0 == len(output))
        # Test deletion of a todo which has already been deleted
        elif (status == 404) :
            self.assertTrue('errorMessages' in json.loads(self.get_response_entity(response)))
            
    ##########################
            
    # Test 14: GET /todos/:id/categories (SUCCESS)
    def test_todos_id_categories_get(self):
        response = self.client.get(ENDPOINT+'todos/1/categories')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        output = json.loads(self.get_response_entity(response))
        self.assertEqual(1, len(output))
        self.assertTrue("categories" in output)
        
    # Test 15: GET /todos/:id/categories (UNEXPECTED BEHAVIOR : - show actual behavior for Non-exisiting todo id)
    def test_todos_id_categories_get_fail1(self):
        # For testing, choose a random todo id
        # Delete the todo if it exists
        self.client.delete(ENDPOINT+'todos/100')
        
        response = self.client.get(ENDPOINT+'todos/100/categories')
        # If there is no errorMessage, means no error detected
        self.assertEqual(self.get_status(response), 404)
        if (self.get_status(response) != 400 or self.get_status(response) != 404) :
            print('Unexpected behaviour for Getting Categories for non-exisiting todo')
            output = json.loads(self.get_response_entity(response))['categories']
            print("The actual behavior: ")
            print(output)
            print("*******")
            
    # Test 16: GET /todos/:id/categories (UNEXPECTED BEHAVIOR : - show expected behavior faiiling for Non-exisiting todo id)
    def test_todos_id_categories_get_fail2(self):
        # For testing, choose a random todo id
        # Delete the todo if it exists
        self.client.delete(ENDPOINT+'todos/100')
        
        response = self.client.get(ENDPOINT+'todos/100/categories')
        return_code = self.get_status(response)
        self.assertEqual(self.get_status(response), 404)
        print('Unexpected behaviour for Getting Categories for non-exisiting todo')
        print("We should get an errorMessage that indicates the inexsitance of todo:id")
        print("The return body should be empty")
        print("*******")
        
            
    # Test 17: HEAD /todos/:id/categories
    def test_todos_head(self):
        response = self.client.head(ENDPOINT+'todos/1/categories')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        #Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)
        
    # Test 18: Post /todos/:id/categories using JSON
    def test_todos_id_cat_post_JSON(self):
        test_input = {
            "title": "School",
            "description": "Winter 2024"
        }
        
        response = self.client.post(ENDPOINT+'todos/1/categories', json = test_input)
        self.assertEqual(self.get_status(response), 201) # Check the status code
        output = json.loads(self.get_response_entity(response))
        self.assertTrue('id' in output) # Check if there is an id assigned to the task
        self.assertEqual(output['title'], test_input['title'])
        self.assertEqual(output['description'], test_input['description'])
          
    # Test 19: Post /todos/:id/categories (UNEXPECTED BEHAVIOR : - show expected behavior failling)
    def test_todos_id_cat_post_fail1(self):
        test_input = {
            "title": "Work out",
            "description": "Every Saturday"
        }
        
        response = self.client.post(ENDPOINT+'todos/1/categories', json = test_input)
        self.assertEqual(self.get_status(response), 201) # Check the status code
        output = json.loads(self.get_response_entity(response))
        cid = output['id'] #Get the generated id
        # Get the category with assigned id
        cat_response = self.client.get(ENDPOINT+'categories/'+cid+'/todos')
        self.assertEqual(self.get_status(cat_response), 200) # Check the status code
        cat_output = json.loads(self.get_response_entity(cat_response))
        
        # Failing of expected behavior
        self.assertTrue(len(cat_output['todos']) != 0)
        print('Unexpected behaviour for Posting a categories with todos/:id/categories')
        print("Expected result does not match actual result, the relationship is only created from Todo to Category, but not created from the Category to Todo")
        print('*********')
        
    # Test 20: Post /todos/:id/categories (UNEXPECTED BEHAVIOR :- show actual behavior)
    def test_todos_id_cat_post_fail2(self):
        test_input = {
            "title": "Work out",
            "description": "Every Saturday"
        }
        
        response = self.client.post(ENDPOINT+'todos/1/categories', json = test_input)
        self.assertEqual(self.get_status(response), 201) # Check the status code
        output = json.loads(self.get_response_entity(response))
        cid = output['id'] #Get the generated id
        # Get the category with the assigned id
        cat_response = self.client.get(ENDPOINT+'categories/'+cid+'/todos')
        self.assertEqual(self.get_status(cat_response), 200) # Check the status code
        cat_output = json.loads(self.get_response_entity(cat_response))
        
        get_response = self.client.get(ENDPOINT+'todos/1/categories')
        self.assertEqual(self.get_status(get_response), 200) # Check the status code
        get_output = json.loads(self.get_response_entity(get_response))
        
        print('*********')
        print('Unexpected behaviour for Posting a categories with todos/:id/categories')
        print("The relationship is only created from Todo to Category:")
        print(get_output['categories'])
        print("From the Category side, no relation: ")
        print(cat_output['todos'])
        print('*********')
        
    
    # Test 21: POST /todos/:id/categories (UNEXPECTED BEHAVIOR :- show expected behavior faiiling)
    def test_todos_id_cat_post_JSON_fail(self):
        todo_data = {
            'title': "Do dishes",
            'doneStatus': True,
            'description': ""
            }
        
        post_response = self.client.post(ENDPOINT+'todos', json = todo_data)
        self.assertEqual(self.get_status(post_response), 201) # Check the status code
        post_output = json.loads(self.get_response_entity(post_response))
        tid = post_output['id']
        
        test_input = {
            "id" : "1",
            "title": "New Cat",
            "description": "to replace Office"
        }
        
        cat_response = self.client.post(ENDPOINT+'todos/'+tid+'/categories', json = test_input)
        self.assertEqual(self.get_status(cat_response), 201) # Check the status code
        response = self.client.get(ENDPOINT+'todos/'+tid+'/categories')
        output = json.loads(self.get_response_entity(response))['categories'][0]
        self.assertEqual(output['id'], '1') # Check if the id is assigned 
        self.assertEqual(output['title'], test_input['title'])
        print('Unexpected behaviour for Posting a categories with todos/:id/categories')
        print("Expected result does not match actual result, the fields do not get updated")
        print('*********')
        
    # Test 22: POST /todos/:id/categories (UNEXPECTED BEHAVIOR :- show actual behavior)
    def test_todos_id_cat_post_JSON_actual_behavior(self):
        todo_data = {
            'title': "Do dishes",
            'doneStatus': True,
            'description': ""
            }
        
        post_response = self.client.post(ENDPOINT+'todos', json = todo_data)
        self.assertEqual(self.get_status(post_response), 201) # Check the status code
        post_output = json.loads(self.get_response_entity(post_response))
        tid = post_output['id']
        
        test_input = {
            "id" : "1",
            "title": "New Cat",
            "description": "to replace Office"
        }
        
        cat_response = self.client.post(ENDPOINT+'todos/'+tid+'/categories', json = test_input)
        self.assertEqual(self.get_status(cat_response), 201) # Check the status code
        response = self.client.get(ENDPOINT+'todos/'+tid+'/categories')
        output = json.loads(self.get_response_entity(response))['categories'][0]
        self.assertEqual(output['id'], '1') # Check if there is an id assigned to the task
        print('*********')
        print('Unexpected behaviour for Posting a categories with todos/:id/categories')
        print('Actual Output: ')
        print(output)
        print('*********')
        
    # Test 23: DELETE /todos/:id/categories/:id
    def test_todos_id_cat_id_delete_JSON(self):
        # adding the relationship 
        test_input = {
            "id": "2",
            "title": "Extra",
            "description": "Free time"
        }
        
        response = self.client.post(ENDPOINT+'todos/1/categories', json = test_input)
    
        response = self.client.delete(ENDPOINT+'todos/1/categories/2')
        status = self.get_status(response)
        self.assertEqual(200, status)
        output = self.get_response_entity(response)
        self.assertTrue("" == output)
    
    # Test 24: DELETE /todos/:id/categories/:id (Failure case)
    def test_todos_id_cat_id_delete_JSON_2(self):
        response = self.client.delete(ENDPOINT+'todos/1/categories/10')
        self.assertEqual(self.get_status(response), 404) # Check the status code
        # Check if there is an errorMessage 
        self.assertTrue('errorMessages' in json.loads(self.get_response_entity(response)))
        
    ##############################
    
    # Test 25: GET /todos/:id/tasksof
    def test_todos_id_categories_get(self):
        response = self.client.get(ENDPOINT+'todos/1/tasksof')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        output = json.loads(self.get_response_entity(response))
        self.assertEqual(1, len(output))
        self.assertTrue("projects" in output)
    
    # Test 26: HEAD /todos/:id/tasksof
    def test_todos_head(self):
        response = self.client.head(ENDPOINT+'todos/1/tasksof')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        #Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)
    
    # Test 27: POST /todos/:id/tasksof using XML
    def test_todos_id_tasksof_post_XML(self):
        xml_input = """ 
        <project>
            <active>true</active>
            <description>429 Project part 1</description>
            <completed>false</completed>
            <title>429 Project</title>
        </project>
        """
        
        xml_headers = {"Content-Type": "application/xml"}
        
        response = self.client.post(ENDPOINT+'todos/1/tasksof', headers=xml_headers, data=xml_input)
        self.assertEqual(self.get_status(response), 201) # Check the status code
        output = json.loads(self.get_response_entity(response))
        # Check if the output JSON has the same properties + an id
        self.assertTrue(6 <= len(output))
        self.assertTrue('id' in output)
        self.assertEqual(output['title'], "429 Project")        
        self.assertEqual(output['description'], "429 Project part 1")
        self.assertEqual(output['completed'], "false")
        self.assertEqual(output['active'], "true")
        #Check if the todo is had been added 
        self.assertEqual(output["tasks"][0]["id"], "1") 
        pid = output['id']
        # Delete relation
        self.client.delete(ENDPOINT+'todos/1/tasksof/'+pid)
        
    # Test 28: DELETE /todos/:id/categories/:id (Failure case)
    def test_todos_id_tasksof_id_delete_JSON(self):
        # adding the relationship 
        test_input = {
            "id": "1",
            "title": "Assignemnt 2",
            "completed": False,
            "active": False,
            "description": "421 A2"
        }
        # Create the relation for testing
        response = self.client.post(ENDPOINT+'todos/1/tasksof', json = test_input)
    
        response = self.client.delete(ENDPOINT+'todos/1/tasksof/1')
        status = self.get_status(response)
        self.assertEqual(200, status)
        output = self.get_response_entity(response)
        self.assertTrue("" == output)
        
    ########################
    
    #Test 29: Testing JSON payload malformed
    def test_post_JSON_malformed(self):
        test_input = {
            "title": "School",
            "Virus": "Hi",
            "description": "Winter 2024"
        }
        
        response = self.client.post(ENDPOINT+'todos/1/categories', json = test_input)
        # Check the status code (400 Bad Request)
        self.assertEqual(self.get_status(response), 400) 
        # Check if there is an errorMessage 
        self.assertTrue('errorMessages' in json.loads(self.get_response_entity(response)))
        
    #Testing 30: XML payload malformed
    def test_post_XML_malformed(self):
        xml_input = """ 
        <todo>
            <error>false</error>
            <description>Do laundry before 3pm</description>
            <title>Laundry</title>
        </todo>
        """
        xml_headers = {"Content-Type": "application/xml"}
        
        response = self.client.post(ENDPOINT+'todos', headers=xml_headers, data=xml_input)
         # Check the status code (400 Bad Request)
        self.assertEqual(self.get_status(response), 400) 
        output = json.loads(self.get_response_entity(response))
        # Check if there is an errorMessage 
        self.assertTrue('errorMessages' in json.loads(self.get_response_entity(response)))
        
    ######################------------------########################
    
    # categories

    # Test 1: GET categories
    def test_categories_get(self):
        response = self.client.get(ENDPOINT+'categories')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        self.assertTrue(2 <= len(json.loads(self.get_response_entity(response))['categories']))
    
    # Test 2: GET categories/:id
    def test_categoriesID_get(self):
        response = self.client.get(ENDPOINT+'categories/1')
        data = json.loads(self.get_response_entity(response))
        self.assertEqual(self.get_status(response), 200) # Check the status code
        self.assertEqual(data['categories'][0]['id'], '1')
        self.assertTrue('title' in data['categories'][0])
        self.assertTrue('description' in data['categories'][0])
    
    # Test 3: GET categories/:id/projects
    def test_categoriesIDprojects_get(self):
        response = self.client.get(ENDPOINT+'categories/1/projects')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        self.assertEqual(self.get_response_entity(response), """{"projects":[]}""")
    
    # Test 4: GET categories/:id/todos
    def test_categoriesIDtodos_get(self):
        response = self.client.get(ENDPOINT+'categories/1/todos')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        self.assertEqual(self.get_response_entity(response), """{"todos":[]}""")

    # Test 5: HEAD categories
    def test_categories_head(self):
        response = self.client.head(ENDPOINT+'categories')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        #Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)
    
    # Test 6: HEAD categories/:id
    def test_categories_head(self):
        response = self.client.head(ENDPOINT+'categories/1')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        #Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)
    
    # Test 7: HEAD categories/:id/projects
    def test_categoriesIDprojects_head(self):
        response = self.client.head(ENDPOINT+'categories/1/projects')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        #Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)
    
    # Test 8: HEAD categories/:id/todos
    def test_categoriesIDtodos_head(self):
        response = self.client.head(ENDPOINT+'categories/1/todos')
        self.assertEqual(self.get_status(response), 200) # Check the status code
        #Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)

    # Test 9: POST categories
    def test_categories_post(self):
        body_data = {
            "title": "New"  # title to add
        }
        response = self.client.post(ENDPOINT+'categories', data=json.dumps(body_data))
        postid = self.get_response_entity(response)[0]
        self.assertEqual(self.get_status(response), 201) # Check the status code
        response = self.client.get(ENDPOINT+'categories')
        self.assertTrue(3 <= len(json.loads(self.get_response_entity(response))['categories']))
        self.client.delete(ENDPOINT+'categories/'+postid)
    
    # Test 10: POST categories/:id
    def test_categoriesID_post(self):
        body_data = {
            "title": "New",
            "description": "Test 6" 
        }
        response = self.client.post(ENDPOINT+'categories/3', data=json.dumps(body_data))
        self.assertEqual(self.get_status(response), 404) # Check the status code
        postid = self.get_response_entity(response)[0]
        self.client.delete(ENDPOINT+'categories/'+postid)

    # Test 11: POST categories/:id/projects
    def test_categoriesIDprojects_post(self):
        body_data = {
            "id" : 1
        }
        response = self.client.post(ENDPOINT+'categories/1/projects', data=json.dumps(body_data))
        self.assertEqual(self.get_status(response), 404) # Check the status code
        #couldn't verify the output message {"errorMessages": ["Could not find thing matching value for id"]}
    
    # Test 12: POST categories/:id/todos
    def test_categoriesIDtodos_post(self):
        body_data = {
            "id" : 1
        }
        response = self.client.post(ENDPOINT+'categories/1/todos', data=json.dumps(body_data))
        self.assertEqual(self.get_status(response), 404) # Check the status code
        #couldn't verify the output message {"errorMessages": ["Could not find thing matching value for id"]}
        #test not recording for some reason

    # Test 13: PUT categories/:id
    def test_categoriesID_put(self):
        body_data = {
            "title": "New",
            "description": "Test 13" 
        }
        response = self.client.put(ENDPOINT+'categories/300', data=json.dumps(body_data))
        self.assertEqual(self.get_status(response), 404) # Check the status code
        postid = self.get_response_entity(response)[0]
        self.client.delete(ENDPOINT+'categories/'+postid)

    # Test 14: DELETE categories/:id
    def test_categoriesID_delete(self):
        body_data = {
            "title": "to Delete"  # title to add
        }
        response = self.client.post(ENDPOINT+'categories', data=json.dumps(body_data))
        output = json.loads(self.get_response_entity(response))
        cid = output['id'] # Get the generated id
        response = self.client.delete(ENDPOINT+'categories/'+cid)
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        #no output message
    
    # Test 15: DELETE categories/:id/projects/:id
    def test_categoriesIDprojects_delete(self):
        response = self.client.delete(ENDPOINT+'categories/1/projects/1')
        self.assertEqual(self.get_status(response), 404) # Check the status code
        #couldn't verify the output message {"errorMessages": ["Could not find thing matching value for id"]}

    # Test 16: DELETE categories/:id/todos/:id
    def test_categoriesIDtodos_delete(self):
        response = self.client.delete(ENDPOINT+'categories/1/todos/1')
        self.assertEqual(self.get_status(response), 404) # Check the status code
        #couldn't verify the output message {"errorMessages": ["Could not find thing matching value for id"]}

    # Test 17: POST categories XML
    def test_categories_post_XML(self):
        xml_input = """ 
            <category>
            <description>test 17</description>
            <title>title 17</title>
            </category>
        """
        xml_headers = {"Content-Type": "application/xml"}
        response = self.client.post(ENDPOINT+'categories', headers=xml_headers, data=xml_input)
        self.assertEqual(self.get_status(response), 201) # Check the status code
        output = json.loads(self.get_response_entity(response))
        # Check if the output JSON has the same properties + an id
        self.assertTrue(3 == len(output))
        self.assertTrue('id' in output)
        self.assertEqual(output['title'], "title 17")        
        self.assertEqual(output['description'], "test 17")
        postid = self.get_response_entity(response)[0]
        self.client.delete(ENDPOINT+'categories/'+postid)
    
    # Test 18: POST categories/:id
    def test_categoriesID_post(self):
        xml_input = """ 
            <category>
            <description>test 18</description>
            <title>title 18</title>
            </category>
        """
        xml_headers = {"Content-Type": "application/xml"}
        response = self.client.post(ENDPOINT+'categories/1', headers=xml_headers, data=xml_input)
        self.assertEqual(self.get_status(response), 200) # Check the status code
        output = json.loads(self.get_response_entity(response))
        # Check if the output JSON has the same properties + an id
        self.assertTrue(3 == len(output))
        self.assertTrue('id' in output)
        self.assertEqual(output['title'], "title 18")        
        self.assertEqual(output['description'], "test 18")
        postid = self.get_response_entity(response)[0]
        self.client.delete(ENDPOINT+'categories/'+postid)
        
    ################-------------------######################
    
    # Projects
    
    # Test 1: HEAD request for /projects/
    def test_projects_head(self):
        response = self.client.head(ENDPOINT + 'projects')
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        # Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)

    # Test 2: GET request using JSON for /projects/
    def test_json_projects_get(self):
        response = self.client.get(ENDPOINT+'projects')
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        self.assertTrue(1 <= len(json.loads(self.get_response_entity(response))['projects']))

    # Test 3: POST request using JSON for /projects
    def test_json_projects_post(self):
        response = self.client.post(ENDPOINT+'projects', json={"title": "Post project",
                                                               "completed": False,
                                                               "active": True,
                                                               "description": "post"})
        self.assertEqual(self.get_status(response), 201)  # Check the status code
        self.assertTrue("Post project" == json.loads(self.get_response_entity(response))['title'])
        pid = json.loads(self.get_response_entity(response))['id']
        response = self.client.delete(ENDPOINT + f'projects/{pid}')

    # Test 4: HEAD request for /projects/:id
    def test_projects_id_head(self):
        response = self.client.head(ENDPOINT + 'projects/1')
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        # Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)

    # Test 5: GET request using JSON for /projects/:id
    def test_json_projects_id_get(self):
        response = self.client.get(ENDPOINT+'projects/1')
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        self.assertTrue(1 <= len(json.loads(self.get_response_entity(response))['projects']))

    # Test 6: POST request using JSON for /projects/:id
    def test_json_projects_id_post(self):
        response = self.client.get(ENDPOINT + 'projects/1')
        fields = {"title": "Post project",
                   "completed": False,
                   "active": True,
                   "description": "post"}
        response = self.client.post(ENDPOINT+'projects/1', json=fields)
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        self.assertTrue("Post project" == json.loads(self.get_response_entity(response))['title'])
        self.assertTrue('false' == json.loads(self.get_response_entity(response))['completed'])
        self.assertTrue('true' == json.loads(self.get_response_entity(response))['active'])
        self.assertTrue("post" == json.loads(self.get_response_entity(response))['description'])
        response = self.client.post(ENDPOINT + 'projects/1', json={"title": "Office Work",
                                                                   "completed": False,
                                                                   "active": False,
                                                                   "description": ""})

    # Test 7: PUT request using JSON for /projects/:id
    def test_json_projects_id_put(self):
        response = self.client.get(ENDPOINT + 'projects/1')
        fields = {"title": "Post project",
                  "completed": False,
                  "active": True,
                  "description": "post"}
        new_fields = {"title": "Post project1",
                      "completed": False,
                      "active": True,
                      "description": "post1"}
        response = self.client.post(ENDPOINT + 'projects', json=fields)
        pid = json.loads(self.get_response_entity(response))['id']
        response = self.client.put(ENDPOINT + f'projects/{pid}', json=new_fields)
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        self.assertTrue("Post project1" == json.loads(self.get_response_entity(response))['title'])
        self.assertTrue('false' == json.loads(self.get_response_entity(response))['completed'])
        self.assertTrue('true' == json.loads(self.get_response_entity(response))['active'])
        self.assertTrue("post1" == json.loads(self.get_response_entity(response))['description'])
        response = self.client.delete(ENDPOINT + f'projects/{pid}')


    # Test 8: DELETE request using JSON for /projects/:id
    def test_json_projects_id_delete(self):
        response = self.client.post(ENDPOINT + 'projects', json={"title": "Post project",
                                                                 "completed": False,
                                                                 "active": True,
                                                                 "description": "post"})
        self.assertEqual(self.get_status(response), 201)  # Check the status code
        self.assertTrue("Post project" == json.loads(self.get_response_entity(response))['title'])
        pid = json.loads(self.get_response_entity(response))['id']
        response = self.client.delete(ENDPOINT + f'projects/{pid}')
        response = self.client.get(ENDPOINT + f'projects/{pid}')
        self.assertEqual(self.get_status(response), 404)

    # Test 9: HEAD request for /projects/:id/tasks
    def test_projects_id_tasks_head(self):
        response = self.client.head(ENDPOINT + 'projects/1/tasks')
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        # Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)

    # Test 10: GET request using JSON for /projects/:id/tasks
    def test_json_projects_id_tasks_get(self):
        response = self.client.get(ENDPOINT+'projects/1/tasks')
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        self.assertTrue('todos' in json.loads(self.get_response_entity(response)))

    # Test 11: POST request using JSON for /projects/:id/tasks
    def test_json_projects_id_tasks_post(self):
        todo_title = {'title': 'print'}
        response = self.client.post(ENDPOINT + f'projects/1/tasks', json=todo_title)
        self.assertEqual(self.get_status(response), 201)
        tid = json.loads(self.get_response_entity(response))['id']
        self.assertEqual(json.loads(self.get_response_entity(response))['tasksof'][0]['id'], '1')
        response = self.client.delete(ENDPOINT+f'projects/1/tasks/{tid}')
        response = self.client.delete(ENDPOINT + f'todos/{tid}')

    # Test 12: DELETE request using JSON for /projects/:id/tasks/:id
    def test_json_projects_id_tasks_id_delete(self):
        # Get the number of todos before adding and deleting
        response = self.client.get(ENDPOINT + f'projects/1/tasks')
        output = json.loads(self.get_response_entity(response))
        number_todos = len(output["todos"])
        todo_title = {'title': 'print'}
        response = self.client.post(ENDPOINT + f'projects/1/tasks', json=todo_title)
        tid = json.loads(self.get_response_entity(response))['id']
        response = self.client.delete(ENDPOINT + f'projects/1/tasks/{tid}')
        self.assertEqual(self.get_status(response), 200)
        response = self.client.get(ENDPOINT + f'projects/1/tasks')
        output = json.loads(self.get_response_entity(response))
        self.assertEqual(number_todos, len(output["todos"]))
        response = self.client.delete(ENDPOINT + f'todos/{tid}')

    # Test 13: HEAD request for /projects/:id/categories
    def test_projects_id_categories_head(self):
        response = self.client.head(ENDPOINT + 'projects/1/categories')
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        # Assert headers contain 4 properties (Date, Content-Type, Transfer-Encoding, Server)
        self.assertTrue(4 == len(response.headers))
        self.assertTrue('Date' in response.headers)
        self.assertTrue('Content-Type' in response.headers)
        self.assertTrue('Transfer-Encoding' in response.headers)
        self.assertTrue('Server' in response.headers)

    # Test 14: GET request using JSON for /projects/:id/categories
    def test_json_projects_id_categories_get(self):
        response = self.client.get(ENDPOINT + 'projects/1/categories')
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        self.assertTrue(0 == len(json.loads(self.get_response_entity(response))['categories']))

    # Test 15: POST request using JSON for /projects/:id/categories
    def test_json_projects_id_categories_post(self):
        category_title = {'title': 'Office'}
        response = self.client.post(ENDPOINT + f'projects/1/categories', json=category_title)
        response = self.client.get(ENDPOINT + f'projects/1/categories')
        self.assertTrue(1 == len(json.loads(self.get_response_entity(response))['categories']))
        cid = json.loads(self.get_response_entity(response))['categories'][0]['id']
        response = self.client.delete(ENDPOINT + f'projects/1/categories/{cid}')

    # Test 16: DELETE request using JSON for /projects/:id/categories/:id
    def test_json_projects_id_categories_id_delete(self):
        category_title = {'title': 'Office'}
        response = self.client.post(ENDPOINT + f'projects/1/categories', json=category_title)
        response = self.client.get(ENDPOINT + f'projects/1/categories')
        cid = json.loads(self.get_response_entity(response))['categories'][0]['id']
        response = self.client.delete(ENDPOINT + f'projects/1/categories/{cid}')
        response = self.client.get(ENDPOINT + f'projects/1/categories')
        self.assertEqual(self.get_status(response), 200)  # Check the status code
        self.assertTrue(0 == len(json.loads(self.get_response_entity(response))['categories']))
        
if __name__ == '__main__':
    # Make sure tests are running in random order
    loader = RandomTestLoader()
    suite = loader.loadTestsFromTestCase(APITester)
    runner = unittest.TextTestRunner()
    runner.run(suite)