#!/usr/bin/env python3
from app import create_app

def main():
    app = create_app()
    with app.test_client() as client:
        resp = client.get('/charge/dashboard')
        print('Status:', resp.status_code)
        print('Length:', len(resp.get_data(as_text=True)))

if __name__ == '__main__':
    main()

