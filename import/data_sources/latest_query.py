def get_latest_query(session, raw_model, model):
    """
    Returns raw model database query according to the last
    entry in the clean model. Only returns the query without
    fetching the data to allow further statements to be added
    like 'offset' and 'limit'
    """
    latest = (
        session.query(model)
        .order_by(model.scraped_at.desc())
        .first()
    )
    if latest:
        # update since api
        return (
            session.query(raw_model)
            .order_by(raw_model.scraped_at.desc())
            .filter(raw_model.scraped_at > latest.scraped_at)
        )
    # empty api.
    return session.query(raw_model)
