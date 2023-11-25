from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db_func import insert_into_table, print_mails_table
from src.db_models import Base
from src.gmail_func import gmail_authenticate, search_messages, generate_data_from_msgs

if __name__ == '__main__':
    engine = create_engine("sqlite://", echo=True)
    # engine = create_engine("sqlite:////Users/yileicao/Documents/email-extraction/email.db", echo=True)
    Base.metadata.create_all(engine)

    service = gmail_authenticate()

    # get emails that match the query you specify
    results = search_messages(service, "RUTILEA")
    print(f"Found {len(results)} results.")
    # for each email matched, read it (output plain/text to console & save HTML and attachments)
    data = generate_data_from_msgs(service, results)
    with engine.connect() as conn:
        insert_into_table(conn, data)
        print_mails_table(conn)
