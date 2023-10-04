from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email, password=user.password)
    wallet = models.Wallet()
    db_user.wallet = wallet
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.name = user.name
    db_user.email = user.email
    db_user.password = user.password
    db_user.type = user.type
    db.commit()
    db.refresh(db_user)
    return db_user


def create_transaction(db: Session, wallet_id: int, transaction: schemas.TransactionBase):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    db_transaction = models.Transaction(
        amount=transaction.amount,
        type=transaction.type,
        wallet_id=wallet_id
    )
    db.add(db_transaction)

    wallet.amount = wallet.amount+transaction.amount if transaction.type == 'credit' else wallet.amount-transaction.amount

    db.commit()
    db.refresh(db_transaction)
    db.refresh(wallet)
    return db_transaction


def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionBase):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    wallet = db_transaction.wallet
    wallet.amount -= db_transaction.amount
    wallet.amount += transaction.amount
    db_transaction.amount = transaction.amount

    db.commit()
    db.refresh(db_transaction)
    db.refresh(wallet)
    return db_transaction


def delete_transaction(db: Session, db_transaction: object):
    wallet = db_transaction.wallet
    wallet.amount -= db_transaction.amount
    db.delete(db_transaction)
    db.commit()
    db.refresh(wallet)
    return {'msg': 'transaction deleted successfully.'}
