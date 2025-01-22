Feature: User Interacting with categories 

  Scenario: User wants a list of categories 
    Given User connects to TodoManager
    And User asks for a list of categories
    Then the request is successful
    And Manager sends back the list

##########################
# USER STORY 1: GET /categories
# Normal flow 
  Scenario: User adds a new category using JSON
      Given User connects to TodoManager
      When User posts a new category with JSON:
        | title | description |
        | Story 1 | Test 1 |
      Then Manager sends back the created category

# Alternate flow
  Scenario: User adds a new category using XML
    Given User connects to TodoManager
    When User posts a new category with XML:
      """
      <category>
          <description>Test 1</description>
          <title>Story 1</title>
      </category>
      """
    Then Manager sends back the created category

# Error flow
  Scenario: User tries to adds a new category using wrong formatted XML 
    Given User connects to TodoManager
    When User posts a new category with XML:
      """
      <category>
          <description>Introduction to Computer Science</description>
          <title>COMP250</title>
          <id>2</id>
      </category>
      """
    Then Manager rejects to create new category because of wrong format

##########################
# USER STORY 2: GET /categories/id and POST /categories

# Normal Flow
  Scenario: Retrieve a category by its ID
    Given User connects to TodoManager
    When User retrieves category with ID 1
    Then the request is successful
    And Manager sends back the category with ID 1

# Alternate Flow
  Scenario: Post a category and retrieve it by its returned ID
    Given User connects to TodoManager
    When User posts a new category
    Then Manager sends back the created category with an ID
    And User retrieves the created category by its returned ID
    Then the request is successful
    And Manager sends back the retrieved category

# Error Flow
  Scenario: Retrieve a category with a non-existing ID
    Given User connects to TodoManager
    When User retrieves category with ID 1001
    Then Manager sends back a not found error
    And Error message is included in the response

##########################

# USER STORY 3: GET /categories/id and POST /categories

# Normal Flow
  Scenario: Create and delete a todo
    Given User connects to TodoManager
    When User posts a new category
    Then Manager sends back the created category with an ID
    And User deletes the created category
    Then the request is successful
    And The deleted category is not found

# Alternate Flow
  Scenario: Create and update and delete a category
    Given User connects to TodoManager
    When User posts a new category
    Then Manager sends back the created category with an ID
    And User updates the category with PUT
    And the request is successful
    And User deletes the created category
    And the request is successful
    And The deleted category is not found

# Error Flow
  Scenario: Delete a category that does not exist
    Given User connects to TodoManager
    When User tries to delete a non-existing category
    Then Manager sends back a not found error

##########################
# USER STORY 4: GET and POST categories/:id/todos

# Normal Flow
  Scenario: Retrieve todos related to a category
    Given User connects to TodoManager
    When User retrieves todos related to category with ID 1
    Then the request is successful
    And Manager sends back the todos

# Alternate Flow 1
  Scenario: Add todos to a categories using JSON
    Given User connects to TodoManager
    When User adds a todo with PUT JSON data to category with ID 1
    Then Manager sends back the created todo with the ID
    When User retrieves todos related to category with ID 1
    Then the request is successful
    Then Manager sends back the todos
  
  #Alternate Flow 2
  Scenario: Add todos to a categories using JSON
    Given User connects to TodoManager
    When User adds a todo with POST JSON data to category with ID 1
    Then Manager sends back the created todo with the ID
    When User retrieves todos related to category with ID 1
    Then the request is successful
    Then Manager sends back the todos

# Error Flow  
# --BUG--
  Scenario: Retrieve todos related to a category
    Given User connects to TodoManager
    When User retrieves todos related to category with ID 100001
    Then Manager should report a not found error


###########################
# USER STORY 5: categories/:id/projects

# Normal flow
  Scenario: Get headers for categories
    Given User connects to TodoManager
    When User requests headers for categories related projects with ID 1
    Then the request is successful
    And Manager sends back the headers for associated projects

# Alternate flow
  Scenario: Post a new project for a exisitng category of giving ID
    Given User connects to TodoManager
      When User posts a new project for a category with XML:
        """
        <project>
            <active>true</active>
            <description>Story 5 - Alternative Flow </description>
            <completed>false</completed>
            <title>Story 5</title>
        </project>
        """
      Then Manager sends back the created project for the category

# Error flow
   Scenario: Add project to a non-existing category using XML
    Given User connects to TodoManager
    When User adds a project to a non-existing category with ID '10001'
    Then Manager sends back a not found error

