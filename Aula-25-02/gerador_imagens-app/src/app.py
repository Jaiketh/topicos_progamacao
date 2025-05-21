import requests
import base64

# URL do Worker AI da Cloudflare
API_URL = "https://api.cloudflare.com/client/v4/accounts/8b6dace8399d7b8b5caf845ee978b1a04/ai/run/@cf/black-forest-labs/flux-1-schnell"

# Substitua pela sua chave de API (se necessário)
HEADERS = {
    "Authorization": "Bearer cHeOLD2NwO2ov3FILyTzcg76I5Xvxscp5WGJ-F8W",
    "Content-Type": "application/json"
}

# Prompt para gerar a imagem
DATA = {
    "prompt": "faça uma paisagem onde todas as coisas são feitas de chocolate",
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 30
}

# Faz a requisição para gerar a imagem
response = requests.post(API_URL, json=DATA, headers=HEADERS)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    result = response.json()
    
    image_base64 = result["result"]["image"]
    
    if image_base64:
        # Converte Base64 para imagem
        try:
            with open("output.png", "wb") as img_file:
                img_file.write(base64.b64decode(image_base64))
            print("Imagem salva como output.png")
        except Exception as e:
            print(f"Erro ao decodificar a imagem: {e}")
else:
    print(f"Erro: {response.status_code}, {response.text}")