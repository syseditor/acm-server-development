import requests, dotenv, os, jwt

def compress_object(argument) -> list:
    if isinstance(argument, str): return list(argument)
    else:
        secrets_list = list()

        for inside_object in argument:
            if isinstance(inside_object, dict):
                for key,value in inside_object.items():
                    secrets_list.append(f'{key} : {value}')
            elif isinstance(inside_object, list):
                extension = compress_object(inside_object)
                secrets_list.extend(extension)
            else:  # it's anything else
                secrets_list.append(f'{inside_object}')
        return secrets_list

def main() -> None:
    dotenv.load_dotenv()
    username = input('Enter the Keycloak user\'s name: ')
    password = input('Enter its password: ')

    location = 'http://localhost:8080/realms/ACM/protocol/openid-connect/token'
    payload = {
        'client_id' : 'ACM',
        'client_secret' : os.getenv("CLIENT_SECRET"),
        'grant_type' : 'password',
        'username' : username,
        'password' : password
    }

    response = requests.post(url=location, data=payload).json()

    try:
        token = response["access_token"]
    except KeyError:
        error_code = response["error"]
        error_descr = response["error_description"]
        print(f'\nAn error occurred, titled "{error_code}"\nDescription: {error_descr}')
    else: #all went okay
        public_key = f'-----BEGIN PUBLIC KEY-----\n{os.getenv("PUBLIC_KEY")}\n-----END PUBLIC KEY-----'
        options = {'verify_exp': False,
                   'verify_aud': False}
        json = jwt.decode(
            jwt=token,
            key=public_key,
            options=options,
            algorithms=['RS256']
        )
        try:
            secrets = json['group_secrets']
        except KeyError:
            print(f'No secrets were found for user {username}')
        else:
            secrets_compressed = compress_object(secrets)
            secrets_string = ', '.join(secrets_compressed)
            print(f'Secrets: {secrets_string}')

if __name__ == "__main__":
    main()