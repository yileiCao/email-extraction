from datetime import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Integer, DateTime
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass

##TODO
## relationship


class User(Base):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    email_address = mapped_column(String(50), nullable=False)
    name = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email_address={self.email_address!r}, " \
               f"name={self.name!r})"


class Mail(Base):
    __tablename__ = "mails"
    id = mapped_column(Integer, primary_key=True)
    sender = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    recipient = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    time = mapped_column(DateTime, nullable=False)
    mail_server_id = mapped_column(String(50), nullable=False)
    keyword = mapped_column(String(200), nullable=False)

    # user: Mapped["User"] = relationship(back_populates="sender")

    def __repr__(self) -> str:
        return f"Emails(id={self.id!r}, sender={self.sender!r}, recipient={self.recipient!r}, " \
               f"time={self.time!r}, server_id={self.mail_server_id!r}, keyword={self.keyword!r})"


if __name__ == '__main__':

    from sqlalchemy import create_engine

    engine = create_engine("sqlite://", echo=True)
    # engine = create_engine("sqlite:////Users/yileicao/Documents/email-extraction/email.db", echo=True)
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import Session
    with Session(engine) as session:
        spongebob = User(
            email_address="spongebob@sqlalchemy.org",
        )
        sandy = User(
            email_address="sandy@sqlalchemy.org",
        )
        mail = Mail(
            sender='spongebob',
            recipient=1,
            time=datetime.now(),
            mail_server_id="aa",
            keyword="aa"
        )
        session.add_all([spongebob, sandy, mail])
        session.commit()

    from sqlalchemy import select
    session = Session(engine)
    stmt = select(User).where(User.email_address.in_(["spongebob@sqlalchemy.org", "sandy@sqlalchemy.org"]))
    for user in session.scalars(stmt):
        print(user)
    stmt = select(Mail)
    for mail in session.scalars(stmt):
        print(mail)