import logging

def save_model(session, model):
        # Save on database
        try:
            session.add(model)
        except Exception:
            logging.error(Exception)