Feature: User Interacting with Todos 

##########################
# USER STORY 1: GET and PUT /todos
# Normal flow 
  Scenario: User adds a new todo using JSON
      Given User connects to TodoManager
      When User posts a new todo with JSON:
        | title | description |
        | Watch 409 recording | watch thursday recording |
      Then Manager sends back the created todo

# Alternate flow
  Scenario: User adds a new todo using XML
    Given User connects to TodoManager
    When User posts a new todo with XML:
      """
      <todo>
          <doneStatus>false</doneStatus>
          <description>watch thursday recording</description>
          <title>Watch 409 recording</title>
      </todo>
      """
    Then Manager sends back the created todo

# Error flow
  Scenario: User tries to adds a new todo using wrong formatted XML 
    Given User connects to TodoManager
    When User posts a new todo with XML:
      """
      <todo>
          <doneStatus>true</doneStatus>
          <description>watch thursday recording</description>
          <title>Watch 409 recording</title>
          <id>null</id>
      </todo>
      """
    Then Manager rejects to create new todo because of wrong format

##########################
# USER STORY 2: GET /todos/id and POST /todos

# Normal Flow
  Scenario: Retrieve a todo by its ID
    Given User connects to TodoManager
    When User retrieves todo with ID 1
    Then the request is successful
    And Manager sends back the todo with ID 1

# Alternate Flow
  Scenario: Post a todo and retrieve it by its returned ID
    Given User connects to TodoManager
    When User posts a new todo
    Then Manager sends back the created todo with an ID
    And User retrieves the created todo by its returned ID
    Then the request is successful
    And Manager sends back the retrieved todo

# Error Flow
  Scenario: Retrieve a todo with a non-existing ID
    Given User connects to TodoManager
    When User retrieves todo with ID 1001
    Then Manager sends back a not found error
    And Error message is included in the response

##########################
# USER STORY 3: GET /todos/id, POST /todos, DELETE /todos/id

# Normal Flow
  Scenario: Create and delete a todo
    Given User connects to TodoManager
    When User posts a new todo
    Then Manager sends back the created todo with an ID
    And User deletes the created todo
    Then the request is successful
    And The deleted todo is not found

# Alternate Flow
  Scenario: Create and update and delete a todo
    Given User connects to TodoManager
    When User posts a new todo
    Then Manager sends back the created todo with an ID
    And User updates the todo with PUT
    And the request is successful
    And User deletes the created todo
    And the request is successful
    And The deleted todo is not found

# Error Flow
  Scenario: Delete a todo that does not exist
    Given User connects to TodoManager
    When User tries to delete a non-existing todo
    Then Manager sends back a not found error

##########################
# USER STORY 4: GET and POST todos/:id/categories

# Normal Flow
  Scenario: Retrieve categories related to a todo
    Given User connects to TodoManager
    When User retrieves categories related to todo with ID 1
    Then the request is successful
    And Manager sends back the categories for todos

# Alternate Flow
  Scenario: Add categories to a todo using JSON
    Given User connects to TodoManager
    When User adds a category with JSON data to todo with ID 1
    Then Manager sends back the created category with the ID
    When User retrieves categories related to todo with ID 1
    Then the request is successful
    Then Manager sends back the categories for todos

# Error Flow  
# --BUG--
  Scenario: Retrieve categories related to a non-existing todo
    Given User connects to TodoManager
    When User retrieves categories related to todo with ID 100001
    Then Manager should report a not found error

##########################
# USER STORY 5: todos/:id/tasksof

# Normal flow
  Scenario: Get headers for todos related tasks
    Given User connects to TodoManager
    When User requests headers for todos related tasks with ID 1
    Then the request is successful
    And Manager sends back the headers for associated tasks

# Alternate flow
  Scenario: Post a new tasks for a exisitng todo of giving ID
    Given User connects to TodoManager
      When User posts a new tasks for a todo with XML:
        """
        <project>
            <active>true</active>
            <description>429 Project part 2</description>
            <completed>false</completed>
            <title>429 Project</title>
        </project>
        """
      Then Manager sends back the created project for the todo

# Error flow
   Scenario: Add project to a non-existing todo using XML
    Given User connects to TodoManager
    When User adds a project to a non-existing todo with ID 'random_id'
    Then Manager sends back a not found error