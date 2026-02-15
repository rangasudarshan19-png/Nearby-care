import google.generativeai as genai

# Configure with API key
genai.configure(api_key='AIzaSyChPE050NNk3jakECiS-MK4PxrBzZJXcHg')

# List all available models
print("Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model: {model.name}")
        print(f"  Supported methods: {model.supported_generation_methods}")
        print()
