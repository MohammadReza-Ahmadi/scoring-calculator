from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# from app.core.data.import_rules_data import import_rules
from app.routes import views

app = FastAPI()

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(views.router)

# dependency injection #
# class Service:
#     db: Database
#
#     def __init__(self) -> None:
#         # super().__init__()
#         # establish db connection by mongoClient
#         client = MongoClient(host='127.0.0.1', port=8000)
#         self.db = client.get_database('score-engine')
#
#
# class Container(containers.DeclarativeContainer):
#     service = providers.Factory(Service)
