from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # للسماح بالطلبات من أي موقع

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'Roblox Profile API is running!'
    })

@app.route('/api/user/<username>', methods=['GET'])
def get_user(username):
    try:
        # البحث عن المستخدم
        search_url = 'https://users.roblox.com/v1/usernames/users'
        search_response = requests.post(
            search_url,
            json={
                'usernames': [username],
                'excludeBannedUsers': False
            },
            timeout=10
        )
        
        if not search_response.ok:
            return jsonify({'error': 'فشل البحث عن المستخدم'}), 400
        
        search_data = search_response.json()
        
        if not search_data.get('data') or len(search_data['data']) == 0:
            return jsonify({'error': 'لم يتم العثور على المستخدم'}), 404
        
        user_id = search_data['data'][0]['id']
        
        # الحصول على معلومات المستخدم
        user_url = f'https://users.roblox.com/v1/users/{user_id}'
        user_response = requests.get(user_url, timeout=10)
        
        if not user_response.ok:
            return jsonify({'error': 'فشل الحصول على معلومات المستخدم'}), 400
        
        user_data = user_response.json()
        
        # الحصول على صورة الأفاتار
        avatar_url = f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png'
        avatar_response = requests.get(avatar_url, timeout=10)
        
        avatar_image = ''
        if avatar_response.ok:
            avatar_data = avatar_response.json()
            if avatar_data.get('data') and len(avatar_data['data']) > 0:
                avatar_image = avatar_data['data'][0]['imageUrl']
        
        # إذا فشلت صورة API، استخدم الرابط المباشر
        if not avatar_image:
            avatar_image = f'https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png'
        
        return jsonify({
            'success': True,
            'data': {
                'id': user_data['id'],
                'name': user_data['name'],
                'displayName': user_data['displayName'],
                'description': user_data.get('description', ''),
                'created': user_data['created'],
                'isBanned': user_data.get('isBanned', False),
                'avatar': avatar_image
            }
        })
        
    except requests.Timeout:
        return jsonify({'error': 'انتهت مهلة الاتصال'}), 504
    except Exception as e:
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
