from fastapi import Depends, FastAPI, HTTPException, Request
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

models.Base.metadata.create_all(bind=engine)


conf = ConnectionConfig(
    MAIL_USERNAME="neerajtanwar17@gmail.com",
    MAIL_PASSWORD="ddwz volb",
    MAIL_FROM="neerajtanwar17@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


api_keys = ["xeJJzhaj1mQ-ksTB_nF_iH0z5YdG50yQtwQCzbcHuKA"]


def api_key_auth(request: Request):
    api_key = request.headers.get("x-api-key")
    if api_key not in api_keys:
        raise HTTPException(status_code=401, detail="API key is invalid")


@app.post("/email")
async def send_mail(email: schemas.EmailSchema) -> JSONResponse:
    try:
        message = MessageSchema(
            recipients=email.dict().get("email"),
            subject="Test email",
            body="This is a test email.",
            # attachments=["attachment.pdf"],
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        return JSONResponse(status_code=200, content={"message": "email has been sent"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.put("/users/", response_model=schemas.User)
def update_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return crud.update_user(db=db, user=user)


@app.get("/users/", dependencies=[Depends(api_key_auth)], response_model=list[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {'msg': 'User deleted successfully.'}


@app.get("/transaction/{wallet_id}", response_model=list[schemas.TransactionCreate])
def get_transactions(wallet_id: int, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet.transactions


@app.post("/transaction/{wallet_id}", response_model=schemas.TransactionBase)
def create_transaction(wallet_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, wallet_id=wallet_id, transaction=transaction)


@app.put("/transaction/{transaction_id}", response_model=schemas.TransactionBase)
def update_transaction(transaction_id: int, transaction: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    return crud.update_transaction(db=db, transaction_id=transaction_id, transaction=transaction)


@app.delete("/transaction/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return crud.delete_transaction(db=db, db_transaction=db_transaction)


@app.get("/wallet/{user_id}", response_model=schemas.WalletBase)
def get_wallet(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found for this user")
    return user.wallet
