# Keycloak: Collecting user attributes and embedding them in a JWT
Our task was to research if it's possible for simple users to login to Keycloak
and access their group attributes. Here's what we found out:

- It's **NOT** possible to create such a role that permits the user to see its attributes.
- Even if you set up the permissions, going to http://localhost:8080/realms/{realm_name}/account and logging in, visible will
only be the basic user information (username, first and last name, email) and not its attributes.

Our next thought was to finally create a **Java SPI Keycloak plugin** that will serve as a
custom protocol mapper which will map our users' attributes. **This is NOT necessary to**
**make**, for a single POST HTTP request can solve our hands.\
(The following solution was tested using [Postman](https://www.postman.com/))

***Steps in Keycloak:***
1) Create a group (and/or subgroups)
2) Create an attribute (Attributes tab)
3) Create a new client. Name it whatever you want (f.e. attr_mapper_client)
4) Go to Client Scopes -> {client_name}_dedicated -> Mappers
5) Add a new mapper **by configuration**
6) Select the **User Attribute** option
7) Set a name, the attribute key (whatever you set for key in the Attributes tab) and a token claim name
8) Save it
9) Go back to your client and select the **Roles** tab
10) Create a simple role
11) Add the role to your desired user(s)
12) Before logging out, go back to your Client -> Credentials
13) Make sure the option **Client Id and Secret** is selected in Client Authenticator
14) Copy the Client Secret (be careful with that key!!!)

***After all that, open Postman and...:***
1) Add a new request
2) Select **POST** for the request type
3) Enter http://localhost:8080/realms/{realm_name}/protocol/openid-connect/token in the url field
4) Go to Body -> x-www-form-urlencoded and enter the following key-value parameters:

| Key | Value |
| --- | --- |
| `client_id` | {your_client_name} |
| `client_secret` | {the_secret_you_copied} |
| `grant_type` | password |
| `username` | {your_username} |
| `password` | {your_password} |
5) Press **Send**
6) Get the value of the "access_token" key (it's a JWT (JSON Web Token))
7) Go to https://jwt.io and place it under the **Encoded Value**
8) In the **Decoded Payload** search for your key-value attribute

***Otherwise, you can execute this curl command:***
```
curl --location http://localhost:8080/realms/ACM/protocol/openid-connect/token -d "client_id=ACM&client_secret=a5Ir9gDTBvCw8s7TRxkJVhqN15uObokG&grant_type=password&username=user7&password=password"
```
The parameters vary depending on the realm, client and user. The result will be the same as the Postman example.

After that, we just need to create a handler (preferably in Javascript, however Python and Java are options too) which will filter the user information and will search for its attributes.\
**Structure Idea**: We could name every key in attributes "group-attributes" and their value will be a JSON object (nested key-value elements) for better information handling and filtering.

Reference for that at https://stackoverflow.com/questions/60767085/keycloak-map-multiple-user-attributes
