from google import genai
import base64
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)

def is_file_valid(filename):
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_image(file):
    image_data = file.read()

    encoded_image = base64.b64encode(image_data).decode("utf-8")

    return encoded_image

def handle_ai_connection(api_key, prompt):
    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text, 200
    except Exception as e:
        return str(e), 500

def parse_response(response):
    responses = []
    parts = [line.strip() for line in response.split("\n") if line.strip()]

    for part in parts:
        split_part = part.split(":", 1)
        
        if split_part[0] and split_part[1]:
            responses.append(part.split(":", 1))
    
    return responses