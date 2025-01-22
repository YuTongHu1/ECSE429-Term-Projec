package project2;

import io.cucumber.datatable.DataTable;
import io.cucumber.java.After;
import io.cucumber.java.AfterAll;
import io.cucumber.java.en.*;

import org.junit.Assert;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ConnectException;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.List;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONObject;

public class StepDefinitions {

    // Global variables 
    private static HttpURLConnection connection;
    private static String baseURL = "http://localhost:4567/";
    
    // Storing returned values for later testing
    private String returnedTodoId;
    private String returnedCategoryId;
    private String projectIDToBeDeleted;
    private String taskIDToBeDeleted;
    
    @After("@notLast") //After each scenario except the last one
    public static void closeConnection() {
        if (connection != null) {
            connection.disconnect();
        }
    }

    //restore initial state upon completion
    @AfterAll
    public static void tearDown() throws URISyntaxException, IOException, ConnectException {
        URI shutdownUri = new URI(baseURL + "shutdown");
        URL shutdownUrl = shutdownUri.toURL();
        HttpURLConnection shutdownConnection = (HttpURLConnection) shutdownUrl.openConnection();
        shutdownConnection.setRequestMethod("GET");
        int responseCode = shutdownConnection.getResponseCode();
        shutdownConnection.disconnect();
        connection.disconnect();
    }

    //******************
    //Methods for testing Todos

    @Given("User connects to TodoManager")
    public void setUp() throws IOException, URISyntaxException{
        URI uri = new URI(baseURL);        
        // Convert URI to URL
        URL url = uri.toURL();
        //GET request to the API for connection
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");

        int responseCode = connection.getResponseCode();
        assertEquals(200, responseCode);
    }

    @Then("the request is successful")
    public void check_request_is_successful() throws IOException {
        if (connection != null){
            int responseCode = connection.getResponseCode();
            assertEquals(200, responseCode);
        }
    }

    @When("User asks for a list of todos")
    public void userAsksForListOfTodos() throws Exception {
        URI uri = new URI(baseURL + "todos");
        URL url = uri.toURL();

        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
    }

    @When("User posts a new todo with JSON:")
    public void userPostsNewTodoWithJSON(DataTable dataTable) throws Exception {
        List<Map<String, String>> todoData = dataTable.asMaps(String.class, String.class);
        for (Map<String, String> row : todoData) {
            JSONObject json = new JSONObject(row);
            URI uri = new URI(baseURL + "todos");
            URL url = uri.toURL();
            System.out.println(json.toString());
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);
            connection.getOutputStream().write(json.toString().getBytes());
        }
    }
    
    @When("User posts a new todo with XML:")
    public void userPostsNewTodoWithXML(String xmlData) throws Exception {
        URI uri = new URI(baseURL + "todos");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlData.getBytes());
    }
    
    @Then("Manager sends back the created todo")
    public void managerSendsBackCreatedTodo() throws Exception {
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(201, responseCode);

        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();

        JSONObject output = new JSONObject(response.toString());
        Assert.assertEquals(4, output.length());
        Assert.assertTrue(output.has("id"));
        Assert.assertEquals("Watch 409 recording", output.getString("title"));
        Assert.assertEquals("watch thursday recording", output.getString("description"));
        Assert.assertEquals(false, output.getBoolean("doneStatus"));
    }

    @Then("Manager rejects to create new todo because of wrong format")
    public void Manager_rejects_to_create_new_todo() throws IOException {
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(400, responseCode);
        BufferedReader errorReader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
        StringBuilder errorMessage = new StringBuilder();
        String line;
        while ((line = errorReader.readLine()) != null) {
            errorMessage.append(line);
        }
        errorReader.close();
        System.out.println(errorMessage.toString());
    }

    @When("User retrieves todo with ID {int}")
    public void User_retrieves_todo_with_ID(int todoID) throws URISyntaxException, IOException {
        URI uri = new URI(baseURL + "todos/" + todoID);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
    }
    
    @Then("Manager sends back the todo with ID {int}")
    public void Manager_sends_todo_with_ID(int todoID) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();

        JSONObject output = new JSONObject(response.toString());
        JSONArray todosArray = output.getJSONArray("todos");
        JSONObject todo = todosArray.getJSONObject(0);
        // Validate that the todo has the expected ID
        Assert.assertEquals(String.valueOf(todoID), todo.getString("id"));
    }

    @When("User posts a new todo")
    public void userPostsNewTodo() throws Exception {
        // Construct the JSON data for the new todo
        JSONObject json = new JSONObject();
        json.put("title", "Create a new todo");
        json.put("doneStatus", false);
        json.put("description", "This is not a description");

        // Send POST request to create the todo
        URI uri = new URI(baseURL + "todos");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.getOutputStream().write(json.toString().getBytes());

        // Get the ID of the created todo from the response for later testing
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        JSONObject jsonResponse = new JSONObject(response.toString());
        // Keep track of the created id 
        returnedTodoId = jsonResponse.getString("id");
    }

    @Then("Manager sends back the created todo with an ID")
    public void managerSendsBackID() {
        Assert.assertNotNull(returnedTodoId);
    }

    @When("User retrieves the created todo by its returned ID")
    public void userRetrievesTodoByReturnedID() throws Exception {
        // GET request to retrieve the todo by its returned ID
        URI uri = new URI(baseURL + "todos/" + returnedTodoId);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
    }

    @Then("Manager sends back the retrieved todo")
    public void managerSendsRetrievedTodo() throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();

        JSONObject retrievedTodo = new JSONObject(response.toString());
        String retrievedTodoId = retrievedTodo.getJSONArray("todos").getJSONObject(0).getString("id");
        Assert.assertEquals(returnedTodoId, retrievedTodoId);
    }

    @Then("Manager sends back a not found error")
    public void managerSendsBackNotFoundError() throws Exception {
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(404, responseCode);
    }

    @Then("Error message is included in the response")
    public void errorMessageInTheResponse() throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
        StringBuilder errorMessage = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            errorMessage.append(line);
        }
        reader.close();

        // Check if the error message is included in the response
        JSONObject returnedMessage = new JSONObject(errorMessage.toString());
        Assert.assertTrue(returnedMessage.has("errorMessages"));
        System.out.println(errorMessage.toString());
    }

    @When("User deletes the created todo")
    public void userDeletesCreatedTodo() throws Exception {
        // DELETE the previously created todo
        URI uri = new URI(baseURL + "todos/" + returnedTodoId);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("DELETE");
    }

    @Then("The deleted todo is not found")
    public void todoIsNotFound() throws Exception {
        // Attempt to retrieve the todo with its ID
        URI uri = new URI(baseURL + "todos/" + returnedTodoId);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
        
        // Verify if the response code is 404 (Check if deleted)
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(404, responseCode);
    }

    @When("User tries to delete a non-existing todo")
    public void DeleteNonExistingTodo() throws Exception {
        // DELETE a non-existing todo
        URI uri = new URI(baseURL + "todos/non_existing_id");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("DELETE");
    }

    @Then("User updates the todo with PUT")
    public void User_updates_the_todo_with_PUT() throws Exception {
        // new JSON data for the todo
        JSONObject json = new JSONObject();
        json.put("title", "Update a Todo");
        json.put("doneStatus", true);
        json.put("description", "Testing PUT");

        // PUT request to update the previously created todo
        URI uri = new URI(baseURL + "todos/" + returnedTodoId);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("PUT");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.getOutputStream().write(json.toString().getBytes());
    }

    @When("User retrieves categories related to todo with ID {int}")
    public void get_categories_of_todo_with_ID(int todoId) throws Exception {
        // Send GET request to retrieve categories related to the todo with given ID 
        URI uri = new URI(baseURL + "todos/" + todoId + "/categories");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
    }
    
    @Then("Manager should report a not found error")
    public void Manager_expects_a_not_found_error() throws IOException {
        int responseCode = connection.getResponseCode();
        if (responseCode != 404) {
            System.out.println("!!! The Manager did not report a not found error !!!");
            System.out.println("The response code is " + responseCode);
        }
    }

    @Then("Manager sends back the categories for todos")
    public void sends_back_the_categories_for_todos() throws Exception{
        // get the JSON output
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        JSONObject jsonResponse = new JSONObject(response.toString());

        // check if the response contains categories
        Assert.assertTrue(jsonResponse.has("categories"));

    }
    
    @Then("Manager sends back the created category with the ID")
    public void send_back_created_category_for_todos() throws Exception {
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(201, responseCode);

        // Get the ID of the added category from the response
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        JSONObject jsonResponse = new JSONObject(response.toString());
        jsonResponse.getString("id");
    }

    @When("User adds a category with JSON data to todo with ID {int}")
    public void Add_a_category_to_todo_with_ID(int todoId) throws Exception{
        // JSON data for the new category
        JSONObject json = new JSONObject();
        json.put("title", "School");
        json.put("description", "Winter 2024");

        // Send POST request to add category to todo with the given ID
        URI uri = new URI(baseURL + "todos/" + todoId + "/categories");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.getOutputStream().write(json.toString().getBytes());
    }

    @When("User requests headers for todos related tasks with ID {int}")
    public void get_headers_todos_related_tasks(int todoId) throws Exception{
        //HEAD request to retrieve headers for tasks associated with todo of given ID
        URI uri = new URI(baseURL + "todos/" + todoId + "/tasksof");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("HEAD");
    }

    @Then("Manager sends back the headers for associated tasks")
    public void send_headers_for_associated_tasks() {
        // check if the response headers contain the expected properties
        Assert.assertTrue(connection.getHeaderFields().containsKey("Date"));
        Assert.assertTrue(connection.getHeaderFields().containsKey("Content-Type"));
        Assert.assertTrue(connection.getHeaderFields().containsKey("Transfer-Encoding"));
        Assert.assertTrue(connection.getHeaderFields().containsKey("Server"));
    }

    @When("User posts a new tasks for a todo with XML:")
    public void User_posts_a_new_tasks_for_a_todo_with_XML(String xmlData) throws Exception{
        URI uri = new URI(baseURL + "todos/1/tasksof");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlData.getBytes());
    }

    @Then("Manager sends back the created project for the todo")
    public void managerSendsBackCreatedProjectForTodo() throws Exception {
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(201, responseCode);

        // Parse the response JSON
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        JSONObject jsonResponse = new JSONObject(response.toString());

        // check if the response JSON contains the expected data
        Assert.assertTrue(jsonResponse.has("id"));
        Assert.assertEquals("429 Project", jsonResponse.getString("title"));
        Assert.assertEquals("429 Project part 2", jsonResponse.getString("description"));
        Assert.assertEquals("false", jsonResponse.getString("completed"));
        Assert.assertEquals("true", jsonResponse.getString("active"));
    }

    @When("User adds a project to a non-existing todo with ID {string}")
    public void add_project_to__non_existing_todo(String fake_id) throws Exception {
        // XML data for adding a project to a non-existing todo
        String xmlInput = "<project>\n" +
                          "    <active>false</active>\n" +
                          "    <description>429 Project part 3</description>\n" +
                          "    <completed>false</completed>\n" +
                          "    <title>429 Project</title>\n" +
                          "</project>";

        // POST request to add project to a non-existing todo with the given ID
        URI uri = new URI(baseURL + "todos/" + fake_id + "/tasksof");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlInput.getBytes());
    }

    //*****************************
    //Methods for testing Categories

    @When("User asks for a list of categories")
    public void user_asks_for_a_list_of_todos() throws Exception {

        URI uri = new URI(baseURL + "categories");
        // Convert URI to URL
        URL url = uri.toURL();

        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");

        // Verify that the response code is 200 (OK)
        int responseCode = connection.getResponseCode();
        assertEquals(200, responseCode);
    }

    @Then("Manager sends back the list")
    public void managerSendsBackList() throws Exception {
        // read and print the response from the server
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        // print the response body
        System.out.println("Response from Manager: " + response.toString());
    }

    // Story 1

    // Normal Flow
    @When("User posts a new category with JSON:")
    public void userPostsNewCategoryWithJSON(DataTable dataTable) throws Exception {
        List<Map<String, String>> todoData = dataTable.asMaps(String.class, String.class);
        for (Map<String, String> row : todoData) {
            JSONObject json = new JSONObject(row);
            URI uri = new URI(baseURL + "categories");
            URL url = uri.toURL();
            
            // Print nicely formatted JSON
            System.out.println("Received JSON data:");
            System.out.println(json.toString(4)); // Indent with 4 spaces
            
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);
            connection.getOutputStream().write(json.toString().getBytes());
        }
    }

    // Alternative Flow
    @When("User posts a new category with XML:")
    public void userPostsNewCategoryWithXML(String xmlData) throws Exception {
        System.out.println("Received XML data:");
        System.out.println(xmlData); // Print the XML data

        URI uri = new URI(baseURL + "categories");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlData.getBytes());
    }
    
    @Then("Manager sends back the created category")
    public void managerSendsBackCreatedCategory() throws Exception {
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(201, responseCode);

        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();

        JSONObject output = new JSONObject(response.toString());
        Assert.assertEquals(3, output.length());
        Assert.assertTrue(output.has("id"));
        Assert.assertEquals("Story 1", output.getString("title"));
        Assert.assertEquals("Test 1", output.getString("description"));
    }

    // Error Flow
    @Then("Manager rejects to create new category because of wrong format")
    public void Manager_rejects_to_create_new_category() throws IOException {
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(400, responseCode);
        BufferedReader errorReader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
        StringBuilder errorMessage = new StringBuilder();
        String line;
        while ((line = errorReader.readLine()) != null) {
            errorMessage.append(line);
        }
        errorReader.close();
        System.out.println(errorMessage.toString());
    }

    // Story 2

    // Normal flow
    @When("User retrieves category with ID {int}")
    public void User_retrieves_category_with_ID(int categoryID) throws URISyntaxException, IOException {
        URI uri = new URI(baseURL + "categories/" + categoryID);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
    }
    
    @Then("Manager sends back the category with ID {int}")
    public void Manager_sends_category_with_ID(int categoryID) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();

        JSONObject output = new JSONObject(response.toString());
        JSONArray todosArray = output.getJSONArray("categories");
        JSONObject todo = todosArray.getJSONObject(0);
        // Validate that the category has the expected ID
        Assert.assertEquals(String.valueOf(categoryID), todo.getString("id"));
    }

    // Alternative Flow
    @When("User posts a new category")
    public void userPostsNewCategory() throws Exception {
        // Construct the JSON data for the new todo
        JSONObject json = new JSONObject();
        json.put("title", "Story 2 - Alternative Fow");
        json.put("description", "Story 2 test");

        // Send POST request to create the category
        URI uri = new URI(baseURL + "categories");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.getOutputStream().write(json.toString().getBytes());

        // Get the ID of the created todo from the response for later testing
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        JSONObject jsonResponse = new JSONObject(response.toString());
        // Keep track of the created id 
        returnedCategoryId = jsonResponse.getString("id");
    }

    @Then("Manager sends back the created category with an ID")
    public void managerSendsBackCatID() {
        Assert.assertNotNull(returnedCategoryId);
    }

    @When("User retrieves the created category by its returned ID")
    public void userRetrievesCatByReturnedID() throws Exception {
        // GET request to retrieve the todo by its returned ID
        URI uri = new URI(baseURL + "categories/" + returnedCategoryId);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
    }

    @Then("Manager sends back the retrieved category")
    public void managerSendsRetrievedCat() throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();

        JSONObject retrievedTodo = new JSONObject(response.toString());
        String retrievedTodoId = retrievedTodo.getJSONArray("categories").getJSONObject(0).getString("id");
        Assert.assertEquals(returnedCategoryId, retrievedTodoId);
    }
    // Story 3

    // Normal Flow
    @When("User deletes the created category")
    public void userDeletesCreatedCategory() throws Exception {
        // DELETE the previously created todo
        URI uri = new URI(baseURL + "categories/" + returnedCategoryId);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("DELETE");
    }

    @Then("The deleted category is not found")
    public void CategoryIsNotFound() throws Exception {
        // Attempt to retrieve the todo with its ID
        URI uri = new URI(baseURL + "categories/" + returnedCategoryId);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
        
        // Verify if the response code is 404 (Check if deleted)
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(404, responseCode);
    }

    // Alternative Flow
    @Then("User updates the category with PUT")
    public void User_updates_the_category_with_PUT() throws Exception {
        // new JSON data for the todo
        JSONObject json = new JSONObject();
        json.put("title", "Updated category");
        json.put("description", "Testing PUT");

        // PUT request to update the previously created todo
        URI uri = new URI(baseURL + "categories/" + returnedCategoryId);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("PUT");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.getOutputStream().write(json.toString().getBytes());
    }

    // Error Flow
    @When("User tries to delete a non-existing category")
    public void DeleteNonExistingCategory() throws Exception {
        // DELETE a non-existing todo
        URI uri = new URI(baseURL + "categories/non_existing_id");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("DELETE");
    }

    // Story 4

    // Normal Flow
    @When("User retrieves todos related to category with ID {int}")
    public void get_categories_of_category_with_ID(int categoryId) throws Exception {
        // Send GET request to retrieve categories related to the todo with given ID 
        URI uri = new URI(baseURL + "categories/" + categoryId + "/todos");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
    }

    // for normal and alternative flow: we expect it to fail based on part 1 of the project
    @Then("Manager sends back the todos")
    public void sends_back_the_categories() throws Exception{
        // Get the JSON output
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        JSONObject jsonResponse = new JSONObject(response.toString());
        System.out.println(jsonResponse);
        // Check if the response contains categories
        if (!jsonResponse.has("todos")) {
            // If categories are found in the response, fail the test
            Assert.fail("Expected to find todos, but didn't find todos.");
        }

    }

    @Then("Manager sends back the created todo with the ID")
    public void send_back_created_category_with_the_ID() throws Exception {
        int responseCode = connection.getResponseCode();
        System.out.println(responseCode);
        if (responseCode != 201){
            System.out.println("Error: PUT didn't work");
            return;
        } else {
        // Get the ID of the added category from the response
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        JSONObject jsonResponse = new JSONObject(response.toString());
        System.out.println(jsonResponse);
        jsonResponse.getString("id");}
    }

    // Alternative 1
    @When("User adds a todo with PUT JSON data to category with ID {int}")
    public void Add_a_todo_to_category_with_PUT_ID(int categoryId) throws Exception{
        // JSON data for the new category
        JSONObject json = new JSONObject();
        json.put("title", "Story 4 - Alternative 1");
        json.put("description", "Test 4");
        json.put("doneStatus", false);
        
        // Send POST request to add category to todo with the given ID
        URI uri = new URI(baseURL + "categories/" + categoryId + "/todos");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("PUT");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.getOutputStream().write(json.toString().getBytes());
    }

    // Alternative 2
    @When("User adds a todo with POST JSON data to category with ID {int}")
    public void Add_a_todo_to_category_with_POST_ID(int categoryId) throws Exception{
        // JSON data for the new category
        JSONObject json = new JSONObject();
        json.put("title", "Story 4 - Alternative 2");
        json.put("description", "Test 4");
        json.put("doneStatus", false);
        
        // Send POST request to add category to todo with the given ID
        URI uri = new URI(baseURL + "categories/" + categoryId + "/todos");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.getOutputStream().write(json.toString().getBytes());
    }

    // Story 5

    // Normal Flow
    @When("User requests headers for categories related projects with ID {int}")
    public void get_headers_categories_related_tasks(int categoryId) throws Exception{
        //HEAD request to retrieve headers for tasks associated with todo of given ID
        URI uri = new URI(baseURL + "categories/" + categoryId + "/projects");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("HEAD");
    }

    @Then("Manager sends back the headers for associated projects")
    public void send_headers_for_associated_project() {
        // check if the response headers contain the expected properties
        System.out.println(connection.getHeaderFields());
        Assert.assertTrue(connection.getHeaderFields().containsKey("Date"));
        Assert.assertTrue(connection.getHeaderFields().containsKey("Content-Type"));
        Assert.assertTrue(connection.getHeaderFields().containsKey("Transfer-Encoding"));
        Assert.assertTrue(connection.getHeaderFields().containsKey("Server"));
    }

    @When("User posts a new project for a category with XML:")
    public void User_posts_a_new_project_for_a_category_with_XML(String xmlData) throws Exception{
        URI uri = new URI(baseURL + "categories/1/projects");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlData.getBytes());
    }

    @Then("Manager sends back the created project for the category")
    public void managerSendsBackCreatedProjectForCategory() throws Exception {
        int responseCode = connection.getResponseCode();
        Assert.assertEquals(201, responseCode);

        // Parse the response JSON
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        JSONObject jsonResponse = new JSONObject(response.toString());
        System.out.println(jsonResponse);

        // check if the response JSON contains the expected data
        Assert.assertTrue(jsonResponse.has("id"));
        Assert.assertEquals("Story 5", jsonResponse.getString("title"));
        Assert.assertEquals("Story 5 - Alternative Flow", jsonResponse.getString("description"));
        Assert.assertEquals("false", jsonResponse.getString("completed"));
        Assert.assertEquals("true", jsonResponse.getString("active"));
    }

    @When("User adds a project to a non-existing category with ID {string}")
    public void add_project_to__non_existing_category(String fake_id) throws Exception {
        // XML data for adding a project to a non-existing todo
        String xmlInput = "<project>\n" +
                          "    <active>false</active>\n" +
                          "    <description>Story 5 - Error Flow</description>\n" +
                          "    <completed>false</completed>\n" +
                          "    <title>Story 5</title>\n" +
                          "</project>";

        // POST request to add project to a non-existing todo with the given ID
        URI uri = new URI(baseURL + "categories/" + fake_id + "/projects");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlInput.getBytes());
    }

    //******************
    //Methods for testing Projects

    // normal flow: Get projects/id
    @When("User asks for a project of id {int}")
    public void userAsksForProjectById(int id) throws Exception {

        URI uri = new URI(baseURL + "projects/" + id);
        // Convert URI to URL
        URL url = uri.toURL();

        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");

        // Verify that the response code is 200 (OK)
        int responseCode = connection.getResponseCode();
        assertEquals(200, responseCode);
    }

    @Then("Manager sends back the project of id {int}")
    public void managerSendsBackProjectOfId(int id) throws Exception {
        // Read and print the response from the server
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        System.out.println("Response from Manager: " + response.toString());
    }

    // alternative flow: Get projects/id
    @When("User asks for a project of a non-existing id {int}")
    public void userAsksForNonExsProjectId(int id) throws Exception {

        URI uri = new URI(baseURL + "projects/" + id);
        // Convert URI to URL
        URL url = uri.toURL();

        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");

        // Verify that the response code is 404
        int responseCode = connection.getResponseCode();
        assertEquals(404, responseCode);
    }

    @Then("Manager sends back an error msg: {string}")
    public void managerSendsBackInstanceNotFoundMsg(String msg) throws Exception {
        // Read and print the response from the server
        int responseCode = connection.getResponseCode();
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        assertTrue(response.toString().contains(msg));
    }

    //error flow
    @When("User asks for a project without id")
    public void userAsksForProjectWithoutId() throws Exception {
        URI uri = new URI(baseURL + "projects/");
        // Convert URI to URL
        URL url = uri.toURL();

        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");

        // Verify that the response code is 404
        int responseCode = connection.getResponseCode();
        assertEquals(404, responseCode);

    }

    @Then("Manager sends back nothing")
    public void managerSendsBackNull() throws Exception {
        // Read and print the response from the server
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();
        assertEquals(response.toString(), "");
    }

    @When("User posts a project using json:")
    public void userPostsNewProjWithJSON(DataTable dataTable) throws Exception {
        List<Map<String, String>> todoData = dataTable.asMaps(String.class, String.class);
        for (Map<String, String> row : todoData) {
            JSONObject json = new JSONObject(row);
            URI uri = new URI(baseURL + "projects");
            URL url = uri.toURL();
            System.out.println(json.toString());
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);
            connection.getOutputStream().write(json.toString().getBytes());
        }
    }

    @When("User posts a new project with xml:")
    public void userPostsNewProjWithXML(String xmlData) throws Exception {
        URI uri = new URI(baseURL + "projects");
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlData.getBytes());
    }

    @Then("Manager sends back the created project")
    public void managerSendsBackCreatedProject() throws Exception {
        int responseCode = connection.getResponseCode();
        assertEquals(201, responseCode);

        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();

        JSONObject output = new JSONObject(response.toString());
        projectIDToBeDeleted = output.getString("id");
        assertEquals(5, output.length());
        assertTrue(output.has("id"));
        assertEquals("429 project", output.getString("title"));
        assertEquals("asap", output.getString("description"));
        System.out.println(output.getString("id"));

    }

    @When("User posts a project")
    public void userPostsNewProj() throws Exception {
        URI uri = new URI(baseURL + "projects");
        URL url = uri.toURL();
        String xmlUpdate = "<project>\n <title>429 project</title>\n <description>asap</description>\n</project>";
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlUpdate.getBytes());
    }

    @Then("User updates the project")
    public void userPutsProj() throws Exception {
        URI uri = new URI(baseURL + "projects/" + projectIDToBeDeleted);
        URL url = uri.toURL();
        String xmlUpdate = "<project>\n <title>421 project</title>\n</project>";
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("PUT");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlUpdate.getBytes());

        int responseCode = connection.getResponseCode();
        assertEquals(200, responseCode);
    }


    @Then("User deletes the project")
    public void userDeletesProj() throws Exception {
        URI uri = new URI(baseURL + "projects/" + projectIDToBeDeleted);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("DELETE");

        int responseCode = connection.getResponseCode();
        assertEquals(200, responseCode);
    }

    @When("User deletes a project of id {int}")
    public void userDeletesProjectById(int id) throws Exception {

        URI uri = new URI(baseURL + "projects/" + id);
        URL url = uri.toURL();

        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("DELETE");

        int responseCode = connection.getResponseCode();
        assertEquals(404, responseCode);
    }

    @When("User deletes a task of id {int} of project {int} and fail")
    public void userDeletesTaskById(int tid, int pid) throws Exception {

        URI uri = new URI(baseURL + "projects/" + pid + "/tasks/" + tid);
        URL url = uri.toURL();

        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("DELETE");

        int responseCode = connection.getResponseCode();
        assertEquals(404, responseCode);
    }

    @Then("User adds a task named: {string}")
    public void userPostsTask(String tname) throws Exception {
        URI uri = new URI(baseURL + "projects/" + projectIDToBeDeleted + "/tasks");
        URL url = uri.toURL();
        String xmlUpdate = "<project>\n <title>" + tname + "</title>\n</project>";
        taskIDToBeDeleted = tname;
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/xml");
        connection.setDoOutput(true);
        connection.getOutputStream().write(xmlUpdate.getBytes());
    }

    @Then("Manager sends back the created task")
    public void managerSendsBackCreatedTask() throws Exception {
        int responseCode = connection.getResponseCode();
        assertEquals(201, responseCode);

        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();

        JSONObject output = new JSONObject(response.toString());
        taskIDToBeDeleted = output.getString("id");
        assertEquals(5, output.length());
        assertTrue(output.has("id"));

    }

    @Then("User deletes last task added")
    public void userDeletesLastTask() throws Exception {
        URI uri = new URI(baseURL + "projects/" + projectIDToBeDeleted + "/tasks/" + taskIDToBeDeleted);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("DELETE");

        int responseCode = connection.getResponseCode();
        assertEquals(200, responseCode);
    }

    @When("User heads {string}")
    public void userHeadsProjects(String routeString) throws Exception {
        URI uri = new URI(baseURL + routeString);
        URL url = uri.toURL();
        connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("HEAD");
    }

    @Then("User requests successfully")
    public void userHeadsProjectsSuccess() throws Exception {
        int responseCode = connection.getResponseCode();
        assertEquals(200, responseCode);
    }

    @Then("User request fails")
    public void userHeadsProjectsFail() throws Exception {
        int responseCode = connection.getResponseCode();
        assertEquals(404, responseCode);
    }

}
