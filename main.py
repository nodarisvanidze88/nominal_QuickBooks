from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="API for the project", 
              description="This is a very fancy project, with auto docs for the API and everything", 
              version="0.0.1")

app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"], 
                   allow_credentials=True, 
                   allow_methods=["*"], 
                   allow_headers=["*"])