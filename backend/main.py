from fastapi import FastAPI

app = FastAPI(title="KnowledgeHub AI知识库接口")

@app.get("/")
def hello():
    return {"msg":"知识库服务运行成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)
