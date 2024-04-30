class Pagination:
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        # Calculates the total pages
        return max(0, self.total_count - 1) // self.per_page + 1

    @property
    def has_prev(self):
        # Checks if there's a previous page
        return self.page > 1

    @property
    def has_next(self):
        # Checks if there's a next page
        return self.page < self.pages

    @property
    def next_num(self):
        # Returns the number of the next page
        return self.page + 1 if self.has_next else None

    @property
    def prev_num(self):
        # Returns the number of the previous page
        return self.page - 1 if self.has_prev else None

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        # Iterates over the range of page numbers for pagination
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num