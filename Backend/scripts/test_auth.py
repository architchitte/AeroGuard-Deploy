from app import create_app

app = create_app()
app.testing = True
client = app.test_client()

# Login
resp = client.post('/api/v1/users/auth/login', json={'username': 'alice'})
print('login status:', resp.status_code)
print('login json:', resp.get_json())

token = resp.get_json().get('access_token') if resp.status_code == 200 else None
headers = {'Authorization': f'Bearer {token}'} if token else {}

# Call protected endpoint
resp2 = client.get('/api/v1/users/1/preferences', headers=headers)
print('prefs status:', resp2.status_code)
print('prefs json:', resp2.get_json())
