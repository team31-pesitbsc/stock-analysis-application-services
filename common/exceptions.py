class StockUpdateException(Exception):
    def __init__(self, latest_date, update_date):
        self.latest_date = latest_date
        self.update_date = update_date
        # TODO - form better exception message
        super().__init__(str(latest_date)+":"+str(update_date))
