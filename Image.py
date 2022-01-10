class Image:
    def __init__(self, description, filename, distance=1, service_id=None):
        self.description = description
        self.filename = filename
        self.distance = distance
        self.service_id = service_id
