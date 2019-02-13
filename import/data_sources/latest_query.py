def get_latest_query(session, raw_model, model):
    """
    Returns raw model database query according to the last
    entry in the clean model. Only returns the query without
    fetching the data to allow further statements to be added
    like 'offset' and 'limit'
    """
    model = model if isinstance(model, str) else model.__table__.name

    latest = session.execute(
        f'SELECT scraped_at FROM {model} ORDER bY scraped_at DESC LIMIT 1;'
    ).first()

    if latest:
        # update since api
        return (
            session.query(raw_model)
            .order_by(raw_model.scraped_at.desc())
            .filter(raw_model.scraped_at > latest.scraped_at)
        )
    # empty api.
    return session.query(raw_model)
