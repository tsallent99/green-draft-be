from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import users, tournaments, players, leagues, entries, teams, leaderboard, payments

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Fantasy Golf API",
    description="API for Fantasy Golf application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api")
app.include_router(tournaments.router, prefix="/api")
app.include_router(players.router, prefix="/api")
app.include_router(leagues.router, prefix="/api")
app.include_router(entries.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")
app.include_router(payments.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Fantasy Golf API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
