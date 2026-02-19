from fastapi import FastAPI

from src.routers import team_stats, player_stats, games

app = FastAPI()

app.include_router(team_stats.router)
app.include_router(player_stats.router)
app.include_router(games.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
