from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import uvicorn
from fastapi.responses import HTMLResponse

# Initialize FastAPI
app = FastAPI()

# SQLite database setup
DATABASE_URL = "sqlite:///./traces.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the database model
class Trace(Base):
    __tablename__ = "traces"
    id = Column(Integer, primary_key=True, index=True)
    asistente = Column(String, index=True)
    usuario = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    tokens_in = Column(Integer)
    tokens_out = Column(Integer)

# Pydantic model for input data validation
class TraceCreate(BaseModel):
    asistente: str
    usuario: str
    date: datetime
    tokens_in: int
    tokens_out: int
    
# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to add a trace
@app.post("/add_trace")
def add_trace(trace: TraceCreate, db: Session = Depends(get_db)):
    db_trace = Trace(
        asistente=trace.asistente,
        usuario=trace.usuario,
        date=trace.date,
        tokens_in=trace.tokens_in,
        tokens_out=trace.tokens_out
    )
    db.add(db_trace)
    db.commit()
    db.refresh(db_trace)
    return {"message": "Trace added successfully", "trace_id": db_trace.id}

# Endpoint to view all traces
@app.get("/view_traces")
def view_traces(db: Session = Depends(get_db)):
    traces = db.query(Trace).all()
    return traces

# HTML template to display traces
@app.get("/")
def read_root(db: Session = Depends(get_db)):
    traces = db.query(Trace).all()
    html_content = """
    <html>
        <head>
            <title>LLM Application Traces</title>
        </head>
        <body>
            <h1>LLM Application Traces</h1>
            <table border="1">
                <tr>
                    <th>ID</th>
                    <th>Asistente</th>
                    <th>Usuario</th>
                    <th>Date</th>
                    <th>Tokens In</th>
                    <th>Tokens Out</th>
                </tr>
    """
    for trace in traces:
        html_content += f"""
                <tr>
                    <td>{trace.id}</td>
                    <td>{trace.asistente}</td>
                    <td>{trace.usuario}</td>
                    <td>{trace.date}</td>
                    <td>{trace.tokens_in}</td>
                    <td>{trace.tokens_out}</td>
                </tr>
        """
    html_content += """
            </table>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Run the server when the script is executed
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
