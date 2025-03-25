from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, account_routes


app = FastAPI(title="OAuth-based API Integration with QuickBooks Online", 
              description="API Integration with QuickBooks Online", 
              version="0.0.1")

app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"], 
                   allow_credentials=True, 
                   allow_methods=["*"], 
                   allow_headers=["*"])

app.include_router(auth_routes.router)
app.include_router(account_routes.router)