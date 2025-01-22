Feature: User Request Projects 
  #As a user
  #I want to use id to get a project
  #So that I can view the details of that project

  #alternative flow
  Scenario: User wants a project with a non-existing id
    Given User connects to TodoManager
    When User asks for a project of a non-existing id 23333
    Then Manager sends back an error msg: "Could not find an instance with projects/23333"

  #error flow
  Scenario: User wants a project with invalid parameter
    Given User connects to TodoManager
    When User asks for a project without id
    Then Manager sends back nothing

  ####################################################
  #As a user
  #I want to add a new project in the project instance table with a description
  #So that I can plan for a new project

  #alternative flow
  Scenario: User wants to add a project with description using xml
    Given User connects to TodoManager
    When User posts a new project with xml:
      """
      <project>
        <description>asap</description>
        <title>429 project</title>
      </project>
      """
    Then Manager sends back the created project

  #error flow
  Scenario: User wants to add a project with wrong syntax xml
    Given User connects to TodoManager
    When User posts a new project with xml:
      """
      <project>
        <description>asap</description>
        <title>429 project</title>
        <active>ffalse</active>
      </project>
      """
    Then Manager sends back an error msg: "Failed Validation: active should be BOOLEAN"


  ####################################################
  #As a user
  #I want to delete an existing project by its id
  #So that I can move on when that project is done

  #normal flow
  Scenario: User adds a project and delete it
    Given User connects to TodoManager
    When User posts a project
    Then Manager sends back the created project
    And User deletes the project

  #error flow
  Scenario: User wants to delete non-existing project
    Given User connects to TodoManager
    When User deletes a project of id 32222
    Then Manager sends back an error msg: "Could not find any instances with projects/32222"


  ####################################################
  #As a user
  #I want to add a project, adds a task and deletes the task
  #So that I can remove the task when it is done

  #alternative flow
  Scenario: User adds a projects, adds two tasks and deletes the latest created task after
    Given User connects to TodoManager
    When User posts a project
    Then Manager sends back the created project
    And User adds a task named: "task1"
    Then Manager sends back the created task
    And User adds a task named: "task2"
    Then Manager sends back the created task
    And User deletes last task added


  ####################################################
  #As a user
  #I want to get the header of projects
  #So that I can know where would be the potential body information

  #normal flow
  Scenario: User gets header of projects
    Given User connects to TodoManager
    When User heads "projects"
    Then User requests successfully


  #alternative flow
  Scenario: User gets header of projects through /projects/1
    Given User connects to TodoManager
    When User heads "projects/1/tasks"
    Then User requests successfully

  #error flow
  Scenario: User gets header of projects through /projects/1/tasks/1
    When User heads "projects/1/tasks/1"
    Then User request fails

  #error flow
  Scenario: User wants to delete non-existing task
    Given User connects to TodoManager
    When User deletes a task of id 32222 of project 1 and fail
    Then Manager sends back an error msg: "Could not find any instances with projects/1/tasks/32222"

  
  #alternative flow
  Scenario: User adds a projects, updates, and deletes it after
    Given User connects to TodoManager
    When User posts a project
    Then Manager sends back the created project
    And User updates the project
    And User deletes the project

  #normal flow
  Scenario: User wants a project with an existing id
    Given User connects to TodoManager
    When User asks for a project of id 1
    Then Manager sends back the project of id 1

  #normal flow
  Scenario: User wants to add a project with description using json
    Given User connects to TodoManager
    When User posts a project using json: 
      | title | description |
      | 429 project | asap |
    Then Manager sends back the created project

  #normal flow
  Scenario: User adds a project, adds a task and deletes the task
    Given User connects to TodoManager
    When User posts a project
    Then Manager sends back the created project
    And User adds a task named: "task1"
    Then Manager sends back the created task
